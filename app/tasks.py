import time

from celery import shared_task


@shared_task()
def call_background_task(message):
    time.sleep(10)
    print("Background task 1!")
    print(message)
