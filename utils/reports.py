import requests
from requests.exceptions import ChunkedEncodingError

from utils.time import date
from utils.platform import PlaftormConnector

from config import client, get_cosmos_tracker_id


class Report:
    """
    After a user enters all tasks, an individual report is send to a specified channel

    Those reports are filtered for a specific user on the specific date (today)
    """

    def __init__(self, user, channel):
        self.user = user
        self.channel = channel

    @staticmethod
    def _create_report(user, completed, current, blocker, channel):
        """
        This is a static method which creates the way the individual report is displayed in the channel

        :param user: It receives a user object
        :param completed tasks
        :param current tasks
        :param blocker tasks
        :param channel: on which channel to create the report
        :return:
        """
        username = user['username'].capitalize()

        text_header = f'I just got a new response by *{username}* for the CT Daily Report follow-up.\nCheck it out:\n'

        if channel is None:
            user_id = user['id']
            channel = f"@{user_id}"
            text_header = 'This is the status of your Follow-Ups for today:'

        message = {
            "channel": channel,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text_header
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Completed Tasks*\n{completed}"
                    },
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Current Tasks*\n{current}"
                    },
                },
                {
                    "type": "divider"
                }
            ]
        }

        if blocker:
            message['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Blockers*\n{blocker}"
                    },
                },
            )
            message['blocks'].append(
                {
                    "type": "divider"
                },
            )

        return message

    @staticmethod
    def _get_tasks(user):
        return user['tasks']['completed'].get('completed_task', None), user['tasks']['current'].get(
            'current_task', None), user['tasks']['blockers'].get('blockers_task', None)

    def send(self):
        completed, current, blocker = self._get_tasks(self.user)

        individual_report = self._create_report(self.user, completed, current, blocker, self.channel)

        client.chat_postMessage(channel=individual_report['channel'],
                                blocks=individual_report['blocks'],
                                text=individual_report['blocks'][0]['text']['text'])


class FinalReport:
    """
    This class creates the final report which is send to a specific channel. It is created for all user,
    a short summary of the responses of the day
    """

    @staticmethod
    def _create_report(responded, blockers, awaiting, result):
        """
        This is a static method which creates how to final report message will look like

        :param responded - message
        :param blockers - message
        :param awaiting - message
        :param result - response object
        :return: It returns an object which is displayed in SLACK
        """
        formatted_awaiting = ",".join(awaiting)

        message = {
            "channel": "#cosmos-tracker",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Hey! The CT Daily Report follow-up report is ready!:tada::mega:",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{len(responded)} responded :dart:\n{len(blockers)} blockers :octagonal_sign:",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{len(awaiting)} team members are pending to respond",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{formatted_awaiting}",
                    }
                },
                {
                    "type": "divider"
                },
            ]
        }

        for entry in result:
            name = list(entry.keys())
            values = list(entry.values())

            completed = values[0].get('completed', None)
            current = values[0].get('current', None)
            blocker = values[0].get('blocker', None)

            message['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{name[0]}*",
                    }
                },
            )

            if completed:
                message['blocks'].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Completed Tasks*\n{completed}\n"
                        }
                    },
                )

            if current:
                message['blocks'].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Current Tasks*\n{current}\n"
                        }
                    },
                )

            if blocker:
                message['blocks'].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Blockers*\n{blocker}\n"
                        }
                    },
                )

            message['blocks'].append(
                {
                    "type": "divider"
                },
            )

        return message

    @staticmethod
    def _get_tasks():
        """
        This method is responsible for getting all tasks which are entered for a specific day from the platform

        :return: It returns responded, blockers, awaiting - messages and the response object (result)
        """

        from utils.users import Users
        url = f'http://52.47.206.24:4000/api/records/cosmos_tracker/?page=0&limit=5&duplicate_call=false'

        today_date = date.today()
        search_value = f"datetime::date = '{today_date}'"

        data = {
            'data': {
                "value_filter": f"{search_value}"
            }
        }

        platform_connector = PlaftormConnector()
        auth_token = platform_connector.get_token()

        response = requests.get(url=url,
                                json=data,
                                headers={
                                    'Authorization': auth_token
                                }).json()

        if not response['success']:
            auth_token = platform_connector.refresh_token()

            response = requests.get(url=url,
                                    json=data,
                                    headers={
                                        'Authorization': auth_token
                                    }).json()

        if response['rows']:
            blockers = [entry['task'] for entry in response['rows']
                        if entry['blocker'] is True]

            COSMOS_TRACKER_ID = get_cosmos_tracker_id()
            users = Users(COSMOS_TRACKER_ID)

            responded = set(entry['user'] for entry in response['rows'])

            awaiting = [f"<@{user['username']}>" for user in users.get_users()
                        if user['username'].capitalize() not in responded]

            result = []

            for user in responded:
                response_object = {user: {}}

                for entry in response['rows']:
                    if entry['user'] == user:
                        if entry['completed']:
                            response_object[user].update({'completed': entry['task']})
                        elif entry['current']:
                            response_object[user].update({'current': entry['task']})
                        elif entry['blocker']:
                            response_object[user].update({'blocker': entry['task']})

                result.append(response_object)

            return responded, blockers, awaiting, result

    def send(self):
        responded, blocker, awaiting, result = self._get_tasks()

        individual_report = self._create_report(responded, blocker, awaiting, result)

        client.chat_postMessage(channel=individual_report['channel'],
                                blocks=individual_report['blocks'],
                                text=individual_report['blocks'][0]['text']['text'])
