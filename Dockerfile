FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
s
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --prefer-binary \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=RoadData.settings_prod

HEALTHCHECK --interval=10s --timeout=10s --retries=10 \
  CMD curl -f http://127.0.0.1:8000/api/transports/ || exit 1

CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn RoadData.wsgi:application --bind 0.0.0.0:8000 --workers 3"
