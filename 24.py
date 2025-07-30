import threading
import ctypes
import time
import logging
import pyaudio
import win32con
import win32gui
import win32api

# 日志配置，增加 encoding="utf-8"
logging.basicConfig(
    filename="audio_player.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

def log(msg):
    print(msg)
    logging.info(msg)

# 定时清除防休眠状态，避免程序自身阻止休眠
def clear_execution_state_loop():
    def loop():
        while True:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            time.sleep(10)
    threading.Thread(target=loop, daemon=True).start()

class PowerBroadcastListener:
    def __init__(self, on_suspend, on_resume):
        self.on_suspend = on_suspend
        self.on_resume = on_resume
        self._hwnd = None
        self._thread = threading.Thread(target=self._message_pump, daemon=True)
        self._thread.start()

    def _message_pump(self):
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PowerBroadcastListenerWindow"
        wc.lpfnWndProc = self._wnd_proc
        class_atom = win32gui.RegisterClass(wc)

        self._hwnd = win32gui.CreateWindow(
            class_atom,
            "PowerBroadcastListenerWindow",
            0, 0, 0, 0, 0,
            0, 0, hinst, None
        )
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_POWERBROADCAST:
            if wparam == win32con.PBT_APMSUSPEND:
                log("检测到系统休眠，暂停播放")
                self.on_suspend()
            elif wparam == win32con.PBT_APMRESUMEAUTOMATIC:
                log("检测到系统唤醒，恢复播放")
                self.on_resume()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

class SilentAudioPlayer:
    def __init__(self, rate=8000, channels=1, chunk_size=1024):
        self.rate = rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._p = pyaudio.PyAudio()
        self._stream = None
        self._playing = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._playing:
                return
            self._stream = self._p.open(format=pyaudio.paInt16,
                                       channels=self.channels,
                                       rate=self.rate,
                                       output=True)
            self._playing = True
        threading.Thread(target=self._play_loop, daemon=True).start()
        log("开始播放静音流")

    def _play_loop(self):
        silence_chunk = b'\x00\x00' * self.chunk_size
        while True:
            with self._lock:
                if not self._playing:
                    time.sleep(0.1)
                    continue
            try:
                self._stream.write(silence_chunk)
            except Exception as e:
                log(f"播放异常: {e}")
                break

    def pause(self):
        with self._lock:
            if self._playing:
                self._playing = False
                log("暂停播放静音流")

    def resume(self):
        with self._lock:
            if not self._playing:
                self._playing = True
                log("恢复播放静音流")

    def stop(self):
        with self._lock:
            self._playing = False
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        self._p.terminate()
        log("停止播放，释放资源")

def main():
    clear_execution_state_loop()

    player = SilentAudioPlayer()
    player.start()

    listener = PowerBroadcastListener(player.pause, player.resume)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("程序退出")
        player.stop()

if __name__ == "__main__":
    main()
