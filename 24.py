import pygame
import os
import ctypes
import time
import sys

def get_system_uptime():
    """
    获取系统启动后的时间（毫秒）。
    """
    return ctypes.windll.kernel32.GetTickCount64()

def reinitialize_mixer(audio_file):
    """
    重新初始化 pygame.mixer 并播放音频。
    """
    try:
        pygame.mixer.quit()
        time.sleep(1)  # 延迟释放资源
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play(loops=-1)
        print("Reinitialized mixer and restarted audio.")
    except Exception as e:
        print(f"Failed to reinitialize mixer: {e}")

def play_audio():
    audio_file = "24.mp3"  # 替换为你的音频文件路径

    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at {audio_file}")
        return

    print("Initializing pygame.mixer...")
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play(loops=-1)
    print("Audio is playing...")

    last_uptime = get_system_uptime()  # 获取当前系统运行时间

    while True:
        try:
            # 检测音频是否停止，若停止则重新播放
            if not pygame.mixer.music.get_busy():
                print("Audio stopped unexpectedly. Restarting...")
                reinitialize_mixer(audio_file)

            # 检测系统是否从休眠中唤醒
            current_uptime = get_system_uptime()
            if current_uptime < last_uptime:  # 系统唤醒会导致 uptime 重置
                print("System wakeup detected. Reinitializing mixer...")
                reinitialize_mixer(audio_file)

            last_uptime = current_uptime  # 更新 uptime

            time.sleep(1)  # 每秒检测一次

        except KeyboardInterrupt:
            print("Exiting program...")
            break

        except pygame.error as e:
            print(f"Error: {e}. Attempting to recover...")
            reinitialize_mixer(audio_file)

    pygame.mixer.quit()
    print("Mixer quit. Program exited.")

if __name__ == "__main__":
    try:
        play_audio()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)
