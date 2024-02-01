#!/usr/bin/python3

import os
import requests
import threading

config = {
    'dir': os.environ.get('XDG_CONFIG_DIR/ttv', f'{os.environ.get("HOME")}/.config/ttv'),
    'icons': {
        'online': 'U',
        'offline': 'D'
    },
    'channels': []
}

class Channel:
    def __init__(self, name):
        self.name = name
        self.live = False

    def get_status(self):
        self.live = self._get_status()

    def _get_status(self):
        response = requests.get(f'https://twitch.tv/{self.name}')

        if response.status_code != 200:
            return False

        if '"isLiveBroadcast":true' not in response.text:
            return False

        return True

class Channels:
    def __init__(self, names):
        self._channels = []

        for name in names:
            self._channels.append(
                Channel(name)
            )

    def get_status(self):
        threads = []

        for channel in self._channels:
            threads.append(
                threading.Thread(target=channel.get_status)
            )

            threads[-1].start()

        for thread in threads:
            thread.join()

        return self._channels

def read_config():
    with open(f'{config["dir"]}/channels') as channels:
        for channel in sorted(channels):
            config['channels'].append(channel.strip())

if __name__ == '__main__':
    read_config()

    channels = Channels(config['channels']).get_status()

    for channel in sorted(channels, key=lambda k: k.live, reverse=True):
        icon = config['icons']['offline']

        if channel.live:
            icon = config['icons']['online']

        print(f'{icon} {channel.name}')
