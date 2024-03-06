from datetime import datetime, timezone
import os
import re
import requests
import sys
import threading
import yaml

def get_config() -> dict:
    config_dir = os.environ.get('XDG_CONFIG_HOME', os.environ.get('HOME') + '/.config')

    with open(config_dir + '/ttv/config.yml') as f:
        return {
            **{
                'piped': 'https://pipedapi.kavin.rocks',
                'safetwitch': 'https://stbackend.drgns.space',
                'twitch': [],
                'youtube': []
            },
            **yaml.safe_load(f)
        }

def td(time: str, format: str = '%Y-%m-%dT%H:%M:%S%z') -> str:
    """Time diff from UTC now in seconds, minutes or hours"""
    time = datetime.strptime(time, format)
    diff = (datetime.now(time.tzinfo) - time).total_seconds()

    for unit, divider in {'h': 3600, 'm': 60, 's': 1}.items():
        time = round(diff / divider)

        if time != 0:
            return f'{time}{unit}'

    return '0s'

class Stream:
    def __init__(self, **kwargs):
        self.url     = kwargs.get('url'    , 'unknown')
        self.user    = kwargs.get('user'   , 'unknown')
        self.topic   = kwargs.get('topic'  , 'unknown')
        self.title   = kwargs.get('title'  , 'unknown')
        self.viewers = kwargs.get('viewers', 'unknown')
        self.elapsed = kwargs.get('elapsed', 'unknown')

    def __str__(self):
        self.remove_emojis_from_title()

        return '{:24}  {:24}  {:64}  {:8}  {:8}  {}'.format(
            self.user[:24],
            self.topic[:24],
            self.title[:64],
            self.viewers[:8],
            self.elapsed[:8],
            self.url
        )

    def remove_emojis_from_title(self):
        # Remove emojis
        self.title = re.sub("["u"\U0001F600-\U0001F64F"u"\U0001F300-\U0001F5FF""]+", '', self.title).strip()

        # Remove double spaces
        self.title = re.sub(r'\s+', ' ', self.title)

class Channel:
    def __init__(self, id, config):
        self.id      = id
        self.config  = config
        self.streams = []

class TT(Channel):
    def fetch(self):
        d = requests.get(f'{self.config["safetwitch"]}/api/users/{self.id}').json()

        try:
            self.streams.append(Stream(
                url=f'https://twitch.tv/{self.id}',
                user=d['data']['username'],
                topic=d['data']['stream']['topic'],
                title=d['data']['stream']['title'],
                viewers=str(d['data']['stream']['viewers']),
                elapsed=td(d['data']['stream']['startedAt'].replace('Z', '+00:00'))
            ))
        except KeyError:
            return

class YT(Channel):
    def fetch(self):
        response = requests.get('{}/channels/tabs?data={}'.format(
            self.config['piped'],
            '{"id":"%i","contentFilters":["livestreams"]}'.replace('%i', self.id)
        ))

        try:
            streams = response.json()['content']
        except KeyError:
            return

        for stream in streams:
            if self.is_live(stream):
                info = self.fetch_stream_info(stream['url'][9:])

                self.streams.append(Stream(
                    url=f'https://youtube.com{stream["url"]}',
                    user=stream['uploaderName'],
                    topic=info['category'],
                    title=stream['title'],
                    viewers=str(stream['views']),
                    elapsed=td(info['uploadDate'])
                ))

    def fetch_stream_info(self, video_id):
        return requests.get(f'{self.config["piped"]}/streams/{video_id}').json()

    def is_live(self, content):
        return content['duration'] == -1

class Channels:
    def __init__(self, config):
        self.channels = [TT(id, config) for id in config['twitch']] \
                      + [YT(id, config) for id in config['youtube']]

    def fetch(self):
        threads = [threading.Thread(target=c.fetch) for c in self.channels]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def streams(self):
        streams = [stream for channel in self.channels for stream in channel.streams]
        streams.sort(key=lambda k: k.viewers, reverse=True)
        streams.sort(key=lambda k: k.topic)

        return streams

def main():
    try:
        config = get_config()
    except FileNotFoundError:
        sys.exit('error: Config not found')
    except yaml.YAMLError as e:
        sys.exit('error: Config syntax: ' + str(e))

    channels = Channels(config)
    channels.fetch()

    for stream in channels.streams():
        print(stream)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
