import threading
import cv2
from base64 import b64decode

class IPCStreamer:
    def __init__(
        self,
        ipc_path : str,
        win_name : str = "stream"
    ):
        self._enabled = False
        self._ipc_path = ipc_path
        self._win_name = win_name
        self._thd : threading.Thread = None


    def start(self):
        self._enabled = True
        self._thd = threading.Thread(target=self._run)
        self._thd.start()

    def stop(self):
        self._enabled = False
        self._thd.join()
        self._thd = None

    def _run(self):
        with open(self._ipc_path, "r") as f:
            while self._enabled:
                frame = b64decode(f.readline())
                if frame:
                    cv2.imshow(self._win_name, frame)

        cv2.destroyWindow(self._win_name)

