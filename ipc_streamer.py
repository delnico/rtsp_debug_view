import struct
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
        self._socket.close()

    def _run(self):
        self._socket.bind(self._ipc_path)
        dtype_map = {
            0: np.uint8,  # CV_8U
            1: np.int8,  # CV_8S
            2: np.uint16,  # CV_16U
            3: np.int16,  # CV_16S
            4: np.int32,  # CV_32S
            5: np.float32,  # CV_32F
            6: np.float64  # CV_64F
        }

        while self._enabled:
            metadata = self._socket.recv(flags=zmq.Flag.SNDMORE)
            data = self._socket.recv()

            metadata = struct.unpack("4i", metadata)

            height = metadata[0]
            width = metadata[1]
            channels = metadata[2]
            cv_type = metadata[3]
            depth = cv_type & 7  # Les 3 premiers bits donnent la profondeur
            dtype = dtype_map.get(depth, np.uint8)

            frame = np.frombuffer(data, dtype=dtype)
            frame = frame.reshape((height, width, channels))
            cv2.imshow(self._win_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self._enabled = False

        cv2.destroyWindow(self._win_name)

