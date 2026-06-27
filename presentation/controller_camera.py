from ultils.log import get_logger

log = get_logger("CameraController")

class CameraController:
    def __init__(self, camera_service):
        self.camera_service = camera_service
        log.debug("CameraController initialized")

    def on_start_clicked(self, url):
        log.info("[UI] Start camera button clicked")
        self.camera_service.start_camera(url)

    def on_stop_clicked(self):
        log.info("[UI] Stop camera button clicked")
        self.camera_service.stop_camera()