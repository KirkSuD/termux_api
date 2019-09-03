#-*-coding:utf8;-*-
#py3
#termux

"""
termux_api.py - Use subprocess to call termux-api

Official wiki: https://wiki.termux.com/wiki/Termux:API

First date: 19/08/13
Last modified: 19/08/26

Try to make a clean, exception-free module for calling termux-api.
Every call would return termux_api_result(result, error),
  please check error is None after every call,
  result is None if it is not a query API.

TODO:
  make the code cleaner
  improve the way of detecting errors
  improve tts_speak()
  improve media_player_...()
  improve microphone_record_...()
  support more APIs?
  check quotes?
  test

APIs with problems:
tts_speak(s, timeout = None) ## options not fully supported, problematic(crash when run multiple)
media_player_...()
microphone_record_...()

Skipped APIs:
termux-call-log ## android >= 9 {"error": "Call log is no longer permitted by Google"}
termux-dialog ## complex
termux-download ## weird, still need testing
termux-job-scheduler ## not on wiki
termux-notification ## complex
termux-notification-remove
termux-sensor ## complex
termux-sms-list ## {"error": "Reading SMS is no longer permitted by Google"}
termux-sms-send ## {"error": "Sending SMS is no longer permitted by Google"}
termux-storage-get ## not understood? ## what does this do?
termux-wallpaper ## not tested, lazy now, i don't(and probably won't) use this

API list:
battery_status()
brightness(brightness)
camera_info()
camera_photo(savepath, camera_id = 0)
clipboard_get()
clipboard_set(s)
contact_list()
fingerprint()
infrared_frequencies()
infrared_transmit(freq, pattern) ## freq: frequency, pattern: a list of numbers
location(provider="gps", request="once") ## provider: [gps/network/passive] ## request: [once/last/updates]
media_player_info()
media_player_play()
media_player_play_file(file)
media_player_pause()
media_player_stop()
media_scan(files, recursive = False, verbose = False) ## not tested ## return plain text
microphone_record(file = None, limit = None, encoder = None, bitrate = None, sample_rate = None, channel_count = None, default = False)
microphone_record_info()
microphone_record_quit()
share(file, action = None, content_type = None, share_to_default_receiver = False, title = None) ## None -> use default
telephony_call(number)
telephony_cellinfo()
telephony_deviceinfo()
toast(s, short = False, position = None, text_color = None, background_color = None) ## position: [top, middle, or bottom] (default: middle)
torch(on = True)
tts_engines()
tts_speak(s, timeout = None) ## not fully supported, problematic
vibrate(duration = None, force = False) ## duration: default: 1000(ms)
volume_get()
volume_set(stream, volume)
wifi_connectioninfo()
wifi_enable(enable = True)
wifi_scaninfo()
"""

import subprocess
import json ## to parse returned json from volume_get
from collections import namedtuple ## to return pretty data

TermuxApiResult = namedtuple("termux_api_result", "result error")

def _stdout_err(args, **kwargs):
    ## print("_stdout_err args:", args) ## debug
    proc = subprocess.run(args, capture_output = True, **kwargs)
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError as err:
        return proc.stdout if proc.stdout else None, err
    return proc.stdout if proc.stdout else None, None
    
def _run_err(args, **kwargs):
    stdout, err = _stdout_err(args, **kwargs)
    if err is not None: return TermuxApiResult(stdout, err)
    return TermuxApiResult(None, stdout if stdout and stdout != b'\n' else None)
    ## termux-wifi-enable prints b'\n'

def _run_plain(args):
    stdout, err = _stdout_err(args)
    if err is not None: return TermuxApiResult(stdout, err)
    return TermuxApiResult(stdout.decode("utf-8") if stdout else None, None)

def _run_json(args):
    stdout, err = _stdout_err(args)
    if err is not None: return TermuxApiResult(stdout, err) 
    try:
        return TermuxApiResult(json.loads(stdout), None)
    except Exception as err:
        return TermuxApiResult(stdout, err)

def battery_status():
    return _run_json(["termux-battery-status"])

def brightness(brightness):
    return _run_err(["termux-brightness", str(brightness)])

def camera_info():
    return _run_json(["termux-camera-info"])

def camera_photo(savepath, camera_id = 0):
    return _run_err(["termux-camera-photo", "-c", str(camera_id), str(savepath)])

def clipboard_get():
    try:
        proc = subprocess.run(["termux-clipboard-get"], capture_output = True, check = True)
    except Exception as err:
        return TermuxApiResult(None, err)
    return TermuxApiResult(proc.stdout, None)

def clipboard_set(s):
    return _run_err(["termux-clipboard-set", str(s)])

def contact_list():
    return _run_json(["termux-contact-list"])

def fingerprint():
    return _run_json(["termux-fingerprint"])

def infrared_frequencies():
    return _run_json(["termux-infrared-frequencies"])

def infrared_transmit(freq, pattern):
    return _run_err(["termux-infrared-transmit", "-f", str(freq),
                     ",".join(str(i) for i in pattern)])

def location(provider="gps", request="once"):
    return _run_json(["termux-location", "-p", provider, "-r", request])


"""
info        Displays current playback information
play        Resumes playback if paused
play <file> Plays specified media file
pause       Pauses playback
stop        Quits playback
"""
def media_player_info():
    res, err = _run_plain(["termux-media-player", "info"])
    if err is not None:
        return TermuxApiResult(res, err)
    if res == "No track currently!\n":
        return TermuxApiResult({"Track": None}, None)
    res = [i.split(":", maxsplit=1) for i in res.split("\n") if ":" in i]
    return TermuxApiResult({i:j for i, j in res}, None)
"""
def media_player_info():
    return _run_plain(["termux-media-player", "info"])
"""
def media_player_play():
    return _run_plain(["termux-media-player", "play"])
def media_player_play_file(file):
    return _run_plain(["termux-media-player", "play", str(file)])
def media_player_pause():
    return _run_plain(["termux-media-player", "pause"])
def media_player_stop():
    return _run_plain(["termux-media-player", "stop"])


def media_scan(files, recursive = False, verbose = False):
    args = ["termux-media-scan"]
    if recursive: args.append("-r")
    if verbose: args.append("-v")
    for f in files: args.append("'%s'" % f)
    return _run_plain(args)


"""
## termux/termux-api/app/src/main/java/com/termux/api/MicRecorderAPI.java
## default is device specific: https://stackoverflow.com/questions/5144713/what-is-mediarecorder-outputformat-default
## default limit is 15min set by termux
## default file is /sdcard/TermuxAudioRecording_yyyy-MM-dd_HH-mm-ss.<extension> set by termux

-d           Start recording w/ defaults
-f <file>    Start recording to specific file
-l <limit>   Start recording w/ specified limit (in seconds, unlimited for 0)
-e <encoder> Start recording w/ specified encoder (aac, amr_wb, amr_nb)
-b <bitrate> Start recording w/ specified bitrate (in kbps)
-r <rate>    Start recording w/ specified sampling rate (in Hz)
-c <count>   Start recording w/ specified channel count (1, 2, ...)
-i           Get info about current recording
-q           Quits recording
"""
def microphone_record(file = None, limit = None, encoder = None, bitrate = None, sample_rate = None, channel_count = None, default = False):
    args = ["termux-microphone-record"]
    if default: args.append("-d")
    opts = [(file, "-f"), (limit, "-l"), (encoder, "-e"), (bitrate, "-b"), (sample_rate, "-r"), (channel_count, "-c")]
    for i, j in opts:
        if i is not None:
            args.append(j)
            args.append(str(i))
    return _run_plain(args)
def microphone_record_info():
    return _run_json(["termux-microphone-record", "-i"])
def microphone_record_quit():
    return _run_plain(["termux-microphone-record", "-q"])
 
def share(file, action = None, content_type = None, share_to_default_receiver = False, title = None):
    args = ["termux-share"]
    if action is not None:
        args.append("-a")
        args.append(action)
    if content_type is not None:
        args.append("-c")
        args.append(content_type)
    if share_to_default_receiver:
        args.append("-d")
    if title is not None:
        args.append("-t")
        args.append(title)
    
def telephony_call(number):
    return _run_err(["termux-telephony-call", str(number)])

def telephony_cellinfo():
    return _run_json(["termux-telephony-cellinfo"])

def telephony_deviceinfo():
    return _run_json(["termux-telephony-deviceinfo"])

def toast(s, position = None, short = False, text_color = None, background_color = None):
    args = ["termux-toast"]
    if short: args.append("-s")
    if position is not None:
        args.append("-g")
        args.append(position)
    if text_color is not None:
        args.append("-c")
        args.append(text_color)
    if background_color is not None:
        args.append("-b")
        args.append(background_color)
    args.append(str(s))
    return _run_err(args)

def torch(on = True):
    return _run_err(["termux-torch", "on" if on else "off"])

def tts_engines():
    return _run_json(["termux-tts-engines"])

def tts_speak(s, timeout = None):
    return _run_err(["termux-tts-speak", str(s)], timeout = timeout)

def vibrate(duration = None, force = False):
    args = ["termux-vibrate"]
    if duration is not None:
        args.append("-d")
        args.append(str(duration))
    if force: args.append("-f")
    return _run_err(args)

def volume_get():
    stream_volume = namedtuple("stream_volume", "volume max_volume")
    try:
        proc = subprocess.run(["termux-volume"], capture_output = True, check = True)
        vols = json.loads(proc.stdout)
        res = {}
        for vol in vols:
            res[vol["stream"]] = stream_volume(vol["volume"], vol["max_volume"])
        return TermuxApiResult(res, None)
    except Exception as err:
        return TermuxApiResult(None, err)

def volume_set(stream, volume):
    return _run_err(["termux-volume", stream, str(volume)])

def wifi_connectioninfo():
    return _run_json(["termux-wifi-connectioninfo"])

def wifi_enable(enable = True):
    return _run_err(["termux-wifi-enable", "true" if enable else "false"])

def wifi_scaninfo():
    return _run_json(["termux-wifi-scaninfo"])

if __name__ == "__main__":
    ## test or debug

    print("\nbattery_status():")
    print(battery_status())

    ## brightness(brightness)

    print("\ncamera_info():")
    print(camera_info())

    ## camera_photo(savepath, camera_id = 0)

    print("\nclipboard_get():")
    print(clipboard_get())

    ## clipboard_set(s)

    print("\ncontact_list():")
    print(contact_list())

    # print("\nfingerprint():")
    # print(fingerprint())
    ## not working?

    print("\ninfrared_frequencies():")
    print(infrared_frequencies())

    ## infrared_transmit(freq, pattern) ## freq: frequency, pattern: a list of numbers

    print('\nlocation(provider="network", request="once"):')
    print(location(provider="network", request="once"))

    print("\nmedia_player_info():")
    print(media_player_info())

    print("\nmedia_player_play():")
    print(media_player_play())

    ## media_player_play_file(file)

    print("\nmedia_player_pause():")
    print(media_player_pause())

    print("\nmedia_player_stop():")
    print(media_player_stop())

    ## media_scan(files, recursive = False, verbose = False) ## not tested ## return plain text

    ## microphone_record(file = None, limit = None, encoder = None, bitrate = None, sample_rate = None, channel_count = None, default = False)

    print("\nmicrophone_record_info():")
    print(microphone_record_info())

    print("\nmicrophone_record_quit():")
    print(microphone_record_quit())

    ## share(file, action = None, content_type = None, share_to_default_receiver = False, title = None) ## None -> use default

    ## telephony_call(number)

    print("\ntelephony_cellinfo():")
    print(telephony_cellinfo())

    print("\ntelephony_deviceinfo():")
    print(telephony_deviceinfo())

    print('\ntoast("hello", short = True, position = "bottom", text_color = "black", background_color = "white"):')
    print(toast("hello", short = True, position = "bottom", text_color = "black", background_color = "white"))

    print("\ntorch(on = True):")
    print(torch(on = True))
    print("\ntorch(on = False):")
    print(torch(on = False))

    print("\ntts_engines():")
    print(tts_engines())

    print('\ntts_speak("hello", timeout = 10):')
    print(tts_speak("hello", timeout = 10))

    print("\nvibrate(duration = None, force = False):")
    print(vibrate(duration = None, force = False)) ## duration: default: 1000(ms)

    print("\nvol = volume_get():")
    vol = volume_get()
    print(vol)

    print('\nvolume_set("music", vol["music"].volume + 1):')
    print(volume_set("music", vol.result["music"].volume + 1))

    print("\nwifi_connectioninfo():")
    print(wifi_connectioninfo())

    print("\nwifi_enable(enable = True):")
    print(wifi_enable(enable = True))

    print("\nwifi_enable(enable = False):")
    print(wifi_enable(enable = False))

    print("\nwifi_scaninfo():")
    print(wifi_scaninfo())





