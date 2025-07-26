import pygame
import os
import ctypes
import time
import sys
import logging

# ========== 日志设置 ==========
log_file = "audio_player.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log(message, level="info"):
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)

# ========== 工具函数 ==========
def get_system_uptime():
    return ctypes.windll.kernel32.GetTickCount64()

def get_audio_path(filename):
    # 使用可执行文件所在目录，支持 .py 和 .exe
    return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), filename)

def reinitialize_mixer(audio_file):
    try:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            time.sleep(1)  # 延迟释放资源
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(loops=-1)
        log("Reinitialized mixer and restarted audio.")
    except Exception as e:
        log(f"Failed to reinitialize mixer: {e}", level="error")

# ========== 主逻辑 ==========
def play_audio():
    audio_file = get_audio_path("24.mp3")

    log(f"Looking for audio file at: {audio_file}")
    log(f"File exists: {os.path.exists(audio_file)}")

    if not os.path.exists(audio_file):
        log(f"Error: Audio file not found at {audio_file}", level="error")
        return

    log("Initializing pygame.mixer...")
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(loops=-1)
        log("Audio is playing...")
    except Exception as e:
        log(f"Failed to initialize audio: {e}", level="error")
        return

    last_uptime = get_system_uptime()
    check_interval_seconds = 5

    while True:
        try:
            if not pygame.mixer.music.get_busy():
                log("Audio stopped unexpectedly. Restarting...", level="warning")
                reinitialize_mixer(audio_file)

            current_uptime = get_system_uptime()
            if current_uptime + 60000 < last_uptime:
                log("System wakeup detected. Reinitializing mixer...", level="info")
                reinitialize_mixer(audio_file)

            last_uptime = current_uptime
            time.sleep(check_interval_seconds)

        except KeyboardInterrupt:
            log("Exiting program by user...")
            break
        except pygame.error as e:
            log(f"pygame error: {e}. Attempting to recover...", level="error")
            reinitialize_mixer(audio_file)
        except Exception as e:
            log(f"Unhandled exception in loop: {e}", level="error")

    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        log("Mixer quit. Program exited.")

# ========== 程序入口 ==========
if __name__ == "__main__":
    try:
        play_audio()
    except Exception as e:
        log(f"Unhandled top-level exception: {e}", level="error")
        sys.exit(1)
