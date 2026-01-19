import json
import queue
import sys
from queue import Queue

import cv2
import zmq

from ipc_streamer import IPCStreamer

queues = {}


def parse_config_file(path_json_file : str) -> list:
    paths = []
    json_file = open(path_json_file)
    json_data = json.load(json_file)
    json_file.close()

    for obj in json_data:
        path = obj['path']
        if path not in paths:
            paths.append(path)
            queues[path] = Queue(maxsize=1)
    return paths


if __name__ == '__main__':
    if len(sys.argv) < 2:
        config_file = "config.json"
    else:
        config_file = sys.argv[1]

    paths = parse_config_file(config_file)

    workers : list = []
    zmq_context = zmq.Context()

    for idx, path in enumerate(paths):
        worker = IPCStreamer(path, zmq_context, queues[path])
        workers.append(worker)
        worker.start()

    enabled = True

    while enabled:
        try:
            for path in paths:
                try:
                    frame = queues[path].get_nowait()
                    cv2.imshow(f"{path}", frame)
                except queue.Empty:
                    pass
            cv2.waitKey(17)
        except (KeyboardInterrupt, SystemExit):
            enabled = False

    for worker in workers:
        worker.stop()

    for path in paths:
        cv2.destroyWindow(f"{path}")

    zmq_context.term()
    cv2.destroyAllWindows()
