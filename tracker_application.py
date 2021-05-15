from flask import request, json

from config import application
from celery_conf import process_task, process_update_message

from utils.messages import DefaultMessage, ResponseMessage, Message
from utils.time import SetTimer
from utils.users import Users, User

from config import slack_event_adapter, get_botID, get_cosmos_tracker_id
from utils.constant_variables import DAILY, SNOOZE, SKIP, BLOCKERS, NO, RESPONDED_COMPLETED, \
    RESPONDED_CURRENT, COMPLETED, FOLLOW_UP, NOT_UNDERSTOOD, SUNDAY, SATURDAY, WEEKDAY

from config import printer

COSMOS_TRACKER_ID = get_cosmos_tracker_id()
users = Users(COSMOS_TRACKER_ID)
BOT_ID = get_botID()


@slack_event_adapter.on('message')
def event_message(payload):
    """
    This method catches events send to ulr=..../slack/events
    It checks if we are updating a message or sending an initial message.
    It the message is initial:
        1 -> We check, if the entered text is daily. If it is we send an initial (default) message to the user
        2 -> If the received message is not initial (default) it means that the user has pressed any of the buttons,
            (each user contains three boolean "completed_id", "current_id", "blockers_id).
        3 -> Depending on which tasks the user is currently entering a different response will be send.


    :param payload: (dict, keys depend on the option which the user has chosen)

    :return empty string, response 200, returned to SLACK server

    A response to the SLACK server should be returned within 3 (three) seconds,
    otherwise the server sends a duplicated task
    """
    event = payload['event']

    channel = event.get('channel', None)

    if channel != 'C01MW5Y9YGZ':

        update_message = event.get('subtype', None)

        if update_message is None:
            user_id = event.get('user', None)

            user = users.get_user_by_id(user_id)

            if user is not None and user_id != BOT_ID:
                text = event['text']

                task_id = event['client_msg_id']

                if text.lower() == DAILY:
                    day = SetTimer.get_day()

                    if day == SUNDAY or day == SATURDAY:
                        weekday_message = Message(user)
                        weekday_message.send(WEEKDAY)

                    elif not user['ready_for_report']:
                        default_message = DefaultMessage(user)
                        default_message.send_message()

                    elif user['replied']:
                        follow_up_message = Message(user)
                        follow_up_message.send(FOLLOW_UP)

                elif user['ready_for_report'] and not user['replied'] and (
                        user['tasks']['completed']['completed_id'] is None or
                        user['tasks']['current']['current_id'] is None or
                        user['tasks']['blockers']['blockers_id'] is None):

                    if user['tasks']['completed']['completed_id'] is None:
                        user['tasks']['completed']['completed_id'] = task_id
                        user['tasks']['completed']['completed_task'] = text

                        completed_message = Message(user)
                        completed_message.send(RESPONDED_COMPLETED)

                    elif user['tasks']['current']['current_id'] is None:
                        user['tasks']['current']['current_id'] = task_id
                        user['tasks']['current']['current_task'] = text

                        current_message = Message(user)
                        current_message.send(RESPONDED_CURRENT)

                    elif user['tasks']['blockers']['blockers_id'] is None:
                        if text.lower() == NO:
                            blocker_message = Message(user)
                            blocker_message.send(BLOCKERS)

                            user['replied'] = True
                            process_task.delay(user)
                        else:
                            user['tasks']['blockers']['blockers_id'] = task_id
                            user['tasks']['blockers']['blockers_task'] = text

                            blocker_message = Message(user)
                            blocker_message.send(BLOCKERS)

                            user['replied'] = True
                            process_task.delay(user)    
                else:
                    not_understood = Message(user)
                    not_understood.send(NOT_UNDERSTOOD)

        else:
            updated_message_id = event['message'].get('client_msg_id', None)

            if updated_message_id is not None:
                user_id = event['message'].get('user', None)

                user = users.get_user_by_id(user_id)

                if user is not None and user_id != BOT_ID:
                    text = event['message']['text']

                    task_id = event['message']['client_msg_id']

                    process_update_message.delay(user, text, task_id)

    return '', 200


@application.route('/interactive', methods=['POST'])
def message():
    """
    Method catches which button has the user pressed.
    The three options are:
    TRUE (The user is ready to enter the report)
    SNOOZE (The initial (default) message will be snoozed (resend to the user after 15minutes)
    SKIP (The user skips tha daily report)

    :return empty string, response 200, returned to SLACK server

    A response to the SLACK server should be returned within 3 (three) seconds,
    otherwise the server sends a duplicated task
    """
    payload = request.form.get('payload')

    data = json.loads(payload)

    user = User(data['user']['id'], data['user']['username'])
    user = user.as_dict()

    action_button_value = data['actions'][0]['value'].lower()
    response_url = data['response_url']

    if BOT_ID != user['id']:
        if action_button_value == SNOOZE:
            snooze_message = Message(user)
            snooze_message.send(SNOOZE)

            snooze_time = SetTimer.update(data['message']['ts'])

            response_message = ResponseMessage(user, "Snooze", response_url)
            response_message.update_message()

            default_message = DefaultMessage(user, snooze_time)
            default_message.schedule_message()

        elif action_button_value:
            true_message = Message(user)
            true_message.send(COMPLETED)

            response_message = ResponseMessage(user, "Yes, I'm ready", response_url)
            response_message.update_message()

            users.update_ready_for_report(user['id'], True)

        elif action_button_value == SKIP:
            skip_message = Message(user)
            skip_message.send(SKIP)

            response_message = ResponseMessage(user, "Skip today's report!", response_url)
            response_message.update_message()

    return '', 200
