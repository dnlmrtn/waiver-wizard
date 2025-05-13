sudo docker compose -f docker-compose.prod.yaml build db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml up -d db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml exec app python manage.py migrate_schemas

sudo docker compose -f docker-compose.prod.yaml exec app python manage.py collectstatic 

sudo docker system prune -a

echo "Deployment Complete"
