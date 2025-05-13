# termux_api

Simple Python module to call [termux-api](https://wiki.termux.com/wiki/Termux:API) by subprocess.

Exception-free module to call termux-api.  
Most calls return (result, error). Please check error is None. Result is None if not a query.  
Thin wrapper around termux-api. Function & param names are close to the [official wiki](https://wiki.termux.com/wiki/Termux:API).  
If wiki is not detailed enough, here's the official repos: [termux-api](https://github.com/termux/termux-api), [termux-api-package](https://github.com/termux/termux-api-package).

## Archived

Support most APIs of v0.50.1, but not updated after v0.51.0 is released.  
(Probably still works for many cases, but please be careful.)

## Requirements

- Python 3.7+, because of [subprocess.run(capture_output=True)](https://docs.python.org/3/library/subprocess.html#subprocess.run).

## How to use

Install Termux & Termux:API app, then `pkg install termux-api`,  
`import termux_api`, then call any function.  
(Certain calls require some permissions to be granted to the Termux API app.)

Example:
```
import termux_api
termux_api.vibrate()
```

[pdoc](https://pdoc.dev/) can be used to generate simple docs:  
`pip install pdoc`, `pdoc termux_api.py`.

## APIs

Currently, this supports all API implementations on wiki. (v0.50.1)  
But some are not fully tested, so please use with some caution.

Most functions return (result, error), function and param names are close to the wiki.  
Function docstrings contain some hints about valid args, or test result of the function.

Special functions:
- Generators yield (result, error): `location(request="updates")`, `sensor()`.
- `tts_speak_init()` starts a Popen, then returns 2 functions: `speak(text)` & `close()`.

Some outputs from termux-api are not json, so it's hard to get results programmatically.  
I tried to read the source code, and parsed most of them:
- `media_player_info()`: return {Track: None} or {Status, Track, Current Position}
- `media_player_play()`: error if not `Now Playing`
- `media_player_pause()`: True if paused, None if already paused, False if no track
- `media_player_resume()`: True if resumed, None if already playing, False if no track
- `media_player_stop()`: True if stopped, False if no track
- `media_scan()`: return scanned file count
- `microphone_record()`: error if not `Recording started`
- `microphone_record_stop()`: True if stopped, False if no recording
- `sensor_cleanup()`: True if successful, False if unnecessary

These functions' outputs are not parsed. Raw strings are returned:
- `job_scheduler*()`: looks complicated

### APIs not on wiki

These APIs, which are not listed on the wiki, are not implemented yet:
```
termux-audio-info
termux-keystore
termux-nfc
termux-notification-channel
termux-notification-list
termux-saf-create
termux-saf-dirs
termux-saf-ls
termux-saf-managedir
termux-saf-mkdir
termux-saf-read
termux-saf-rm
termux-saf-stat
termux-saf-write
termux-speech-to-text
```

## Bug report

If you find a bug, please submit an issue. Thank you.
