import os
from celery import Celery

# Define as configurações padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alugAE.settings')

app = Celery('alugAE')

# Lê as configurações do Django para o Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente as tasks em todos os apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')