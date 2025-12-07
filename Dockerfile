FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary --timeout 600 --retries 10 -r requirements.txt && \
    mkdir -p /var/log/gunicorn && chmod -R 755 /var/log/gunicorn

COPY . /app

ENV DJANGO_SETTINGS_MODULE=RoadData.settings_prod

HEALTHCHECK --interval=10s --timeout=10s --retries=10 \
  CMD curl -f http://127.0.0.1:8000/api/transports/ || exit 1

CMD sh -c "python manage.py migrate && \
           python manage.py collectstatic --noinput && \
           gunicorn RoadData.wsgi:application --bind 0.0.0.0:8000 --workers 3"
