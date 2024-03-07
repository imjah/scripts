from datetime import datetime
import os
import re
import requests
import sys
import threading
import yaml

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
        self.error   = False
        self.config  = config
        self.streams = []

class TT(Channel):
    def fetch(self):
        for url in self.config['safetwitch']:
            try:
                return self._fetch(url)
            except (KeyError, requests.RequestException) as e:
                continue

        self.error = True

    def _fetch(self, url):
        channel = requests.get(f'{url}/api/users/{self.id}').json()['data']

        if channel['isLive']:
            self.streams.append(
                Stream(
                    url=f'https://twitch.tv/{self.id}',
                    user=channel['username'],
                    topic=channel['stream']['topic'],
                    title=channel['stream']['title'],
                    viewers=str(channel['stream']['viewers']),
                    elapsed=td(channel['stream']['startedAt'].replace('Z', '+00:00'))
            ))

class YT(Channel):
    def fetch(self):
        for url in self.config['piped']:
            try:
                return self._fetch(url)
            except (KeyError, requests.RequestException) as e:
                continue

        self.error = True

    def _fetch(self, url):
        videos = requests.get(f'{url}/channels/tabs?data={{"id":"{self.id}","contentFilters":["livestreams"]}}').json()['content']

        for video in videos:
            if video['duration'] == -1:
                stream = requests.get(f'{url}/streams/{video["url"][9:]}').json()

                self.streams.append(
                    Stream(
                        url=f'https://youtube.com{video["url"]}',
                        user=stream['uploader'],
                        topic=stream['category'],
                        title=stream['title'],
                        viewers=str(stream['views']),
                        elapsed=td(stream['uploadDate'])
                ))

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

    def errors(self):
        return [channel.id for channel in self.channels if channel.error]

def get_config() -> dict:
    config_dir = os.environ.get('XDG_CONFIG_HOME', os.environ.get('HOME') + '/.config')

    with open(config_dir + '/ttv/config.yml') as f:
        return {
            **{
                'piped': ['https://pipedapi.kavin.rocks'],
                'safetwitch': ['https://stbackend.drgns.space'],
                'twitch': [],
                'youtube': []
            },
            **yaml.safe_load(f)
        }

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

    channels_with_error = channels.errors()

    if channels_with_error:
        sys.exit(f'error: Cannot fetch {len(channels_with_error)} channel(s): {", ".join(channels_with_error)}')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('')
