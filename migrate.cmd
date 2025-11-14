docker-compose build
docker-compose up -d



docker-compose exec project_template_app python manage.py makemigrations
docker-compose exec project_template_app python manage.py migrate

docker cp django_backend_project_template_app:/app/backend/users/migrations/. backend/users/migrations/

docker-compose down