# Waiver Wizard: Track Fantasy Waivers in Advance

## Local Testing Setup
### Setup ENV Variables
Create .env file from example:
```bash
cp .env.example .env.dev
```

Replace with the following example info:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecretpassword

DB_HOST=db
DB_NAME=app
DB_USER=postgres
DB_PASS=supersecretpassword
DB_PORT=5432

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=example@exmaple.com
DJANGO_SUPERUSER_PASSWORD=admin

DJANGO_SETTINGS_MODULE=app.settings
LEAGUE_ID=454.l.43895

ALLOWED_HOSTS='["localhost"]'

CORS_ORIGIN_WHITELIST=http://localhost:3000

DEBUG=True
SECRET_KEY=django-insecure-74ek#$su&p=oz$_al^9pz7q#olw4_vo6s70$jgwb_@cl_=hw2m
SITE_URL='localhost'
```

### Install Requirements
```bash
bash ./scripts/install_requirements.sh
```

### Database Setup

Ensure your `.env.dev` file has the necessary variables, then start the database container:
```bash
docker-compose up -d db
```

Run the database initialization script: 
```bash
docker exec waiver-wizard-db-1 bash /scripts/init_database.sh
```

Verify the database was created:
```bash
docker exec -it waiver-wizard-db-1 psql -U postgres
```
To exit:
```bash
\q
```

## Production Deployment

Create .env file from example:
```bash
cp .env.example .env.prod
```

### Install Requirements
```bash
bash ./scripts/install_requirements.sh
```

### Database Setup

Ensure your `.env.prod` file has the necessary variables, then start the database container:
```bash
docker-compose up -d db
```

Run the database initialization script: 
```bash
docker exec waiver-wizard-db-1 bash /scripts/init_database.sh
```
Run production deployment script:
```bash
bash ./scripts/deploy_to_production.sh
```
