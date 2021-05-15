from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

from flask import Flask
from flask_apscheduler import APScheduler

from utils.constant_variables import TOKEN, SIGNING_SECRET

import pprint

# A library which prints dicts "prettier"
printer = pprint.PrettyPrinter()

#Initialize scheduler
scheduler = APScheduler()
scheduler.start()

application = Flask(__name__)

# The endpoint where we would listen for the SLACK events (messages)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', application)

# Connecting the app with SLACK
client = WebClient(token=TOKEN)


def get_cosmos_tracker_id():
    list_channels = client.conversations_list()

    for channel in list_channels['channels']:
        if channel['name'] == 'cosmos-tracker':
            return channel['id']


def get_botID():
    """
    A method which gets the Cosmos-Tracker ID from SLACK

    :return: the bot_id (Cosmos-Tracker ID)
    """
    return client.api_call("auth.test")['user_id']
