from utils.messages import DefaultMessage
from tracker_application import users


def schedule_message():
    """
    A method which send initial (default) messages to all of the users in the SLACK workspace

    :return empty string, response 200, returned to SLACK server

    A response to the SLACK server should be returned within 3 (three) seconds,
    otherwise the server sends a duplicated task
    """
    list_users = users.get_users()

    for user in list_users:
        if not user['ready_for_report']:
            default_message = DefaultMessage(user)

            default_message.send_message()

    return '', 200
