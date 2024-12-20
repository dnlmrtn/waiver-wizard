# Database Setup

If you need to recreate the database from scratch:

### Ensure your `.env.dev` file has the necessary database variables:
  ```
  env
  DB_USER=postgres
  DB_NAME=app
```
### Start the database container:
```bash
docker-compose up -d db
```

### Run the database initialization script: 
```bash
docker exec <container-name> bash /scripts/init_database.sh
```

### Verify the database was created:
```bash
docker exec -it waiver-wizard_db_1 psql -U postgres
```
