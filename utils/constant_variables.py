import configparser

"""
All constant variables which are used in the other files are stored here
"""

conf = configparser.ConfigParser()
conf.read("conf.cfg")

SNOOZE = 'snooze'
SKIP = 'false'
BLOCKERS = 'blockers'
DAILY = 'daily'
SATURDAY = 'Saturday'
SUNDAY = 'Sunday'
WEEKDAY = 'weekday'
DETAILED_VIEW = 'view_here'
RESPONDED_COMPLETED = 'responded_completed'
RESPONDED_CURRENT = 'responded_current'
COMPLETED = 'completed'
CURRENT = 'current'
FINISHED_REPORT = 'finished_report'
YES = 'yes'
NO = 'no'
TRUE_TASK = '1'
FALSE_TASK = '0'
COSMOS_TRACKER = '#cosmos-tracker'
FOLLOW_UP = 'follow_up'
NOT_UNDERSTOOD = 'not_understood'

RABBITMQ_USER = conf['RabbitMQ']['user']
RABBITMQ_PASSWORD = conf['RabbitMQ']['rabbit_password']
RABBITMQ_IP = conf['RabbitMQ']['ip']
RABBITMQ_VHOST = conf['RabbitMQ']['vhost']

TOKEN = conf['Slack']['token']
SIGNING_SECRET = conf['Slack']['signing_secret']

PLATFORM_EMAIL = conf['Platform']['email']
PLATFORM_PASSWORD = conf['Platform']['platform_password']
PLATFORM_AUTH_TOKEN = conf['Platform']['auth_token']

INITIAL_MESSAGE_HOUR = conf['Time']['initial_message_hour']
INITIAL_MESSAGE_MINUTES = conf['Time']['initial_message_minutes']

REPORT_HOUR = conf['Time']['report_hour']
REPORT_MINUTES = conf['Time']['report_minutes']
DAY_OF_WEEKS = conf['Time']['day_of_week']

USER_RESET_HOUR = conf['Time']['user_reset_hour']
USER_RESET_MINUTES = conf['Time']['user_reset_minutes']
