import os
import sys
import json
import requests
from pynput import keyboard
from pygame import mixer
from pystray import Icon, Menu, MenuItem
from PIL import Image
import threading
from plyer import notification
import webbrowser
import atexit

# Paths
APPDATA_PATH = os.path.join(os.getenv('APPDATA'), 'keyboard-sounds')
SOUNDS_PATH = os.path.join(APPDATA_PATH, 'sounds')
CONFIG_PATH = os.path.join(APPDATA_PATH, 'config.json')
ICON_URL = 'https://github.com/RuskyDev/keyboard-sounds/raw/refs/heads/main/setup/icon.ico'
ICON_FILE = os.path.join(APPDATA_PATH, 'icon.ico')
DEFAULT_SOUND_URL = 'https://github.com/RuskyDev/keyboard-sounds/raw/refs/heads/main/setup/default.mp3'
DEFAULT_SOUND_FILE = os.path.join(SOUNDS_PATH, 'default.mp3')
LOCK_FILE = os.path.join(APPDATA_PATH, 'app.lock')

# Global variables
IS_ENABLED = True
VOLUME_LEVEL = 0.5
TRAY_ICON = None
SOUND = None
VERSION = "1.2"

def CheckIfRunning():
    if not os.path.exists(APPDATA_PATH):
        os.makedirs(APPDATA_PATH)

    if os.path.exists(LOCK_FILE):
        sys.exit("Another instance is already running.")
    else:
        with open(LOCK_FILE, 'w') as lock:
            lock.write(str(os.getpid()))

def DeleteLockFile():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

CheckIfRunning()

def DownloadAssets():
    if not os.path.exists(SOUNDS_PATH):
        os.makedirs(SOUNDS_PATH)
    
    if not os.path.exists(DEFAULT_SOUND_FILE):
        response = requests.get(DEFAULT_SOUND_URL)
        with open(DEFAULT_SOUND_FILE, 'wb') as file:
            file.write(response.content)
    
    if not os.path.exists(ICON_FILE):
        response = requests.get(ICON_URL)
        with open(ICON_FILE, 'wb') as file:
            file.write(response.content)

def CreateConfig():
    if not os.path.exists(CONFIG_PATH):
        config_data = {
            "sound": "default.mp3",
            "volume": VOLUME_LEVEL
        }
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(config_data, config_file)

def LoadSound():
    global VOLUME_LEVEL
    with open(CONFIG_PATH, 'r') as config_file:
        config = json.load(config_file)

    sound_file = os.path.join(SOUNDS_PATH, config["sound"])
    VOLUME_LEVEL = config.get("volume", 0.5)
    sound = mixer.Sound(sound_file)
    sound.set_volume(VOLUME_LEVEL)
    return sound

def CheckForUpdates():
    try:
        response = requests.get('https://api.github.com/repos/RuskyDev/keyboard-sounds/tags')
        latest_version = response.json()[0]['name']
        if latest_version != VERSION:
            notification.notify(
                title="Keyboard Sounds Update",
                message=f"Your version is {VERSION}. A new version {latest_version} is available. Please update!",
                app_name="Keyboard Sounds",
                timeout=1
            )
    except Exception as e:
        return

mixer.init()
DownloadAssets()
CreateConfig()

SOUND = LoadSound()

notification.notify(
    title="Keyboard Sounds",
    message="The app is running in the background. Right-click the tray icon for more information.",
    app_name="Keyboard Sounds",
    timeout=1
)

CheckForUpdates()

def PlaySound():
    global IS_ENABLED
    if IS_ENABLED:
        SOUND.play()

def OnPress(key):
    PlaySound()

def StartListener():
    with keyboard.Listener(on_press=OnPress) as listener:
        listener.join()

def ToggleSoundState(icon, item):
    global IS_ENABLED
    IS_ENABLED = not IS_ENABLED
    UpdateMenu(icon)

def ReloadConfigurations(icon, item):
    global SOUND, VOLUME_LEVEL
    SOUND = LoadSound()
    mixer.Sound.set_volume(SOUND, VOLUME_LEVEL)

def OpenConfigurations(icon, item):
    os.startfile(CONFIG_PATH)

def OpenSupport(icon, item):
    webbrowser.open("https://discord.gg/MAnvhWJvsC")

def UpdateMenu(icon):
    toggle_item = MenuItem("Disable" if IS_ENABLED else "Enable", ToggleSoundState)
    settings_menu = Menu(
        MenuItem('Reload Configurations', ReloadConfigurations),
        MenuItem('Open Configurations', OpenConfigurations)
    )
    menu = Menu(
        toggle_item,
        MenuItem('Settings', settings_menu),
        MenuItem('Support', OpenSupport),
        MenuItem('Quit', QuitProgram)
    )
    icon.menu = menu

def QuitProgram(icon, item):
    icon.stop()
    mixer.quit()
    DeleteLockFile()
    sys.exit()

def SetupTrayIcon():
    global TRAY_ICON
    icon_image = Image.open(ICON_FILE)
    TRAY_ICON = Icon("Keyboard Sounds", icon_image)
    UpdateMenu(TRAY_ICON)
    TRAY_ICON.run()

TRAY_THREAD = threading.Thread(target=SetupTrayIcon)
TRAY_THREAD.start()

LISTENER_THREAD = threading.Thread(target=StartListener)
LISTENER_THREAD.start()

atexit.register(DeleteLockFile)
