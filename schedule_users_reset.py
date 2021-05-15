from tracker_application import users


def schedule_users_reset():
    """
    A method to reset the users state at specific time
    """

    users.reset()

    print(users.get_users())

    return '', 200
