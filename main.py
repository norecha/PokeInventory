import argparse

from pgoapi import PGoApi


class Main(object):
    def __init__(self):
        self.config = None
        self.api = None

    def init_config(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-a", "--auth", required=True, type=str)
        parser.add_argument("-u", "--username", type=str)
        parser.add_argument("-p", "--password", type=str)
        parser.add_argument("-t", "--token", type=str)
        parser.add_argument("-lat", "--latitude", required=True, type=float)
        parser.add_argument("-lon", "--longitude", required=True, type=float)

        self.config = parser.parse_args()

        if not (self.config.username and self.config.password) and not self.config.token:
            raise Exception("(username and password) or token is required")

    def init_api(self):
        self.api = PGoApi()

        self.api.login(self.config.auth, self.config.username, self.config.password, self.config.latitude,
                       self.config.longitude, 10, app_simulation=False)

    def run(self):
        self.init_config()
        self.init_api()


if __name__ == '__main__':
    Main().run()
