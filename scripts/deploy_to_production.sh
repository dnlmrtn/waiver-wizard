git checkout main
git pull origin main

sudo docker compose -f docker-compose.prod.yaml build db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml up -d db redis celery celery-beat app nginx
sudo docker compose -f docker-compose.prod.yaml exec app python rcs/manage.py migrate_schemas

sudo docker compose -f docker-compose.prod.yaml exec app python rcs/manage.py collectstatic 

sudo docker system prune -a

echo "Deployment Complete"
