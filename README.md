# TTV

Resource friendly, distraction free feed for Twitch and YouTube livestreams built with [SafeTwitch](https://codeberg.org/safetwitch) and [Piped](https://github.com/teampiped) APIs.

**Install**

Make sure you have [`just`](https://github.com/casey/just) and `python3` installed.

```
cd ttv && just setup && just build && just install
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

Show available livestreams:

```
ttv
```

Show available livestreams, select and play one of them:

```
MENU="fzf" PLAYER="mpv" ttvmenu
```

Show chat (YouTube not supported):

```
ttv --chat <channel-id>
```
