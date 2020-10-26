web: gunicorn -b 0.0.0.0:8000 -w 4 manage:app
worker: python -u manage.py run_worker
