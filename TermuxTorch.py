#-*-coding:utf8;-*-

import subprocess, time

on_sec = 0.8
off_sec = 0.5
while True:
    try:
        subprocess.check_call(["termux-torch","on"])
        print("\r On  ", end="")
        time.sleep(on_sec)
        subprocess.check_call(["termux-torch","off"])
        print("\r Off ", end="")
        time.sleep(off_sec)
    except KeyboardInterrupt:
        subprocess.check_call(["termux-torch","off"])
        print("\r Closed")
        time.sleep(1)
        raise SystemExit
    except Exception as err:
        print("\n\nError:")
        print(err)
        print()

