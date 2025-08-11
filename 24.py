import pyaudio
import threading
import time
import logging
import win32con
import win32gui
import win32api
import win32gui_struct

# ================= 日志配置 =================
logging.basicConfig(
    filename="silent_audio.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

# ================= 播放器类 =================
class SilentAudioPlayer:
    def __init__(self, rate=44100, channels=2, chunk=1024):
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.playing = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.playing:
                return
            self.playing = True
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk,
                stream_callback=self.callback
            )
            self.stream.start_stream()
            logging.info("静音播放已开始")

    def stop(self):
        with self.lock:
            if not self.playing:
                return
            self.playing = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            logging.info("静音播放已停止")

    def callback(self, in_data, frame_count, time_info, status):
        # 生成静音数据
        data = b'\x00' * frame_count * self.channels * 2
        return (data, pyaudio.paContinue)

    def terminate(self):
        self.stop()
        self.p.terminate()
        logging.info("播放器已退出")


# ================= 电源事件监听 =================
class PowerEventListener:
    def __init__(self, player: SilentAudioPlayer):
        self.player = player

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_POWERBROADCAST:
            if wparam == win32con.PBT_APMSUSPEND:
                logging.info("系统进入休眠，暂停播放")
                self.player.stop()
            elif wparam == win32con.PBT_APMRESUMEAUTOMATIC:
                logging.info("系统唤醒，恢复播放")
                self.player.start()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def run(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "PowerEventListener"
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindowEx(
            0, wc.lpszClassName, "PowerEventWindow", 0,
            0, 0, 0, 0,
            0, 0, hinst, None
        )
        win32gui.PumpMessages()


# ================= 主程序入口 =================
if __name__ == "__main__":
    player = SilentAudioPlayer()
    listener = PowerEventListener(player)

    # 启动播放
    player.start()

    # 开启电源事件监听线程
    threading.Thread(target=listener.run, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("程序手动结束")
    finally:
        player.terminate()
