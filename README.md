# Waiver Wizard: Track Fantasy Waivers in Advance

# Local Testing Setup

## Install Requirements
```bash
bash ./scripts/install_requirements.txt
```

## Database Setup

Ensure your `.env.dev` file has the necessary database variables.

Start the database container:
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


