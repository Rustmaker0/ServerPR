FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --timeout 300 --retries 20 -r requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=RoadData.settings_prod

CMD sh -c "python manage.py migrate && \
           python manage.py collectstatic --noinput && \
           gunicorn RoadData.wsgi:application --bind 0.0.0.0:8000 --workers 3"
