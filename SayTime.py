#-*-coding:utf8;-*-

"""
Use termux-tts-speak to say current time in Chinese.
Requires termux_api
"""

import termux_api
import time

set_maxvol = True

def num_to_chinese(n):
    ch = u"零一二三四五六七八九十"
    try: n=int(n)
    except ValueError: raise ValueError("n should be an integer")
    if n<=10: return ch[n]
    elif n<20: #11-19
        return ch[10]+ch[n-10]
    elif n<100: #20-99
        if n%10==0:
            return ch[n//10]+ch[10]
        return ch[n//10]+ch[10]+ch[n%10] 
    else: raise ValueError("only integers < 100 are supported")

"""
for i in range(100):
    print(num_to_chinese(i).encode("utf-8"))
"""

def get_chinese_time(h, m):
    h %= 12
    if h == 0: h = 12

    if h == 2: res = u"兩"
    else: res = num_to_chinese(h)
    res += u"點"

    if m == 0: res += u"整"
    elif m == 30: res += u"半"
    else:
        if m < 10:
            res += u"零"
        res += num_to_chinese(m)+u"分"

    return res
    ## old, simple version
    #return "%s點 %s分" % (
    #    num_to_chinese(h), num_to_chinese(m))

"""
for h in range(12):
    for m in range(60):
        print(get_chinese_time(h, m).encode("utf-8"))
"""

def get_current_chinese_time():
    cur_time = time.localtime()
    h, m = cur_time.tm_hour, cur_time.tm_min
    return get_chinese_time(h, m)

to_speak = get_current_chinese_time()
print(to_speak)

if set_maxvol:
    vol = termux_api.volume_get()["music"]
    termux_api.volume_set("music", vol.max_volume)
try:
    print(termux_api.tts_speak(to_speak, timeout=20))
except Exception as err:
    print("Error occurred while TTS speaking:")
    print(err)
finally:
    termux_api.volume_set("music", vol.volume)


