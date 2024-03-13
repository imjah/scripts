# TTV

Resource friendly, distraction free feed for Twitch and YouTube livestreams built with [SafeTwitch](https://codeberg.org/safetwitch) and [Piped](https://github.com/teampiped) APIs.

**Install**

Make sure you have [`just`](https://github.com/casey/just) and `python3` installed. In [ttv](ttv) directory:

```
just setup && just build && just install
```

**Uninstall**

```
just uninstall
```

**Configure**

```yaml
# ~/.config/ttv/config.yml

twitch:
  - <channel-id>
  - ...

youtube:
  - <channel-id>
  - ...

piped:
  - https://pipedapi.kavin.rocks
  - ...

safetwitch:
  - https://stbackend.drgns.space
  - ...
```

**Usage**

View available livestreams:

```
ttv
```

View available livestreams, select and play one of them:

```
MENU="fzf" PLAYER="mpv" ttvmenu
```

> [`fzf`](https://github.com/junegunn/fzf) and [`mpv`](https://github.com/mpv-player/mpv) are used by default, but you can change it as shown above.
