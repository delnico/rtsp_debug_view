import threading
import cv2
import numpy as np
import zmq

class IPCStreamer:
    def __init__(
        self,
        ipc_path : str,
        context : zmq.Context,
        win_name : str = None,
    ):
        self._enabled = False
        self._ipc_path = ipc_path
        self._win_name = (win_name if win_name else ipc_path)
        self._thd : threading.Thread = None
        self._socket = context.socket(zmq.PULL)


    def start(self):
        self._enabled = True
        self._thd = threading.Thread(target=self._run)
        self._thd.start()

    def stop(self):
        self._enabled = False
        self._thd.join()
        self._thd = None

    def _run(self):
        self._socket.bind(self._ipc_path)
        while self._enabled:
            data = self._socket.recv()
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow(self._win_name, frame)
            cv2.waitKey(1)
        cv2.destroyWindow(self._win_name)

