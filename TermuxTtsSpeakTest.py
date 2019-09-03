#-*-coding:utf8;-*-

"""
Test termux-tts-speak
"""

import subprocess

def tts_speak(s):
    return subprocess.call(["termux-tts-speak", s])

for h in range(1,13):
    for m in range(60):
        tospeak = "%d:%02d"%(h,m)
        print(tospeak)
        tts_speak(tospeak)
