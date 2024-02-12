#!/usr/bin/python3

import os
import signal
import sys
import time

config = {
    'output': os.getenv('OUTPUT', None)
}

def countdown(to: int):
    total = to

    for unit, interval in {'h': 3600, 'm': 60, 's': 1}.items():
        timer = int(total / interval)

        if timer < 2 and unit != 's':
            continue

        while timer:
            display(f"{timer}{unit}")
            time.sleep(interval)
            total -= interval
            timer = int(total / interval)

    os.system("mpv /usr/share/sounds/budgie/default/alerts/bark.ogg")

def display(v: str):
    try:
        with open(config['output'], 'w') as file:
            file.write(v)
    except (TypeError, FileNotFoundError):
        print(v)

def parse_time(t: str) -> int:
    try:
        return int(t)
    except ValueError:
        try:
            match t[-1]:
                case "s":
                    return int(t[:-1])
                case "m":
                    return int(t[:-1]) * 60
                case "h":
                    return int(t[:-1]) * 3600
        except (IndexError, ValueError):
            return 0

def remove_output():
    try:
        os.remove(config['output'])
    except (TypeError, OSError) as e:
        pass

def main():
    signal.signal(signal.SIGTERM, lambda s, f: [remove_output(), exit()])

    try:
        to = parse_time(sys.argv[1])
    except IndexError:
        sys.exit(f"Usage: {os.path.basename(sys.argv[0])} <time>")

    try:
        while to:
            countdown(to)
    except KeyboardInterrupt:
        remove_output()
        print()

if __name__ == "__main__":
    main()
