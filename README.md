<<<<<<< HEAD
# cosmosTracker
=======
# Cosmos Tracker
The App automates daily stand-ups and reduces the need for meetings.

Track automatically what your team is up to.

# Install Requirements
Install all requirements from .txt file perform following command:
pip install -r requirements.txt

# Configuration
The main configuration file should be called conf.cfg.

It should be in the same directory as app.py. It should contain all of the credentials:

[Slack]
- token = ...
- signing_secret = ...

[Platform]

- email = ...
- password = ...
- auth_token = ...

[RabbitMQ]
- user = ...
- rabbit_password = ...
- ip = ...

[Time]
- initial_message_hour = ... (example: 9)
- initial_message_minutes = ... (example: 30)

- report_hour = ... (example: 11)
- report_minutes = ... (example: 0)

- day_of_week = ... (example: mon-fri)

- user_reset_hour = ... (example: 23)
- user_reset_minutes = ... (example: 59)
>>>>>>> 25b7c2d (Replace 3 scheduler with one)
