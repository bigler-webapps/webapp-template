docker-compose build
docker-compose up -d



docker compose exec template_app python manage.py makemigrations
docker compose exec template_app python manage.py migrate

