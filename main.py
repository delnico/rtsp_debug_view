import json
import sys
import os

import cv2

from ipc_streamer import IPCStreamer


def parse_config_file(path_json_file : str) -> list:
    paths = []
    json_file = open(path_json_file)
    json_data = json.load(json_file)
    json_file.close()

    for obj in json_data:
        path = obj['path']
        if path not in paths:
            paths.append(path)
    return paths


if __name__ == '__main__':
    if len(sys.argv) < 2:
        config_file = "config.json"
    else:
        config_file = sys.argv[1]

    paths = parse_config_file(config_file)

    workers : list = []

    for path in paths:
        if not os.path.exists(path):
            os.mkfifo(path)
        worker = IPCStreamer(path)
        workers.append(worker)
        worker.start()

    try:
        input("Press enter to stop...")
    except Exception as e:
        print(e)
    finally:
        print("Exiting...")

    for worker in workers:
        worker.stop()

    cv2.destroyAllWindows()
