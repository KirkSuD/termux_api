# termux_api

Simple Python module to call [termux-api](https://wiki.termux.com/wiki/Termux:API) by subprocess.  
I used qpython + sl4a before. This is made to call termux-api in my Python scripts.

Exception-free module to call termux-api.  
Most calls return (result, error). Please check error is None. Result is None if not a query.  
Thin wrapper around termux-api. Function & param names are close to the official wiki.

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

Currently, this supports all API implementations on wiki.  
But some are not fully tested, so please use with some caution.

Most functions return (result, error), function and param names are close to the wiki.  
Function docstrings contain some hints about valid args, or test result of the function.

Special functions:
- Generators yield (result, error): `location(request="updates")`, `sensor()`.
- `tts_speak_init()` starts a Popen, return `speak(text)` & `close()`.

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

## Bug report

If you find a bug, please submit an issue. Thank you.
