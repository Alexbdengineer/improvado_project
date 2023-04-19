#celery_app.py
from celery import Celery
from celery.schedules import crontab
from weather_update import _update_weather_data

app = Celery('tasks', broker='pyamqp://guest@localhost//')

app.conf.update({
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
})

@app.task
def update_weather_data():
    _update_weather_data()

app.conf.beat_schedule = {
    'update_weather_data': {
        'task': 'celery_app.update_weather_data',
        'schedule': crontab(minute='*/10'),
    },
}
