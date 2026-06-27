from ultils.log import get_logger

log = get_logger("ESP32Controller")

class ESP32Controller:
    def __init__(self, esp32_service):
        self.esp32_service = esp32_service
        log.debug("ESP32Controller initialized")

    def on_connect_clicked(self, ip):
        log.info(f"[UI] Connect button clicked | ip={ip}")
        self.esp32_service.connect_esp32(ip)

    def on_disconnect_clicked(self):
        log.info("[UI] Disconnect button clicked")
        self.esp32_service.disconnect_esp32()

    def on_start_clicked(self):
        log.info("[UI] START conveyor button clicked")
        self.esp32_service.start_conveyor()

    def on_stop_clicked(self):
        log.info("[UI] STOP conveyor button clicked")
        self.esp32_service.stop_conveyor()
    def on_test_model_clicked(self):
        log.info("[UI] Test model button clicked")
        self.esp32_service.test_model()