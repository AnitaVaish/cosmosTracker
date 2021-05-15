from celery import Celery
import time

from config import application
from utils.constant_variables import RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_IP, COSMOS_TRACKER, RABBITMQ_VHOST
from utils.messages import UpdateMessage
from utils.tasks import Task
from utils.reports import Report

from config import printer


def make_celery(app):
    """
    A method to initialize the celery (task queue - broker) worker.
    It is used for simple background tasks.
    :param app: the initialized in the config flask app (application)
    :return: configured celery worker
    """
    celery = Celery(
    application.import_name,
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_IP}/{RABBITMQ_VHOST}',
)

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_worker = make_celery(application)

@celery_worker.task(name='process_task')
def process_task(user):
    """
    This worker is responsible for creating entries on the platform
    :param user: a user object
    :param entry: contains the information about the entry which should be created on the platform
    :param status: contains for which task is the entry
    """
    task = Task(user)
    task.create()

    report = Report(user, COSMOS_TRACKER)
    report.send()


@celery_worker.task(name='process_update_message')
def process_update_message(user, text, task_id):
    """
    This worker is responsible for updating the already created tasks on the platform
    :param user: a user object
    :param text: the updated text
    :param task_id: the task_id
    """
    edited_message = UpdateMessage(user, text, task_id)
    edited_message.update_message()
