import requests

from utils.constant_variables import conf, PLATFORM_EMAIL, PLATFORM_PASSWORD, PLATFORM_AUTH_TOKEN


class PlaftormConnector:
    """
    This class establishes the connection with the platform

    It also updated the the token, which is needed to connect to the platform
    """

    def __init__(self):
        self.email = PLATFORM_EMAIL
        self.password = PLATFORM_PASSWORD
        self.auth_token = PLATFORM_AUTH_TOKEN

    def get_token(self):
        return self.auth_token

    def refresh_token(self):
        """
        This method check if the authentication token is expired, if so the token is refreshes
        (It re-logs in the platform, the new token in saved in the conf.cfg five)

        :return: the updated authentication token, needed to connect to the platform
        """
        login_url = 'http://52.47.206.24:4000/api/login/'
        login_data = {
            'email': self.email,
            'password': self.password,
        }

        response = requests.post(url=login_url,
                                 json=login_data)
    
        new_token = response.json()['user']['token']
        
        auth_token = f'Bearer {new_token}'

        conf.set("Platform", "auth_token", auth_token)

        conf.write(open("conf.cfg", "w"))

        return auth_token
