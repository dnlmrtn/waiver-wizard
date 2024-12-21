# Configuration
DOMAIN="yourdomain.com"  # Replace with your domain
EMAIL="your@email.com"   # Replace with your email
NGINX_CONF="/etc/nginx/sites-available/default"  # Adjust path if needed

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Install required packages if not present
if ! command_exists certbot; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
systemctl stop nginx

# Backup existing certificates if they exist
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
if [ -d "$CERT_PATH" ]; then
    echo "Backing up existing certificates..."
    BACKUP_DIR="/root/ssl_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$CERT_PATH" "$BACKUP_DIR"
fi

# Generate new certificate
echo "Generating new SSL certificate for $DOMAIN..."
certbot --nginx \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect \
    --keep-until-expiring \
    --expand

# Check if certificate generation was successful
if [ $? -eq 0 ]; then
    echo "Certificate generated successfully!"
    
    # Verify Nginx config
    nginx -t
    if [ $? -eq 0 ]; then
        # Restart Nginx
        systemctl start nginx
        echo "Nginx restarted successfully!"
        
        # Test SSL configuration
        curl -I "https://$DOMAIN"
        
        # Set up auto-renewal (if not already set)
        if ! crontab -l | grep -q certbot; then
            (crontab -l 2>/dev/null; echo "0 */12 * * * /usr/bin/certbot renew --quiet") | crontab -
            echo "Auto-renewal cron job added"
        fi
    else
        echo "Nginx configuration test failed. Please check your configuration."
        # Restore from backup if it exists
        if [ -d "$BACKUP_DIR" ]; then
            cp -r "$BACKUP_DIR"/* "$CERT_PATH"
            echo "Restored previous certificates from backup"
        fi
        systemctl start nginx
    fi
else
    echo "Certificate generation failed!"
    if [ -d "$BACKUP_DIR" ]; then
        cp -r "$BACKUP_DIR"/* "$CERT_PATH"
        echo "Restored previous certificates from backup"
    fi
    systemctl start nginx
fi

# Print certificate information
if [ -f "$CERT_PATH/fullchain.pem" ]; then
    echo "Certificate details:"
    openssl x509 -in "$CERT_PATH/fullchain.pem" -text -noout | grep -A 2 "Validity"
fi

echo "Script completed!"
