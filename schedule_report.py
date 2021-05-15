from utils.reports import FinalReport


def schedule_report():
    """
    A method which initialized the Final report  and send it to the users

    :return empty string, response 200, returned to SLACK server

    A response to the SLACK server should be returned within 3 (three) seconds,
    otherwise the server sends a duplicated task
    """
    final_report = FinalReport()

    final_report.send()

    return '', 200
