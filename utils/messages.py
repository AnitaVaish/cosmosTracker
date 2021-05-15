import requests
from requests.exceptions import ChunkedEncodingError

from config import client

from utils.time import SATURDAY, SUNDAY
from utils.constant_variables import SNOOZE, SKIP, BLOCKERS, RESPONDED_COMPLETED, RESPONDED_CURRENT, COMPLETED, \
    FOLLOW_UP, NOT_UNDERSTOOD, TRUE_TASK, FALSE_TASK, WEEKDAY


class DefaultMessage:
    """
    This class created the initial (default) message, which is send to the user
    """

    def __init__(self, user, scheduled_time=None):
        self.user = user
        self.scheduled_time = scheduled_time

    @staticmethod
    def _create_message(user, scheduled_time=None):
        """
        A static method to create the initial (default) message send to the user

        :param user: an user object
        :param scheduled_time: If scheduled_time is given (when to schedule a message for the user - user by SNOOZE)
        :return: as message object displayed in SLACK
        """
        user_id = user['id']
        username = user['username'].capitalize()

        message = {
            "user": user_id,
            "channel": f"@{user_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey *{username}*! :wave:\n"
                                f"Are you ready to fill out the *CT Daily Report*?"
                    },
                },
                {
                    "type": "actions",
                    "block_id": "actionblock789",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Yes, I'm ready!"
                            },
                            "style": "primary",
                            "value": "True"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Skip today's report!"
                            },
                            "style": "danger",
                            "value": "False"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Snooze"
                            },
                            "value": "Snooze"
                        },
                    ]
                }
            ]
        }

        if scheduled_time is not None:
            message['post_at'] = scheduled_time

        return message

    def send_message(self):
        message = self._create_message(self.user)

        response = client.chat_postMessage(channel=message['channel'],
                                           blocks=message['blocks'],
                                           text=message['blocks'][0]['text']['text'])

        message['response'] = response

        return response

    def schedule_message(self):
        message = self._create_message(self.user,
                                       self.scheduled_time, )

        response = client.chat_scheduleMessage(channel=message['channel'],
                                               blocks=message['blocks'],
                                               text=message['blocks'][0]['text']['text'],
                                               post_at=message['post_at'])

        message['response'] = response


class ResponseMessage:
    """
    This class displays which options from the initial (default) message has the user chosen
    """

    def __init__(self, user, text, response_url):
        self.user = user
        self.text = text
        self.response_url = response_url

    @staticmethod
    def _create_message(user, text):
        """
        A static method to create the response message

        :param user: an user object
        :param text: the text (option) which was chosen by the user
        :param response_url: this is the way to find the message in SLACK,
                            message in SLACK are updated by their urls
        :return: as message object displayed in SLACK
        """
        user_id = user['id']
        username = user['username'].capitalize()

        return {
            "user": user_id,
            "channel": f"@{user_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey *{username}*! :wave:\n"
                                f"Are you ready to fill out the *CT Daily Report*? \n"
                                f">{text}\n"
                    },
                },
            ]
        }

    def update_message(self):
        message = self._create_message(self.user, self.text)

        response = requests.post(url=self.response_url,
                                 json=message)

        return response


class UpdateMessage:
    """
    This class updates the user messages (it performs a put request to the platform)
    """

    def __init__(self, user, text, task_id):
        self.user = user
        self.text = text
        self.task_id = task_id
        self.url = f'http://52.47.206.24:4000/api/records/cosmos_tracker/?page=0&limit=5&duplicate_call=false'
        self.put_url = f"http://52.47.206.24:4000/api/record/cosmos_tracker/"

    def update_message(self):
        """
        This method is responsible for updating tasks on the platform

        1 - It gets the tasks from the platform, it filters the get request by the task_id
        2 - It updates the tasks
        """

        import requests
        from utils.platform import PlaftormConnector
        from utils.time import datetime

        search_value = f"\"task_id\" = '{self.task_id}'"

        data = {
            'data': {
                "value_filter": f"{search_value}"
            }
        }

        platform_connector = PlaftormConnector()
        auth_token = platform_connector.get_token()

        response = requests.get(url=self.url,
                                json=data,
                                headers={
                                    'Authorization': auth_token
                                }).json()

        if not response['success']:
            auth_token = platform_connector.refresh_token()

            response = requests.get(url=self.url,
                                    json=data,
                                    headers={
                                        'Authorization': auth_token
                                    }).json()

        today_date = datetime.now()
        today_date = today_date.strftime("%Y-%m-%d")

        entry_id = response['rows'][0].get('id', None)
        entry_date = response['rows'][0].get('datetime', None)

        if entry_id and entry_date and (str(today_date) in entry_date):
            blocker = response['rows'][0]['blocker']
            completed = response['rows'][0]['completed']
            current = response['rows'][0]['current']

            if blocker is True:
                blocker = TRUE_TASK
                completed = FALSE_TASK
                current = FALSE_TASK

            if completed is True:
                blocker = FALSE_TASK
                completed = TRUE_TASK
                current = FALSE_TASK

            if current is True:
                blocker = FALSE_TASK
                completed = FALSE_TASK
                current = TRUE_TASK

            update_datetime = datetime.now()
            update_datetime = update_datetime.strftime("%Y-%m-%d %H:%M:%S")

            data = {
                'data': {
                    "id": entry_id,
                    'datetime': update_datetime,
                    'user': self.user['username'].capitalize(),
                    'task': self.text,
                    'task_id': self.task_id,
                    "completed": completed,
                    "current": current,
                    "blocker": blocker
                }
            }

            response = requests.put(url=self.put_url,
                                    json=data,
                                    headers={
                                        'Authorization': auth_token
                                    }).json()

            if not response['success']:
                auth_token = platform_connector.refresh_token()

                requests.put(url=self.put_url,
                             json=data,
                             headers={
                                 'Authorization': auth_token
                             }).json()


class WeekendMessage:
    """
    This class displays a message, if the user tries to enter a task on a weekend
    """

    def __init__(self, user):
        self.user = user
        self.text = "It is `weekend`, no tasks for today! :tada:"

    def send(self):
        from utils.time import date, calendar

        today_day = date.today()

        day = calendar.day_name[today_day.weekday()]

        if day == SATURDAY or day == SUNDAY:
            user_id = self.user['id']

            client.chat_postMessage(channel=f"@{user_id}",
                                    text=self.text)


class Message:
    """
    This class displays a follow-up message after the user chosen an options from the initial (default) message
    """

    def __init__(self, user):
        self.user = user

    def send(self, response):
        """
        This method is responsible for the follow-up message, depending on the chosen option from the user

        :param response: the option which the user has chosen
        """
        text = ''
        user_id = self.user['id']
        username = self.user['username'].capitalize()

        if response.lower() == COMPLETED:
            text = f"Sure thing *{username}*, let's begin with the CT Daily Report. :sunglasses:\n\n" \
                   "What tasks did you complete yesterday?"

        elif response.lower() == SKIP:
            text = f"Ok *{username}* :sneezing_face:, " \
                   f"you can fill out the CT Daily report later by typing `daily`!"

        elif response.lower() == SNOOZE:
            text = f"Sure thing *{username}*, I will remind you in `15 minutes`! :wink:"

        elif response.lower() == RESPONDED_COMPLETED:
            text = 'What are you planning to work on today?'

        elif response.lower() == RESPONDED_CURRENT:
            text = 'Great. Do you have any blockers? If so, just tell me. Otherwise please say: no.'

        elif response.lower() == BLOCKERS:
            text = 'Well done! Your update for CT Daily Report was completed.'

        elif response.lower() == FOLLOW_UP:
            text = "There's no more pending follow-ups."

        elif response.lower() == NOT_UNDERSTOOD:
            text = "The command is not understood!"

        elif response.lower() == WEEKDAY:
            text = "You don't have any active check-ins to complete today!"

        client.chat_postMessage(channel=f'@{user_id}',
                                text=text)
