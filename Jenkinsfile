FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt


RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary --timeout 600 --retries 10 -r requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=RoadData.settings_prod

CMD ["/bin/sh", "-c", "\
python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
exec gunicorn RoadData.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --access-logfile - \
  --error-logfile - \
"]
