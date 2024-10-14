import pygame
import time
import os

def play_audio():
    print("Initializing pygame...")
    pygame.mixer.init()

    # 音频文件路径
    audio_file = "24.mp3"
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return

    # 加载并循环播放音频
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play(loops=-1)
    print("Audio is playing in loop...")

    # 定时重新初始化 pygame.mixer
    restart_interval = 3600  # 每1小时重启一次音频
    last_restart_time = time.time()

    while True:
        if not pygame.mixer.music.get_busy():
            print("Audio stopped, restarting...")
            pygame.mixer.music.play(loops=-1)
        
        # 每个指定间隔重新初始化音频设备
        if time.time() - last_restart_time > restart_interval:
            print("Restarting pygame mixer...")
            pygame.mixer.quit()  # 停止pygame
            time.sleep(1)  # 稍微延时一下
            pygame.mixer.init()  # 重新初始化
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play(loops=-1)  # 重新播放
            last_restart_time = time.time()
        
        time.sleep(1)  # 每秒检查一次

if __name__ == "__main__":
    play_audio()
