# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 3  
loglevel = 'info'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'