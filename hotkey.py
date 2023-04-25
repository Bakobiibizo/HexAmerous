import pyautogui
import time
import keyboard
import pyperclip

def send_clipboard_content():
    content = pyperclip.paste()
    pyautogui.typewrite(content)

HOTKEY = 'ctrl+alt+v'
print(f"Hotkey: {HOTKEY}")

while True:
    try:
        if keyboard.is_pressed(HOTKEY):
            time.sleep(0.5)
            send_clipboard_content()
            time.sleep(0.5)
        time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting the script")
        break