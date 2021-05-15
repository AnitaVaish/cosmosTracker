from config import application, scheduler
from schedule_message import schedule_message
from schedule_report import schedule_report
from schedule_users_reset import schedule_users_reset
import tracker_application

from utils.constant_variables import INITIAL_MESSAGE_HOUR, INITIAL_MESSAGE_MINUTES, REPORT_HOUR, REPORT_MINUTES, \
    DAY_OF_WEEKS, USER_RESET_HOUR, USER_RESET_MINUTES

if __name__ == "__main__":
    """
    Scheduler to reset all users states
    """
    scheduler.add_job(id='schedule_users_reset',
                    func=schedule_users_reset,
                    trigger='cron',
                    day_of_week=DAY_OF_WEEKS,
                    hour=int(USER_RESET_HOUR),
                    minute=int(USER_RESET_MINUTES))

    """
    Scheduler for the initial (default) message
    
    Method arguments:
    id = unique id (string) the scheduler
    func = which method should be executed
    trigger = how should the scheduler be repeated - "cron"  (24 hours)
    day_of_week = on which days should the scheduler be executed
    hour, minute = exact time of the scheduler
    """
    scheduler.add_job(id='schedule_message',
                    func=schedule_message,
                    trigger='cron',
                    day_of_week=DAY_OF_WEEKS,
                    hour=int(INITIAL_MESSAGE_HOUR),
                    minute=int(INITIAL_MESSAGE_MINUTES))

    """
    Scheduler for the final report message
    """
    scheduler.add_job(id='schedule_report',
                    func=schedule_report,
                    trigger='cron',
                    day_of_week=DAY_OF_WEEKS,
                    hour=int(REPORT_HOUR),
                    minute=int(REPORT_MINUTES))


    application.run(host='0.0.0.0',
                    port=6000,
                    debug=False)
