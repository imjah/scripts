from argparse import ArgumentParser
from datetime import datetime
from json import JSONDecodeError
from websockets import InvalidURI, InvalidHandshake, ProtocolError
import asyncio
import json
import os
import re
import requests
import sys
import threading
import time
import websockets
import yaml

class Stream:
    def __init__(self, **kwargs):
        self.url     = kwargs.get('url'    , 'unknown')
        self.user    = kwargs.get('user'   , 'unknown')
        self.title   = kwargs.get('title'  , 'unknown')
        self.topic   = kwargs.get('topic'  , 'unknown')
        self.viewers = kwargs.get('viewers', 'unknown')
        self.date    = kwargs.get('date'   , 'unknown')

    def __str__(self) -> str:
        return '{:16}  {:48}  {:24}  {:<8,}  {}  {}'.format(
            self.user[:16],
            self._get_title_without_emojis()[:48],
            self.topic[:24],
            self.viewers,
            self._get_date_clock(),
            self.url
        )

    def _get_date_clock(self) -> str:
        date = datetime.strptime(self.date, '%Y-%m-%dT%H:%M:%S%z')
        diff = datetime.now(date.tzinfo) - date

        return time.strftime('%H:%M:%S', time.gmtime(diff.total_seconds()))

    def _get_title_without_emojis(self) -> str:
        emojis = re.compile('[\U0001F300-\U0001F9FF]+', flags=re.UNICODE)
        spaces = re.compile('\s+')

        return spaces.sub(' ', emojis.sub('', self.title)).strip()

class Channel:
    def __init__(self, id, config):
        self.id      = id
        self.streams = []
        self.fetched = False
        self.timeout = config['timeout']

    def fetch(self):
        for url in self.urls:
            try:
                self._fetch(url)
                self.fetched = True

                return
            except (KeyError, requests.RequestException) as e:
                continue

class TT(Channel):
    def __init__(self, id, config):
        super().__init__(id, config)

        self.urls = config['safetwitch']

    def _fetch(self, url):
        channel = requests.get(f'{url}/api/users/{self.id}', timeout=self.timeout).json()['data']

        if channel['isLive']:
            self.streams.append(
                Stream(
                    url     = 'https://twitch.tv/' + self.id,
                    user    = channel['username'],
                    topic   = channel['stream']['topic'],
                    title   = channel['stream']['title'],
                    viewers = channel['stream']['viewers'],
                    date    = channel['stream']['startedAt'].replace('Z', '+00:00')
            ))

class YT(Channel):
    def __init__(self, id, config):
        super().__init__(id, config)

        self.urls = config['piped']

    def _fetch(self, url):
        videos = requests.get(f'{url}/channels/tabs?data={{"id":"{self.id}","contentFilters":["livestreams"]}}', timeout=self.timeout).json()['content']

        for video in videos:
            if video['duration'] == -1:
                stream = requests.get(f'{url}/streams/{video["url"][9:]}', timeout=self.timeout).json()

                self.streams.append(
                    Stream(
                        url     = 'https://youtube.com' + video['url'],
                        user    = stream['uploader'],
                        topic   = stream['category'],
                        title   = stream['title'],
                        viewers = stream['views'],
                        date    = stream['uploadDate']
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

    def streams(self) -> list:
        return sorted([stream for channel in self.channels for stream in channel.streams], key=lambda k: k.user)

    def unfetched(self) -> list:
        return [channel.id for channel in self.channels if not channel.fetched]

class Chat:
    def __init__(self, id: str, config: dict):
        self.id      = id
        self.urls    = config['safetwitch']
        self.timeout = config['timeout']
        self.spacing = config['chat-spacing']*'\n' + '\n'

    async def listen(self):
        print(f'Joining {self.id} chat... ', end='')

        for url in self.urls:
            try:
                await self._listen(url.replace('http', 'ws'))

                return
            except (InvalidURI, InvalidHandshake, ProtocolError):
                continue

        print('failed', end=self.spacing)

    async def _listen(self, url: str):
        async with websockets.connect(url, timeout=self.timeout) as ws:
            await ws.send(f'JOIN {self.id}')

            while 1:
                msg = await ws.recv()

                try:
                    print(self._format(json.loads(msg)), end=self.spacing)
                except JSONDecodeError:
                    print(msg, end=self.spacing)
                finally:
                    continue

    def _format(self, msg: dict):
        try:
            match msg['type']:
                case 'PRIVMSG':
                    return self._format_user(msg)
        except KeyError:
            pass

        return msg

    def _format_user(self, msg: dict):
        return '{}: {}'.format(
            self._colorize(
                msg['tags']['display-name'],
                msg['tags']['color']
            ),
            msg['message'].strip()
        )

    def _colorize(self, msg: str, hex_color: str):
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
        except ValueError:
            return msg

        ansi = 16 + (36 * r // 256) + (6 * g // 256) + (b // 256)

        return f'\033[38;5;{ansi}m{msg}\033[0m'

def get_config() -> dict:
    config_dir = os.environ.get('XDG_CONFIG_HOME', os.environ.get('HOME') + '/.config')

    with open(config_dir + '/ttv/config.yml') as f:
        return {
            **{
                'piped': ['https://pipedapi.kavin.rocks'],
                'safetwitch': ['https://stbackend.drgns.space'],
                'twitch': [],
                'youtube': [],
                'timeout': 5,
                'chat-spacing': 0
            },
            **yaml.safe_load(f)
        }

async def main(args: ArgumentParser):
    config = get_config()

    if args.chat:
        await Chat(args.chat, config).listen()

        return

    channels = Channels(config)
    channels.fetch()

    for stream in channels.streams():
        print(stream)

    if unfeched := channels.unfetched():
        sys.exit(f'error: Cannot fetch channel/s: {", ".join(unfeched)}')

if __name__ == '__main__':
    parser = ArgumentParser(
        prog='ttv',
        description='Feed for Twitch and YouTube livestreams'
    )

    parser.add_argument('-c', '--chat', help='Show chat for given channel id')

    try:
        asyncio.run(
            main(parser.parse_args())
        )
    except FileNotFoundError:
        sys.exit('error: Config not found')
    except yaml.YAMLError as e:
        sys.exit('error: Config syntax: ' + str(e))
    except KeyboardInterrupt:
        print()
