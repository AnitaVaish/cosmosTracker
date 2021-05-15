import calendar
from datetime import datetime, timedelta, date, time
from utils.constant_variables import SATURDAY, SUNDAY


class SetTimer:
    """
    The class is responsible for setting the time, on specific messages
    """
    def __init__(self, day, hour, minutes):
        self.day = day
        self.hour = hour
        self.minutes = minutes

    def set(self):
        tomorrow = date.today() + timedelta(days=self.day)
        scheduled_time = time(hour=self.hour, minute=self.minutes)

        day = calendar.day_name[tomorrow.weekday()]

        if day != SATURDAY and day != SUNDAY:
            schedule_timestamp = datetime.combine(tomorrow, scheduled_time).timestamp()

            return str(schedule_timestamp)

    @staticmethod
    def update(message_time):
        """
        This method sets the snooze time

        :param message_time: when the snooze message should be sent
        :return: string of the time
        """
        current_time = datetime.fromtimestamp(int(float(message_time)))
        update_time = (current_time + timedelta(minutes=15)).timestamp()

        return str(update_time)

    @staticmethod
    def get_day():
        day = calendar.day_name[date.today().weekday()]

        return day
