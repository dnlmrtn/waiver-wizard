git checkout master
git pull origin master

docker compose -f docker-compose.prod.yaml build db redis celery celery-beat app nginx
docker compose -f docker-compose.prod.yaml restart db redis celery celery-beat app nginx
docker-compose -f $1 exec app python rcs/manage.py migrate_schemas

docker system prune

echo "Deployment Complete"
