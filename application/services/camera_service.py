from ultils.log import get_logger

log = get_logger("CameraService")

class CameraService:
    def __init__(self, camera, state):
        self.camera = camera
        self.state = state
        self.camera.frame_callback = self.on_new_frame
        self._frame_count = 0
        log.debug("CameraService initialized")

    def on_new_frame(self, frame):
        with self.state.frame_lock:
            self.state.current_frame = frame
        self._frame_count += 1
        if self._frame_count % 30 == 0:
            log.debug(f"Frame #{self._frame_count} received | shape={frame.shape}")

    def start_camera(self, camera_url):
        log.info("Starting camera...")
        self.camera.start(camera_url)
        self.state.camera_running = True
        log.info("Camera started OK")

    def stop_camera(self):
        log.info("Stopping camera...")
        self.camera.stop()
        self.state.camera_running = False
        log.info("Camera stopped OK")