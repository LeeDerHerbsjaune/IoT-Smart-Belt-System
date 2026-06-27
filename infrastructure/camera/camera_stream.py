import cv2
import threading
from ultils.log import get_logger
from ultils.config.settings import Settings
import time



log = get_logger("CameraStream")

class CameraStream:
    def __init__(self, source):
        self.source = source
        self.cap = None
        self.running = False
        self.thread = None
        self.frame_callback = None
        log.debug(f"CameraStream created | source={source}")

    def start(self, camera_url=None):
        if self.running:
            log.warning("start() called but camera already running — ignored")
            return
        camera_url = camera_url.strip()
        if camera_url.isdigit():
            self.source = int(camera_url)
            Settings.CAMERA_SOURCE = self.source
        else:
            self.source = camera_url   
            Settings.CAMERA_SOURCE = self.source

        log.info(f"Opening camera source={self.source}...")
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            log.error(f"Cannot open camera source={self.source}")
            raise Exception("Cannot open camera")
        log.info("Camera opened OK")
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
        log.debug("Capture thread started")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        log.info(f"Camera FPS: {self.fps:.2f}")
        self.frame_delay = 3 / self.fps

    def stop(self):
        log.info("Stopping camera stream...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.cap:
            self.cap.release()
        log.info("Camera stream stopped")

    def loop(self):
        log.debug("Capture loop running")
        start = time.perf_counter()
        drop_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                drop_count += 1
                if drop_count % 10 == 1:
                    log.warning(f"Frame read failed (drop #{drop_count})")
                continue
            drop_count = 0
            frame = cv2.resize(frame, (640, 480))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.frame_callback:
                self.frame_callback(rgb)
            elapsed = time.perf_counter() - start

            sleep_time = max(0, self.frame_delay - elapsed)

            time.sleep(sleep_time)
        log.debug("Capture loop exited")
