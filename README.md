# termux_api

A simple Python module to call [termux-api](https://wiki.termux.com/wiki/Termux:API) using [subprocess.run()](https://docs.python.org/3/library/subprocess.html#subprocess.run).

Try to make a clean, exception-free module to call termux-api.  
Every call returns named tuple termux_api_result(result, error).  
Please check error is None after every call.  
Result is None if it is not a query API.

I used qpython + sl4a before.
I made this to call termux-api in my Python scripts.

## Requirements

* Python 3.7+, because of [subprocess.run(capture_output=True)](https://docs.python.org/3/library/subprocess.html#subprocess.run).

## How to use

Copy `termux_api.py` to your working directory.  
`import termux_api`, then call the function you want.  
(Certain calls require some permissions to be granted to the Termux API app.)

Example:
```
import termux_api
termux_api.vibrate()
```

## TODO

* make the code cleaner
* improve error detection
* improve tts_speak(), some options are not supported, crash when run multiple at a time, a queue is needed
* improve media_player_...(), maybe try to parse the non-JSON output
* improve microphone_record_...(), maybe try to parse the non-JSON output
* support more APIs?
* check quotes?
* test

## Skipped / not supported APIs

```
termux-call-log  # android >= 9 {"error": "Call log is no longer permitted by Google"}
termux-dialog  # complex
termux-download  # weird, still need testing
termux-job-scheduler  # not on wiki
termux-notification  # complex
termux-notification-remove
termux-sensor  # complex
termux-sms-list  # {"error": "Reading SMS is no longer permitted by Google"}
termux-sms-send  # {"error": "Sending SMS is no longer permitted by Google"}
termux-storage-get  # what does this do?
termux-wallpaper  # not tested
```

## Supported APIs (some are not fully tested)

```
battery_status()
brightness(brightness)
camera_info()
camera_photo(savepath, camera_id=0)
clipboard_get()
clipboard_set(s)
contact_list()
fingerprint()
infrared_frequencies()
infrared_transmit(freq, pattern)  # freq: frequency, pattern: a list of numbers
location(provider="gps", request="once")  # provider: gps/network/passive  # request: once/last/updates
media_player_info()
media_player_play()
media_player_play_file(file)
media_player_pause()
media_player_stop()
media_scan(files, recursive=False, verbose=False)  # not tested  # return plain text
microphone_record(file=None, limit=None, encoder=None, bitrate=None, sample_rate=None, channel_count=None, default=False)
microphone_record_info()
microphone_record_quit()
share(file, action=None, content_type=None, share_to_default_receiver=False, title=None)  # None -> use default
telephony_call(number)
telephony_cellinfo()
telephony_deviceinfo()
toast(s, short=False, position=None, text_color=None, background_color=None)  # position: top/middle/bottom (default: middle)
torch(on=True)
tts_engines()
tts_speak(s, timeout=None)  # not fully supported, problematic
vibrate(duration=None, force=False)  # duration: default: 1000(ms)
volume_get()
volume_set(stream, volume)
wifi_connectioninfo()
wifi_enable(enable=True)
wifi_scaninfo()
```
