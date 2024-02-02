import os
import requests
import threading

config = {
    'dir': os.environ.get('XDG_CONFIG_DIR/ttv', f'{os.environ.get("HOME")}/.config/ttv'),
    'safetwitch_api': 'https://stbackend.drgns.space/api'
}

class User:
    def __init__(self, name):
        self.name = name
        self.data = None

    def fetch(self):
        response = requests.get(f'{config["safetwitch_api"]}/users/{self.name}')

        if response.status_code == 200:
            self.data = response.json()['data']

class Users:
    def __init__(self):
        self._read_users()

    def fetch(self):
        threads = [threading.Thread(target=user.fetch) for user in self.data]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def _read_users(self):
        self.data = []

        with open(f'{config["dir"]}/channels') as file:
            for line in sorted(file):
                self.data.append(User(line.strip()))

if __name__ == '__main__':
    users = Users()
    users.fetch()

    for user in users.data:
        if (user.data['isLive']):
            print(f'{user.name} {user.data["stream"]["topic"]} {user.data["stream"]["viewers"]}')
