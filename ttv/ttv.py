import os
import requests
import threading

config = {
    'dir': os.environ.get('XDG_CONFIG_DIR/ttv', f'{os.environ.get("HOME")}/.config/ttv'),
    'safetwitch_api': 'https://stbackend.drgns.space/api'
}

class User:
    def __init__(self, name):
        self.name    = name
        self.live    = False
        self.topic   = ''
        self.viewers = 0

    def fetch(self):
        response = requests.get(f'{config["safetwitch_api"]}/users/{self.name}')

        if response.status_code != 200:
            return

        data = response.json()['data']

        try:
            self.live    = data['isLive']
            self.topic   = data['stream']['topic']
            self.viewers = data['stream']['viewers']
        except KeyError:
            return

class Users:
    def __init__(self):
        self._read_users()

    def fetch(self):
        threads = [threading.Thread(target=user.fetch) for user in self.data]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def sort(self):
        self.data.sort(key=lambda k: k.viewers, reverse=True)
        self.data.sort(key=lambda k: k.topic)

    def online(self):
        return filter(lambda k: k.live, self.data)

    def _read_users(self):
        self.data = []

        with open(f'{config["dir"]}/channels') as file:
            for line in file:
                self.data.append(User(line.strip()))

if __name__ == '__main__':
    users = Users()
    users.fetch()
    users.sort()

    for user in users.online():
        print(f'{user.name} {user.topic} {user.viewers}')
