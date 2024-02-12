#!/usr/bin/python3

import argparse
import asyncio
import os
import signal
import sys

async def countdown(to: int, file: str | None):
    def write(s: str):
        try:
            with open(file, 'w') as f:
                f.write(s)
        except (TypeError, FileNotFoundError):
            print(s)

    total = to

    for unit, interval in {'h': 3600, 'm': 60, 's': 1}.items():
        while total > interval or (total == 1 and unit == 's'):
            sleep = asyncio.create_task(asyncio.sleep(interval))
            write(f'{total // interval}{unit}')
            total -= interval
            await sleep

    os.system("mpv /usr/share/sounds/budgie/default/alerts/bark.ogg")

def parse_time(t: str) -> int:
    match t[-1]:
        case "h":
            return int(t[:-1]) * 3600
        case "m":
            return int(t[:-1]) * 60
        case "s":
            return int(t[:-1])
        case _:
            return int(t)

def rm(f: str | None):
    if f and os.path.exist(f):
        os.remove(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('time', nargs='+')
    parser.add_argument('-o', '--output', metavar='FILE')
    args   = parser.parse_args()
    signal.signal(signal.SIGTERM, lambda s, f: [rm(args.output), exit()])

    try:
        while 1:
            for to in [parse_time(t) for t in args.time]:
                asyncio.run(countdown(to, args.output))
    except (ValueError, IndexError):
        sys.exit('Invalid time value')
    except KeyboardInterrupt:
        rm(args.output)

if __name__ == "__main__":
    main()
