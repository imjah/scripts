from datetime import datetime
import os
import re
import requests
import sys
import threading
import yaml

def td(time: str, format: str = '%Y-%m-%dT%H:%M:%SZ') -> str:
    """Time diff from UTC now in seconds, minutes or hours"""
    diff = (datetime.utcnow() - datetime.strptime(time, format)).total_seconds()

    for unit, divider in {'h': 3600, 'm': 60, 's': 1}.items():
        time = round(diff / divider)

        if time != 0:
            return f'{time}{unit}'

    return '0s'

def remove_emojis(s):
    return re.sub("["u"\U0001F600-\U0001F64F"u"\U0001F300-\U0001F5FF""]+", '', s).strip()

class Stream:
    def __init__(self, **kwargs):
        self.url     = kwargs.get('url'    , 'unknown')
        self.user    = kwargs.get('user'   , 'unknown')
        self.topic   = kwargs.get('topic'  , 'unknown')
        self.viewers = kwargs.get('viewers', 'unknown')
        self.elapsed = kwargs.get('elapsed', 'unknown')

    def __str__(self):
        return '{:24}  {:48}  {:8}  {:8}  {}'.format(
            self.user[:24],
            self.topic[:48],
            self.viewers[:8],
            self.elapsed[:8],
            self.url
        )

class ChannelTwitch:
    def __init__(self, id, config):
        self.id      = id
        self.config  = config
        self.streams = []

    def fetch(self):
        d = requests.get(f'{self.config["safetwitch"]}/api/users/{self.id}').json()

        try:
            self.streams.append(Stream(
                url=f'https://twitch.tv/{self.id}',
                user=d['data']['username'],
                topic=d['data']['stream']['topic'],
                viewers=str(d['data']['stream']['viewers']),
                elapsed=td(d['data']['stream']['startedAt'])
            ))
        except KeyError:
            return

class ChannelYoutube:
    def __init__(self, id, config):
        self.id      = id
        self.config  = config
        self.streams = []

    def fetch(self):
        p = '{"id":"%i","contentFilters":["livestreams"]}'.replace('%i', self.id)
        d = requests.get(f'{self.config["piped"]}/channels/tabs?data={p}').json()

        for c in d['content']:
            if c['duration'] == -1:
                self.streams.append(Stream(
                    url=f'https://youtube.com{c["url"]}',
                    user=c['uploaderName'],
                    topic=remove_emojis(c['title']),
                    viewers=str(c['views'])
                ))

class Channels:
    def __init__(self, config):
        self.channels = [ChannelTwitch(i, config) for i in config['twitch']]
        self.channels += [ChannelYoutube(i, config) for i in config['youtube']]

    def fetch(self):
        threads = [threading.Thread(target=c.fetch) for c in self.channels]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def streams(self):
        return [stream for channel in self.channels for stream in channel.streams]

    def sorted_streams(self):
        streams = self.streams()

        streams.sort(key=lambda k: k.viewers, reverse=True)
        streams.sort(key=lambda k: k.topic)

        return streams

def main():
    config = {
        'dir': f'{os.environ.get("XDG_CONFIG_DIR", os.environ.get("HOME") + "/.config")}/ttv',
        'piped': 'https://pipedapi.kavin.rocks',
        'safetwitch': 'https://stbackend.drgns.space',
        'twitch': [],
        'youtube': []
    }

    try:
        with open(f'{config["dir"]}/config.yml') as file:
            config = {**config, **yaml.safe_load(file)}
    except Exception as e:
        sys.exit(f'Config error: {e}')

    channels = Channels(config)
    channels.fetch()

    for stream in channels.sorted_streams():
        print(stream)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
