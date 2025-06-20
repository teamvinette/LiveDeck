from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import time
import queue

# -------------------- CONFIG --------------------
MIDDLEWARE_LISTEN_IP = "127.0.0.1"
MIDDLEWARE_LISTEN_PORT = 10999
ABLETONOSC_IP = "127.0.0.1"
ABLETONOSC_SEND_PORT = 11000
ABLETONOSC_RECEIVE_PORT = 11001
SHUTDOWN_TRIGGER = "/shutdown"

# -------------------- SETUP --------------------
dispatcher = Dispatcher()
to_ableton = SimpleUDPClient(ABLETONOSC_IP, ABLETONOSC_SEND_PORT)

# -------------------- TASK QUEUE --------------------
class Task:
    def __init__(self, track_name, mute_value=None, solo_value=None):
        self.track_name = track_name
        self.mute_value = mute_value
        self.solo_value = solo_value

task_queue = queue.Queue()
processing_task = False

# -------------------- HANDLERS --------------------
def handle_unknown(addr, *args):
    print(f"[WARN] Unhandled OSC message: {addr} {args}")

def handle_shutdown(addr, *args):
    print("Shutdown requested. Cleaning up...")
    shutdown_event.set()

def extract_track_name(addr):
    parts = addr.split("_", 1)
    if len(parts) == 2:
        return parts[1]  # Keep original case and spacing
    return ""

def generic_handler(addr, *args):
    global processing_task
    print(f"[INFO] Received OSC: {addr}")

    if addr.startswith("/custom/mute_"):
        track_name = extract_track_name(addr)
        task_queue.put(Task(track_name, mute_value=1))

    elif addr.startswith("/custom/unmute_"):
        track_name = extract_track_name(addr)
        task_queue.put(Task(track_name, mute_value=0))

    elif addr.startswith("/custom/solo_"):
        track_name = extract_track_name(addr)
        task_queue.put(Task(track_name, solo_value=1))

    elif addr.startswith("/custom/unsolo_"):
        track_name = extract_track_name(addr)
        task_queue.put(Task(track_name, solo_value=0))

    else:
        print(f"[WARN] No matching pattern for {addr}")
        return

    # Start processing if idle
    if not processing_task:
        processing_task = True
        to_ableton.send_message("/live/song/get/track_names", [])

def handle_track_names(addr, *args):
    global processing_task

    if task_queue.empty():
        print("[INFO] No pending tasks.")
        processing_task = False
        return

    task = task_queue.get()
    print(f"[DEBUG] Processing task: {task.track_name}, mute: {task.mute_value}, solo: {task.solo_value}")

    raw = args[0] if len(args) == 1 else args
    track_list = list(raw) if isinstance(raw, (list, tuple)) else []
    if not track_list:
        print("[ERROR] Received empty or invalid track list")
        processing_task = False
        return

    try:
        index = track_list.index(task.track_name)
    except ValueError:
        print(f"[ERROR] Track '{task.track_name}' not found")
        processing_task = False
        return

    if task.mute_value is not None:
        to_ableton.send_message("/live/track/set/mute", [index, task.mute_value])
        print(f"[INFO] Set mute for '{task.track_name}' at index {index} to {task.mute_value}")

    if task.solo_value is not None:
        to_ableton.send_message("/live/track/set/solo", [index, task.solo_value])
        print(f"[INFO] Set solo for '{task.track_name}' at index {index} to {task.solo_value}")

    # If more tasks remain, immediately trigger next request
    if not task_queue.empty():
        to_ableton.send_message("/live/song/get/track_names", [])
    else:
        processing_task = False

# -------------------- DISPATCHER --------------------
dispatcher.set_default_handler(handle_unknown)
dispatcher.map(SHUTDOWN_TRIGGER, handle_shutdown)
dispatcher.map("/custom/*", generic_handler)
dispatcher.map("/live/song/track_names", handle_track_names)
dispatcher.map("/live/song/get/track_names", handle_track_names)

# -------------------- SERVER --------------------
shutdown_event = threading.Event()
companion_server = ThreadingOSCUDPServer((MIDDLEWARE_LISTEN_IP, MIDDLEWARE_LISTEN_PORT), dispatcher)
ableton_server = ThreadingOSCUDPServer((ABLETONOSC_IP, ABLETONOSC_RECEIVE_PORT), dispatcher)

servers = [companion_server, ableton_server]
threads = []
for name, server in zip(["Companion", "Ableton"], servers):
    t = threading.Thread(target=server.serve_forever, name=f"{name}Server")
    t.start()
    threads.append(t)
    print(f"[INFO] Started {name} server on {server.server_address}")

try:
    while not shutdown_event.is_set():
        shutdown_event.wait(0.5)
except KeyboardInterrupt:
    print("\n[INFO] KeyboardInterrupt received. Shutting down...")
    shutdown_event.set()
finally:
    for server in servers:
        server.shutdown()
    for t in threads:
        t.join()
    print("[INFO] Middleware exited cleanly")
