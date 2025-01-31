#!/bin/bash

pip install uvicorn
pip install --upgrade uvicorn

python manage.py makemigrations
python manage.py migrate

# collect static files
python manage.py collectstatic --noinput

uvicorn backend.asgi:application --host 0.0.0.0 --port 8000 --reload
