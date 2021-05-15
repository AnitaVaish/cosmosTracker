import requests
from requests.exceptions import ChunkedEncodingError

from utils.platform import PlaftormConnector
from utils.time import datetime

from utils.constant_variables import COMPLETED, CURRENT, BLOCKERS, TRUE_TASK, FALSE_TASK


class Task:
    """
    This class is responsible for created entries, for the specific task
    """

    def __init__(self, user):
        self.user = user

    def create(self):
        """
        This method is responsible for creating an entry in the platform

        :param status: status of the task (COMPLETED, CURRENT or BLOCKERS)
        :param entry: an object containing information about the entry
        :return: response, if the entry was entered successfully or not
        """
        tasks = self.user['tasks']

        today_date = datetime.now()
        today_date = today_date.strftime("%Y-%m-%d %H:%M:%S")

        url = 'http://52.47.206.24:4000/api/records/cosmos_tracker/'

        data_object = []

        for task, values in tasks.items():
            if task == COMPLETED:
                data_object.append({
                    'data': {
                        'datetime': today_date,
                        'user': self.user['username'].capitalize(),
                        'task': values['completed_task'],
                        'task_id': values['completed_id'],
                        'completed': TRUE_TASK,
                        'current': FALSE_TASK,
                        'blockers': FALSE_TASK
                    }
                })

            elif task == CURRENT:
                data_object.append({
                    'data': {
                        'datetime': today_date,
                        'user': self.user['username'].capitalize(),
                        'task': values['current_task'],
                        'task_id': values['current_id'],
                        'completed': FALSE_TASK,
                        'current': TRUE_TASK,
                        'blockers': FALSE_TASK
                    }
                })

            elif task == BLOCKERS and values['blockers_id'] is not None:
                data_object.append({
                    'data': {
                        'datetime': today_date,
                        'user': self.user['username'].capitalize(),
                        'task': values['blockers_task'],
                        'task_id': values['blockers_id'],
                        'completed': FALSE_TASK,
                        'current': FALSE_TASK,
                        'blockers': TRUE_TASK
                    }
                })

        for data in data_object:
            platform_connector = PlaftormConnector()
            auth_token = platform_connector.get_token()

            response = requests.post(url=url,
                                     json=data,
                                     headers={
                                         'Authorization': auth_token
                                     }).json()

            if not response['success']:
                auth_token = platform_connector.refresh_token()

                requests.post(url=url,
                              json=data,
                              headers={
                                  'Authorization': auth_token
                              }).json()
