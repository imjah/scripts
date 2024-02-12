#!/usr/bin/python3

import asyncio
import os
import signal
import sys

config = {
    'output': os.getenv('OUTPUT', None)
}

async def countdown(to: int):
    total = to

    for unit, interval in {'h': 3600, 'm': 60, 's': 1}.items():
        while total > interval or (total == 1 and unit == 's'):
            sleep = asyncio.create_task(asyncio.sleep(interval))
            display(f'{total // interval}{unit}')
            total -= interval
            await sleep

    os.system("mpv /usr/share/sounds/budgie/default/alerts/bark.ogg")

def display(s: str):
    try:
        with open(config['output'], 'w') as file:
            file.write(s)
    except (TypeError, FileNotFoundError):
        print(s)

def parse_seconds(t: str) -> int:
    match t[-1]:
        case "h":
            return int(t[:-1]) * 3600
        case "m":
            return int(t[:-1]) * 60
        case "s":
            return int(t[:-1])
        case _:
            return int(t)

def clean_and_exit():
    try:
        os.remove(config['output'])
    except (TypeError, OSError):
        pass

    sys.exit('')

def main():
    signal.signal(signal.SIGTERM, lambda s, f: clean_and_exit())

    if len(sys.argv) < 2:
        sys.exit(f'Usage: {os.path.basename(sys.argv[0])} <time..>')

    try:
        times = [parse_seconds(time) for time in sys.argv[1:]]
    except (IndexError, ValueError):
        sys.exit('Invalid time value')

    try:
        while 1:
            for time in times:
                asyncio.run(countdown(time))
    except KeyboardInterrupt:
        clean_and_exit()

if __name__ == "__main__":
    main()
