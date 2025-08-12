import pygame
import wave
import struct
import time
import logging
import os
import sys

# 设置日志
logging.basicConfig(
    filename='silent_audio_player.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def generate_silent_wav(filename, duration=1, sample_rate=44100):
    """
    生成一个无声的WAV文件。
    :param filename: 输出文件名
    :param duration: 时长（秒）
    :param sample_rate: 采样率
    """
    num_samples = int(duration * sample_rate)
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)  # 单声道
        w.setsampwidth(2)  # 16位
        w.setframerate(sample_rate)
        for _ in range(num_samples):
            w.writeframes(struct.pack('h', 0))
    logging.info(f"生成无声WAV文件: {filename}, 时长: {duration}秒")

def play_silent_audio():
    silent_file = 'silent.wav'
    
    # 如果无声文件不存在，生成一个1秒的
    if not os.path.exists(silent_file):
        generate_silent_wav(silent_file, duration=1)
    
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=4096)
        logging.info("Pygame mixer 初始化成功")
    except pygame.error as e:
        logging.error(f"Pygame mixer 初始化失败: {e}")
        sys.exit(1)
    
    try:
        sound = pygame.mixer.Sound(silent_file)
        logging.info("加载无声音频文件成功")
    except pygame.error as e:
        logging.error(f"加载音频文件失败: {e}")
        sys.exit(1)
    
    logging.info("开始不间断播放无声音频")
    while True:
        try:
            channel = sound.play()
            while channel.get_busy():
                time.sleep(0.1)  # 低资源占用检查，休眠0.1秒
            # 立即重新播放，实现不间断
        except Exception as e:
            logging.error(f"播放过程中出错: {e}")
            time.sleep(1)  # 出错后稍等重试

if __name__ == "__main__":
    logging.info("程序启动")
    play_silent_audio()
