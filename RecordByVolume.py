#-*-coding:utf-8;-*-
#py3
#termux

"""
Author: KirkSuD
Date: 2018-08-14
Last modified: 2019/08/26

A script to control microphone recorder
  through pressing volume button on Android using Termux.

Note: HIGH latency! Every call to termux-api requires 0.5sec to run.
"""

save_dir="Directory to save your recordings"
blank_media="Blank media path, its duration should be really long!"
file_name = "rec_%Y%m%d_%H%M%S.m4a"

encoder = "aac"
bitrate = 128
sample_rate = 44100
channel_count = 2

import termux_api

import time, os

def notfiy_error(s):
    termux_api.vibrate(5000, force=True)
    termux_api.toast("RecordByScreen.py - %s!" % s, position="bottom", text_color="red")

print("\nRecorder controlled by volume button")
print("Save at:", save_dir)
input("Press ENTER to start…")

print("Initializing...")

res = termux_api.media_player_play_file(blank_media)
if res.error is not None:
    print("media_player_play_file(blank_media) failed:\n", res)
    input("Run anyway? Press ENTER...")

res = termux_api.volume_set("music", 1)
if res.error is not None:
    print('volume_set("music", 1) failed:\n', res)
    input("Run anyway? Press ENTER...")

res = termux_api.microphone_record_info()
if res.error is not None:
    print("microphone_record_info() failed:\n", res)
try:
    recording = res.result["isRecording"]
except:
    print('Error getting "isRecording":\n', res)
    recording = False

print("\n Is recording:", recording)

print(" Waiting…")
st=0
while True:
    try:
        ## time.sleep(check_time) ## no need
        res = termux_api.volume_get() ## slow, >0.5s
        ## print(time.time()-st)
        ## st = time.time() ## see the delay
        try:
            vol = res.result["music"].volume
        except:
            print("Failed to get volume:\n", res)
            notify_error("failed to get volume")
            continue
        if vol != 1:
            ## print("Volume button pressed.")
            if recording:
                termux_api.vibrate(200, force=True)
                ## time.sleep(0.4) ## no need, termux-api is REALLY slow!
                termux_api.vibrate(200, force=True)
                res = termux_api.microphone_record_quit()
                if res.error is None:
                    recording = False
                    print(" Stopped, waiting…")
                else:
                    print("Error stopping record:\n", res)
                    notify_error("error stopping record")
            else:
                termux_api.vibrate(600, force=True)
                name = time.strftime(file_name)
                record_file = os.path.join(save_dir, name)
                res = termux_api.microphone_record(record_file, limit = 0, encoder = encoder,
                    bitrate = bitrate, sample_rate = sample_rate, channel_count = channel_count)
                if res.error is None:
                    recording=True
                    print("\n Recording %s..." % name)
                else:
                    print("Error starting record:\n", res)
                    notify_error("error starting record")
            res = termux_api.volume_set("music", 1)
            if res.error is not None:
                print('volume_set("music", 1) failed:\n', res)
                notify_error("error setting music volume")
                input("Continue anyway? Press ENTER...")
    except KeyboardInterrupt:
        print("\n Got KeyboardInterrupt, quit playing and exit...")
        res = termux_api.media_player_stop()
        if res.error is not None:
            print('media_player_stop() failed:\n', res)
        print(" Good bye ~")
        raise SystemExit
