from datetime import datetime
import os
import requests
import threading

config = {
    'dir': os.environ.get('XDG_CONFIG_DIR/ttv', f'{os.environ.get("HOME")}/.config/ttv'),
    'safetwitch_api': 'https://stbackend.drgns.space/api',
    'piped_api': 'https://pipedapi.kavin.rocks'
}

class TwitchUser:
    def __init__(self, name):
        self.name    = name
        self.live    = False
        self.topic   = ''
        self.viewers = 0
        self.elapsed = ''

    def __str__(self):
        return '{:24} | {:24} | {:<12} | {}'.format(
            self.name,
            self.topic,
            self.viewers,
            self.elapsed
        )

    def fetch(self):
        response = requests.get(f'{config["safetwitch_api"]}/users/{self.name}')

        if response.status_code != 200:
            return

        data = response.json()['data']

        try:
            self.live    = data['isLive']
            self.topic   = data['stream']['topic']
            self.viewers = data['stream']['viewers']
            self.elapsed = self._parse_elapsed(data['stream']['startedAt'])
        except KeyError:
            return

    def _parse_elapsed(self, time: str):
        delta = datetime.utcnow() - datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')

        for unit, interval in {'h': 3600, 'm': 60}.items():
            time = int(delta.total_seconds() / interval)

            if time:
                return f'{time}{unit}'

class YouTubeUser:
    def __init__(self, id):
        self.live    = False
        self.topic   = ''
        self.viewers = 0
        self.id      = id
        self.streams = []

    def __str__(self):
        out = ''

        for stream in self.streams:
            out += '{:24} | {:24} | {:<12}\n'.format(
                stream['url'][:24],
                stream['title'][:24],
                stream['views']
            )

        return out[:-1]

    def fetch(self):
        data = '{"id": "%i", "contentFilters": ["livestreams"]}'.replace('%i', self.id)
        response = requests.get(f'{config["piped_api"]}/channels/tabs?data={data}')

        if response.status_code != 200:
            return

        for stream in response.json()['content']:
            if stream['duration'] == -1:
                self.live = True
                self.streams.append(stream)

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

        try:
            with open(f'{config["dir"]}/users') as file:
                for line in file:
                    self.data.append(TwitchUser(line.strip()))
        except FileNotFoundError:
            return

        try:
            with open(f'{config["dir"]}/youtube-users') as file:
                for line in file:
                    self.data.append(YouTubeUser(line.strip()))
        except FileNotFoundError:
            return

if __name__ == '__main__':
    users = Users()
    users.fetch()
    users.sort()

    for user in users.online():
        print(user)
