#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import numpy as np
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import ImageFont
from mpd import MPDClient
import RPi.GPIO as GPIO
import socket
import subprocess

# --- Configuration OLED ---
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
font_path = "/usr/share/fonts/truetype/dejavu/"
fonts = {
    'tiny': ImageFont.truetype(os.path.join(font_path, 'DejaVuSansMono.ttf'), 8),
    'small': ImageFont.truetype(os.path.join(font_path, 'DejaVuSansMono.ttf'), 12),
    'medium': ImageFont.truetype(os.path.join(font_path, 'DejaVuSansMono.ttf'), 14),
    'large': ImageFont.truetype(os.path.join(font_path, 'DejaVuSansMono.ttf'), 18)
}

scroll_offset = 0
scroll_speed = 4

# --- Configuration GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUTTON_PLAY_PAUSE = 13
BUTTON_STOP = 16
BUTTON_NEXT_RADIO = 12
BUTTON_PREV_RADIO = 11
BUTTON_SHUTDOWN = 26

for pin in [BUTTON_PLAY_PAUSE, BUTTON_STOP, BUTTON_NEXT_RADIO, BUTTON_PREV_RADIO, BUTTON_SHUTDOWN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

radio_index = 0
radio_ids = []
last_radio_change_time = 0
last_status_change_time = 0
feedback_duration = 3
current_radio_name = ""
current_status_message = ""

# --- Message de bienvenue ---
def show_greeting():
    with canvas(device) as draw:
        draw.text((15, 20), "Bonjour", font=fonts['large'], fill="white")
    time.sleep(2)

# --- Load radios ---
def load_radio_favorites():
    global radio_ids
    client = MPDClient()
    client.connect("localhost", 6600)
    client.command_list_ok_begin()
    client.clear()
    client.load("RADIO")
    client.play(0)
    client.command_list_end()
    radio_ids = list(range(len(client.playlistinfo())))
    client.stop()
    client.close()
    client.disconnect()

# --- Get data ---
def get_moode_data():
    client = MPDClient()
    client.connect("localhost", 6600)
    status = client.status()
    current = client.currentsong()
    client.close()
    client.disconnect()
    return {
        "status": status.get('state', 'stop'),
        "volume": int(status.get('volume', 0)),
        "title": current.get('title', '(No Title)'),
        "artist": current.get('artist', ''),
        "name": current.get('name', ''),
        "audio": status.get('audio', ''),
        "bitrate": status.get('bitrate', ''),
        "duration": int(float(status.get('duration', 0))),
        "elapsed": int(float(status.get('elapsed', 0)))
    }

# --- Commandes ---
def mpd_command(cmd):
    global radio_index, current_radio_name, last_radio_change_time, current_status_message, last_status_change_time
    client = MPDClient()
    client.connect("localhost", 6600)
    if cmd == "toggle":
        if client.status().get("state") == "play":
            client.pause(1)
            current_status_message = "Pause"
        else:
            client.play()
            current_status_message = "Lecture"
        last_status_change_time = time.time()
    elif cmd == "stop":
        client.stop()
        current_status_message = "Arrêt"
        last_status_change_time = time.time()
    elif cmd == "next_radio":
        radio_index = (radio_index + 1) % len(radio_ids)
        client.play(radio_index)
        current_radio_name = client.currentsong().get('name', '(Unknown)')
        last_radio_change_time = time.time()
    elif cmd == "prev_radio":
        radio_index = (radio_index - 1) % len(radio_ids)
        client.play(radio_index)
        current_radio_name = client.currentsong().get('name', '(Unknown)')
        last_radio_change_time = time.time()
    client.close()
    client.disconnect()

# --- IP ---
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

# --- Affichage ---
def display_info(data, show_ip=False):
    global scroll_offset
    now = time.time()
    with canvas(device) as draw:
        if now - last_radio_change_time < feedback_duration:
            draw.text((0, 0), f"Radio: {current_radio_name}", font=fonts['large'], fill="white")
            return
        if now - last_status_change_time < feedback_duration:
            draw.text((0, 0), current_status_message, font=fonts['large'], fill="white")
            return

        is_radio = data['artist'] == '' and data['name'] != ''

        if is_radio:
            draw.text((0, 0), data['name'], font=fonts['large'], fill="white")
            scroll_text = f"{data['artist']} – {data['title']}"
            scroll_width = fonts['small'].getbbox(scroll_text)[2]
            scroll_offset = (scroll_offset + scroll_speed) % (scroll_width + 20)
            draw.text((-scroll_offset, 24), scroll_text, font=fonts['small'], fill="white")
        else:
            draw.text((0, 0), data['title'], font=fonts['large'], fill="white")
            draw.text((0, 26), data['artist'], font=fonts['small'], fill="white")

        draw.text((0, 44), {"play": "▶", "pause": "⏸", "stop": "■"}.get(data['status'], ""), font=fonts['large'], fill="white")
        if not is_radio:
            draw.text((100, 44), f"{data['elapsed']}s", font=fonts['medium'], fill="white")

        if data['bitrate'] or data['audio']:
            encoding = f"{data['bitrate']} kbps"
            w = fonts['medium'].getbbox(encoding)[2]
            draw.text(((device.width - w) // 2, 44), encoding, font=fonts['medium'], fill="white")

        if show_ip:
            draw.text((0, 68), get_ip(), font=fonts['tiny'], fill="white")

# --- GPIO callback ---
def button_callback(channel):
    if channel == BUTTON_PLAY_PAUSE:
        mpd_command("toggle")
    elif channel == BUTTON_STOP:
        mpd_command("stop")
    elif channel == BUTTON_NEXT_RADIO:
        mpd_command("next_radio")
    elif channel == BUTTON_PREV_RADIO:
        mpd_command("prev_radio")
    elif channel == BUTTON_SHUTDOWN:
        with canvas(device) as draw:
            draw.text((10, 30), "Extinction...", font=fonts['medium'], fill="white")
        time.sleep(2)
        subprocess.call(["sudo", "shutdown", "-h", "now"])

for pin in [BUTTON_PLAY_PAUSE, BUTTON_STOP, BUTTON_NEXT_RADIO, BUTTON_PREV_RADIO, BUTTON_SHUTDOWN]:
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_callback, bouncetime=500)

# --- Main loop ---
idle_counter = 0
show_ip = False
show_greeting()
load_radio_favorites()

try:
    while True:
        data = get_moode_data()
        display_info(data, show_ip)
        idle_counter = idle_counter + 1 if data['status'] != 'play' else 0
        device.hide() if idle_counter > 300 else device.show()
        time.sleep(1)
except KeyboardInterrupt:
    pass
except Exception as e:
    with canvas(device) as draw:
        draw.text((0, 0), f"Erreur: {str(e)}", font=fonts['tiny'], fill="white")
        time.sleep(5)
finally:
    GPIO.cleanup()
