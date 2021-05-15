from config import client
from utils.constant_variables import COMPLETED, CURRENT


class User:
    """
    The class creates a representation of what kind of keys each user object contains
    """

    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.ready_for_report = False
        self.replied = False
        self.tasks = {
            'completed': {
                'completed_id': None,
                'completed_task': None
            },
            'current': {
                'current_id': None,
                'current_task': None
            },
            'blockers': {
                'blockers_id': None,
                'blockers_task': None
            }
        }

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ready_for_report': self.ready_for_report,
            'replied': self.replied,
            'tasks': self.tasks,
        }


class Users:
    """
    This class creates a list of User objects
    The users are taken from the SLACK workspace
    """

    def __init__(self, cosmos_tracker_id):
        self.client = client
        self.list_users = []
        self.cosmos_tracker_id = cosmos_tracker_id

        channel_members = client.conversations_members(channel=self.cosmos_tracker_id)
        members_id_list = [member for member in channel_members['members']]

        result = client.users_list()
        all_users = result["members"]

        for usr in all_users:
            if usr['id'] in members_id_list and usr['name'] != 'cosmos_tracker':
                user = User(usr['id'], usr['name'])
                user = user.as_dict()

                self.list_users.append(user)

    def get_users(self):
        return self.list_users

    def update_ready_for_report(self, user_id, mark):
        for usr in self.list_users:
            if usr['id'] == user_id:
                usr['ready_for_report'] = mark

    def update_id(self, user_id, response_id, mark):
        for usr in self.list_users:
            if usr['id'] == user_id:
                if mark == COMPLETED:
                    usr['tasks']['completed']['completed_id'] = response_id
                elif mark == CURRENT:
                    usr['tasks']['completed']['current_id'] = response_id
                else:
                    usr['tasks']['completed']['blockers_id'] = response_id

    def get_user_by_id(self, user_id):
        for usr in self.list_users:
            if usr['id'] == user_id:
                return usr

        return None

    def reset(self):
        for usr in self.list_users:
            usr['ready_for_report'] = False
            usr['replied'] = False
            usr['tasks'] = {
                'completed': {
                    'completed_id': None,
                    'completed_task': None
                },
                'current': {
                    'current_id': None,
                    'current_task': None
                },
                'blockers': {
                    'blockers_id': None,
                    'blockers_task': None
                }
            }
