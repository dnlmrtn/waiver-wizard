git checkout main
git pull origin main

sudo docker compose -f docker-compose.prod.yaml build db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml restart db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml exec app python rcs/manage.py migrate_schemas

sudo docker system prune

echo "Deployment Complete"
