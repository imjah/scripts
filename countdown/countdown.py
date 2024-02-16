#!/usr/bin/python3

import argparse
import asyncio
import os
import signal
import subprocess
import threading

async def countdown(to: int, output: str | None, media: str | None):
    total = to

    for unit, interval in {'h': 3600, 'm': 60, 's': 1}.items():
        while total > interval or (total == 1 and unit == 's'):
            sleep = asyncio.create_task(asyncio.sleep(interval))

            try:
                with open(output, 'w') as f:
                    f.write(f'{total // interval}{unit}')
            except (TypeError, FileNotFoundError):
                print(f'{total // interval}{unit}')

            total -= interval

            await sleep

    if media and os.path.exists(media):
        threading.Thread(
            target=lambda: subprocess.run(['mpv', media], capture_output=True)
        ).start()

def parse_time(time):
    try:
        match time[-1]:
            case 'h':
                return int(time[:-1]) * 3600
            case 'm':
                return int(time[:-1]) * 60
            case 's':
                return int(time[:-1])
            case _:
                return int(time)
    except (IndexError, ValueError):
        raise argparse.ArgumentTypeError(f'invalid value "{time}"')

def rm(file: str | None):
    if file and os.path.exists(file):
        os.remove(file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('time', nargs='+', type=parse_time)
    parser.add_argument('-o', '--output', metavar='FILE')
    parser.add_argument('-m', '--media', metavar='FILE')
    args   = parser.parse_args()

    signal.signal(signal.SIGTERM, lambda s, f: [rm(args.output), exit()])

    try:
        while 1:
            for to in args.time:
                asyncio.run(countdown(to, args.output, args.media))
    except KeyboardInterrupt:
        rm(args.output)
        print()
