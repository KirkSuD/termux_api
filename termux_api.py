"""
termux_api.py - call termux-api by subprocess

Official wiki: https://wiki.termux.com/wiki/Termux:API
"""

from __future__ import annotations

import atexit
import json
import re
import subprocess
from json import JSONDecodeError
from subprocess import CalledProcessError
from typing import Any, Optional

_all_popen = []


def _kill_all_popen():
    for popen in _all_popen:
        popen.kill()


atexit.register(_kill_all_popen)


def _run(args, **kwargs) -> tuple[Optional[str], Optional[CalledProcessError]]:
    args = [str(i) for i in args]
    try:
        proc = subprocess.run(
            args, capture_output=True, check=True, text=True, **kwargs
        )
        return proc.stdout, None
    except CalledProcessError as err:
        return None, err


def _run_json(
    args, **kwargs
) -> tuple[Any, Optional[CalledProcessError | JSONDecodeError]]:
    stdout, err = _run(args, **kwargs)
    if err:
        return None, err
    try:
        return json.loads(stdout), None
    except JSONDecodeError as err:
        return None, err


def _run_error(args, **kwargs) -> tuple[None, Optional[CalledProcessError | str]]:
    stdout, err = _run(args, **kwargs)
    if err:
        return None, err
    if stdout.strip():
        return None, stdout
    else:
        return None, None


def _run_startswith_error(
    args, startswith, is_error=False, **kwargs
) -> tuple[None, Optional[CalledProcessError | str]]:
    stdout, err = _run(args, **kwargs)
    if err:
        return None, err
    if stdout.startswith(startswith) == is_error:
        return None, stdout
    else:
        return None, None


def _run_startswith_map(
    args, mapping, default=None, **kwargs
) -> tuple[Optional[Any], Optional[CalledProcessError]]:
    stdout, err = _run(args, **kwargs)
    if err:
        return None, err
    for k, v in mapping.items():
        if stdout.startswith(k):
            return v, None
    return default, None


def _run_regex(
    args, regex, types, **kwargs
) -> tuple[Optional[Any], Optional[CalledProcessError]]:
    stdout, err = _run(args, **kwargs)
    if err:
        return None, err
    m = re.match(regex, stdout)
    if m is None:
        return None, None
    if type(types) is list:
        return [t(g) for t, g in zip(types, m.groups())], None
    else:
        return types(m.groups()[0]), None


def _run_updates(args, **kwargs):
    args = [str(i) for i in args]
    popen = subprocess.Popen(
        args, bufsize=1, stdout=subprocess.PIPE, text=True, **kwargs
    )
    _all_popen.append(popen)
    buffer = ""
    for line in iter(popen.stdout.readline, ""):
        buffer += line
        try:
            yield json.loads(buffer), None
            buffer = ""
        except JSONDecodeError:
            pass
    popen.stdout.close()
    return_code = popen.wait()
    _all_popen.remove(popen)
    if return_code:
        yield None, CalledProcessError(return_code, args)


def _construct_args(command: list[str], flags={}, kwargs={}, args=[]):
    res = command
    for k, v in flags.items():
        if v:
            res.append(k)
    for k, v in kwargs.items():
        if v is None:
            continue
        res.append(k)
        if v is True:
            res.append("true")
        elif v is False:
            res.append("false")
        else:
            res.append(v)
    res.extend(args)
    return res


def _join_list(lis):
    if lis is None:
        return None
    return ",".join(str(i) for i in lis)


def battery_status():
    return _run_json(["termux-battery-status"])


def brightness(brightness):
    """brightness: 0-255 or auto, require android.permission.WRITE_SETTINGS"""
    return _run_error(["termux-brightness", brightness])


def call_log(offset=0, limit=10):
    """not working on some devices even when permission is granted"""
    return _run_json(["termux-call-log", "-o", offset, "-l", limit])


def camera_info():
    return _run_json(["termux-camera-info"])


def camera_photo(output_file, camera_id=0):
    return _run_error(["termux-camera-photo", "-c", camera_id, output_file])


def clipboard_get():
    return _run(["termux-clipboard-get"])


def clipboard_set(text):
    return _run_error(["termux-clipboard-set", text])


def contact_list():
    return _run_json(["termux-contact-list"])


def dialog_list():
    return _run(["termux-dialog", "-l"])


def dialog_confirm(title=None, hint=None):
    args = _construct_args(["termux-dialog", "confirm"], {}, {"-t": title, "-i": hint})
    return _run_json(args)


def dialog_checkbox(title=None, values=[]):
    args = _construct_args(
        ["termux-dialog", "checkbox"], {}, {"-t": title, "-v": _join_list(values)}
    )
    return _run_json(args)


def dialog_counter(title=None, range=None):
    """range: [min, max, start]"""
    args = _construct_args(
        ["termux-dialog", "counter"], {}, {"-t": title, "-r": _join_list(range)}
    )
    return _run_json(args)


def dialog_date(title=None, date_format=None):
    """date_format: output SimpleDateFormat pattern, e.g. dd-MM-yyyy k:m:s"""
    args = _construct_args(
        ["termux-dialog", "date"], {}, {"-t": title, "-d": date_format}
    )
    return _run_json(args)


def dialog_radio(title=None, values=[]):
    args = _construct_args(
        ["termux-dialog", "radio"], {}, {"-t": title, "-v": _join_list(values)}
    )
    return _run_json(args)


def dialog_sheet(title=None, values=[]):
    args = _construct_args(
        ["termux-dialog", "sheet"], {}, {"-t": title, "-v": _join_list(values)}
    )
    return _run_json(args)


def dialog_spinner(title=None, values=[]):
    args = _construct_args(
        ["termux-dialog", "spinner"], {}, {"-t": title, "-v": _join_list(values)}
    )
    return _run_json(args)


def dialog_speech(title=None, hint=None):
    args = _construct_args(["termux-dialog", "speech"], {}, {"-t": title, "-i": hint})
    return _run_json(args)


def dialog_text(title=None, hint=None, multi_line=False, number=False, password=False):
    args = _construct_args(
        ["termux-dialog", "text"],
        {"-m": multi_line, "-n": number, "-p": password},
        {"-t": title, "-i": hint},
    )
    return _run_json(args)


def dialog_time(title=None):
    args = _construct_args(["termux-dialog", "time"], {}, {"-t": title})
    return _run_json(args)


def download(url, path=None, title=None, description=None):
    args = _construct_args(
        ["termux-download"], {}, {"-p": path, "-t": title, "-d": description}, [url]
    )
    return _run_error(args)


def fingerprint():
    return _run_json(["termux-fingerprint"])


def infrared_frequencies():
    return _run_json(["termux-infrared-frequencies"])


def infrared_transmit(frequency, pattern):
    return _run_error(
        ["termux-infrared-transmit", "-f", frequency, _join_list(pattern)]
    )


def job_scheduler_list():
    return _run(["termux-job-scheduler", "-p"])


def job_scheduler_cancel(job_id=None):
    return _run(["termux-job-scheduler", "--cancel", job_id])


def job_scheduler_cancel_all():
    return _run(["termux-job-scheduler", "--cancel-all"])


def job_scheduler(
    script_path,
    job_id=None,
    period_ms=0,
    network="any",
    battery_not_low=True,
    storage_not_low=False,
    charging=False,
    persisted=False,
    trigger_content_uri=None,
    trigger_content_flag=1,
):
    """refer to: `termux-job-scheduler -h`"""
    args = _construct_args(
        ["termux-job-scheduler"],
        {},
        {
            "-s": script_path,
            "--job-id": job_id,
            "--period-ms": period_ms,
            "--network": network,
            "--battery-not-low": battery_not_low,
            "--storage-not-low": storage_not_low,
            "--charging": charging,
            "--persisted": persisted,
            "--trigger-content-uri": trigger_content_uri,
            "--trigger-content-flag": trigger_content_flag,
        },
    )
    return _run(args)


def location(provider="gps", request="once"):
    """provider: gps/network/passive, request: once/last/updates"""
    args = ["termux-location", "-p", provider, "-r", request]
    if request == "updates":
        return _run_updates(args)
    return _run_json(args)


def media_player_info():
    """return {"Track": None} or {Status, Track, Current Position}"""
    res, err = _run(["termux-media-player", "info"])
    if err:
        return None, err
    if res.startswith("No track currently"):
        return {"Track": None}, None
    res = dict(
        [line.split(": ", maxsplit=1) for line in res.split("\n") if ":" in line]
    )
    return res, None


def media_player_play(file):
    args = ["termux-media-player", "play", file]
    return _run_startswith_error(args, "Now Playing")


def media_player_pause():
    return _run_startswith_map(
        ["termux-media-player", "pause"],
        {
            "Paused playback": True,
            "Playback already paused": None,
            "No track to pause": False,
        },
    )


def media_player_resume():
    return _run_startswith_map(
        ["termux-media-player", "play"],
        {
            "Resumed playback": True,
            "Already playing track": None,
            "No previous track to resume": False,
        },
    )


def media_player_stop():
    return _run_startswith_map(
        ["termux-media-player", "stop"],
        {
            "Stopped playback": True,
            "No track to stop": False,
        },
    )


def media_scan(files, recursive=False, verbose=False):
    """verbose makes no difference"""
    # -v just prints all files out, including non-media files
    args = _construct_args(
        ["termux-media-scan"], {"-r": recursive, "-v": verbose}, {}, files
    )
    return _run_regex(args, "Finished scanning ([0-9]+) file", int)


def microphone_record(
    file=None,
    limit=None,
    encoder=None,
    bitrate=None,
    sample_rate=None,
    channel_count=None,
    default=False,
):
    """
    default encoding is device specific.
    default limit is 15min.
    default file is /sdcard/TermuxAudioRecording_yyyy-MM-dd_HH-mm-ss.<extension>
    """
    args = _construct_args(
        ["termux-microphone-record"],
        {"-d": default},
        {
            "-f": file,
            "-l": limit,
            "-e": encoder,
            "-b": bitrate,
            "-r": sample_rate,
            "-c": channel_count,
        },
    )
    return _run_startswith_error(args, "Recording started")


def microphone_record_info():
    return _run_json(["termux-microphone-record", "-i"])


def microphone_record_quit():
    return _run_startswith_map(
        ["termux-microphone-record", "-q"],
        {"Recording finished": True, "No recording to stop": False},
    )


def notification(
    title=None,
    content=None,
    button1=None,
    button2=None,
    button3=None,
    image=None,
    sound=False,
    vibrate=None,
    led_color=None,
    led_off=None,
    led_on=None,
    alert_once=False,
    pin=False,
    priority=None,
    id=None,
    group=None,
    type=None,
    action=None,
    button1_action=None,
    button2_action=None,
    button3_action=None,
    delete_action=None,
    media_next=None,
    media_pause=None,
    media_play=None,
    media_previous=None,
):
    """refer to the official wiki: https://wiki.termux.com/wiki/Termux-notification"""
    args = _construct_args(
        ["termux-notification"],
        {"--alert-once": alert_once, "--ongoing": pin, "--sound": sound},
        {
            "--action": action,
            "--button1": button1,
            "--button1-action": button1_action,
            "--button2": button2,
            "--button2-action": button2_action,
            "--button3": button3,
            "--button3-action": button3_action,
            "--content": content,
            "--group": group,
            "--id": id,
            "--image-path": image,
            "--led-color": led_color,
            "--led-off": led_off,
            "--led-on": led_on,
            "--on-delete": delete_action,
            "--priority": priority,
            "--title": title,
            "--vibrate": _join_list(vibrate),
            "--type": type,
            "--media-next": media_next,
            "--media-pause": media_pause,
            "--media-play": media_play,
            "--media-previous": media_previous,
        },
    )
    return _run_error(args)


def notification_remove(id):
    return _run_error(["termux-notification-remove", id])


def sensor(sensors=None, delay=None, times=None):
    args = ["termux-sensor"]
    if sensors is None:
        args.append("-a")
    else:
        args.append("-s")
        args.append(_join_list(sensors))
    args = _construct_args(args, {}, {"-d": delay, "-n": times})
    return _run_updates(args)


def sensor_cleanup():
    """clean up running sensor listeners"""
    return _run_startswith_map(
        ["termux-sensor", "-c"],
        {
            "Sensor cleanup successful": True,
            "Sensor cleanup unnecessary": False,
        },
    )


def sensor_list():
    return _run_json(["termux-sensor", "-l"])


def sensor_once(sensors=None):
    if sensors is None:
        return _run_json(["termux-sensor", "-a", "-n", 1])
    return _run_json(["termux-sensor", "-s", _join_list(sensors), "-n", 1])


def share(file, action=None, content_type=None, default_receiver=False, title=None):
    """action: edit/send/view"""
    args = _construct_args(
        ["termux-share"],
        {"-d": default_receiver},
        {"-a": action, "-c": content_type, "-t": title},
        [file],
    )
    return _run_error(args)


def sms_list(
    offset=0, limit=10, show_date=False, show_number=False, message_type="inbox"
):
    """message_type: all|inbox|sent|draft|outbox"""
    args = _construct_args(
        ["termux-sms-list"],
        {"-d": show_date, "-n": show_number},
        {"-l": limit, "-o": offset, "-t": message_type},
    )
    return _run_json(args)


def sms_send(text, numbers, sim_slot=None):
    """not tested"""
    args = _construct_args(
        ["termux-sms-send"], {}, {"-n": _join_list(numbers), "-s": sim_slot}, [text]
    )
    return _run_error(args)


def storage_get(output_file):
    return _run_error(["termux-storage-get", output_file])


def telephony_call(number):
    """not tested"""
    return _run_error(["termux-telephony-call", number])


def telephony_cellinfo():
    return _run_json(["termux-telephony-cellinfo"])


def telephony_deviceinfo():
    return _run_json(["termux-telephony-deviceinfo"])


def toast(
    text, position="middle", short=False, text_color="white", background_color="gray"
):
    """position: top/middle/bottom"""
    args = _construct_args(
        ["termux-toast"],
        {"-s": short},
        {"-g": position, "-c": text_color, "-b": background_color},
        [text],
    )
    return _run_error(args)


def torch(on=True):
    return _run_error(["termux-torch", "on" if on else "off"])


def tts_engines():
    return _run_json(["termux-tts-engines"])


def tts_speak(
    text,
    engine=None,
    language=None,
    region=None,
    variant=None,
    pitch=None,
    rate=None,
    stream=None,
    timeout=None,
):
    """stream: ALARM, MUSIC, NOTIFICATION, RING, SYSTEM, VOICE_CALL"""
    args = _construct_args(
        ["termux-tts-speak"],
        {},
        {
            "-e": engine,
            "-l": language,
            "-n": region,
            "-v": variant,
            "-p": pitch,
            "-r": rate,
            "-s": stream,
        },
        [text],
    )
    return _run_error(args, timeout=timeout)


def tts_speak_init(
    engine=None,
    language=None,
    region=None,
    variant=None,
    pitch=None,
    rate=None,
    stream=None,
):
    """return functions: speak(text), close()"""
    args = _construct_args(
        ["termux-tts-speak"],
        {},
        {
            "-e": engine,
            "-l": language,
            "-n": region,
            "-v": variant,
            "-p": pitch,
            "-r": rate,
            "-s": stream,
        },
    )
    args = [str(i) for i in args]
    popen = subprocess.Popen(args, bufsize=1, stdin=subprocess.PIPE, text=True)
    _all_popen.append(popen)

    def speak(text: str):
        popen.stdin.write(text + "\n")
        return None, None

    def close():
        popen.stdin.close()
        return_code = popen.wait()
        _all_popen.remove(popen)
        if return_code:
            return None, CalledProcessError(return_code, args)
        return None, None

    return speak, close


def usb(device, permission_dialog=False, execute_command=None):
    """not tested"""
    args = _construct_args(
        ["termux-usb"], {"-r": permission_dialog}, {"-e": execute_command}, [device]
    )
    return _run_error(args)


def usb_list():
    return _run_json(["termux-usb", "-l"])


def vibrate(duration=None, force=False):
    args = _construct_args(["termux-vibrate"], {"-f": force}, {"-d": duration})
    return _run_error(args)


def volume_get():
    return _run_json(["termux-volume"])


def volume_set(stream, volume):
    return _run_error(["termux-volume", stream, volume])


def wallpaper(file=None, url=None, lockscreen=False):
    """not tested"""
    args = _construct_args(
        ["termux-wallpaper"], {"-l": lockscreen}, {"-f": file, "-u": url}
    )
    return _run_error(args)


def wifi_connectioninfo():
    return _run_json(["termux-wifi-connectioninfo"])


def wifi_enable(enable=True):
    """not working on some devices"""
    return _run_error(["termux-wifi-enable", "true" if enable else "false"])


def wifi_scaninfo():
    return _run_json(["termux-wifi-scaninfo"])


if __name__ == "__main__":

    def run_tests(tests, wait_enter=True):
        for test in tests:
            func, args, kwargs = test[0], [], {}
            if len(test) > 1:
                args = test[1]
            if len(test) > 2:
                kwargs = test[2]
            print()
            print("Test", func.__name__, args, kwargs)
            if wait_enter:
                if input("Press enter...") != "":
                    print("Skipped.")
                    continue
            res, err = func(*args, **kwargs)
            if err:
                print("Error:", err)
            else:
                print("Result:", res)

    def test_sensor(delay=1000, times=5, wait_enter=True):
        print()
        print(f"sensor {delay=} {times=}")
        if wait_enter:
            input("Press enter...")
        for res, err in sensor(delay=delay, times=times):
            if err:
                print("Error:", err)
            else:
                print("Result:", res)

    def test_tts_speak(wait_enter=True):
        print()
        print("tts_speak_init")
        if wait_enter:
            input("Press enter...")
        speak, close = tts_speak_init()
        while text := input("speak: ").strip():
            _, err = speak(text)
            if err:
                print("Error:", err)
        _, err = close()
        if err:
            print("Error:", err)

    test_dir = "/sdcard/Download/termux_api_test/"
    in_script = "/data/data/com.termux/files/home/termux-toast-hello.sh"
    in_audio = test_dir + "in.ogg"
    # in_image = test_dir + "in.jpg"
    in_text = test_dir + "in.txt"
    out_html = test_dir + "out.html"
    out_audio = test_dir + "out.m4a"
    out_image = test_dir + "out.jpg"
    out_text = test_dir + "out.txt"
    tests = [
        [battery_status],
        [brightness, [128]],
        [call_log],
        [camera_info],
        [camera_photo, [out_image]],
        [clipboard_set, ["test"]],
        [clipboard_get],
        [contact_list],
        [dialog_checkbox, ["title", ["value 1", "value 2"]]],
        [download, ["https://google.com", out_html, "title", "desc"]],
        [fingerprint],
        [infrared_frequencies],
        [infrared_transmit, [40000, [20, 50, 20, 30]]],
        [job_scheduler, [in_script]],
        [location, ["network"]],
        [media_player_play, [in_audio]],
        [media_player_info],
        [media_player_pause],
        [media_player_stop],
        [media_scan, [[in_audio]]],
        [microphone_record, [out_audio, 10, "aac", 128, 44100, 2]],
        [microphone_record_info],
        [microphone_record_quit],
        [notification, ["title", "content"], {"id": "termux_api_test"}],
        [notification_remove, ["termux_api_test"]],
        [sensor_list],
        [sensor_once],
        # [sensor],  # test alone
        [share, [in_text]],
        [sms_list],
        # [sms_send, ["Hello", ["123"]]],
        [storage_get, [out_text]],
        # [telephony_call, ["123"]],
        [telephony_cellinfo],
        [telephony_deviceinfo],
        [toast, ["hello"]],
        [torch],
        [torch, [False]],
        [tts_engines],
        [tts_speak, ["hello"], {"timeout": 20}],
        # [tts_speak_init],  # test alone
        [usb_list],
        # [usb, ["/dev/bus/usb/xxx/xxx"]],
        [vibrate],
        [volume_get],
        [volume_set, ["music", 0]],
        # [wallpaper, [in_image]],
        [wifi_connectioninfo],
        [wifi_enable],
        [wifi_enable, [False]],
        [wifi_scaninfo],
    ]
    run_tests(tests)
    test_sensor()
    test_tts_speak()
