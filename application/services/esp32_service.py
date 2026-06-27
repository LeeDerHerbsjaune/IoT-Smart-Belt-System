import time
from ultils.log import get_logger

log = get_logger("ConveyorService")

class ConveyorService:
    def __init__(self, state, esp32_client, motor, servo):
        self.motor = motor
        self.servo = servo
        self.esp32_client = esp32_client
        self.state = state
        log.debug("ConveyorService initialized")

    # ── CONNECT ──────────────────────────────────────────
    def connect_esp32(self, ip):
        log.info(f"Connecting to ESP32 at {ip} ...")
        self.esp32_client.set_ip(ip)
        success = self.esp32_client.ping()
        self.state.esp32_connected = success
        if success:
            log.info(f"ESP32 connected OK → {ip}")
        else:
            log.warning(f"ESP32 ping FAILED → {ip}")
        return success
    def test_model(self):
        log.info("Testing model on ESP32...")
        success = self.motor.test_model()
        self.state.conveyor_running = True
        if success:
            log.info("Model test SUCCESS")
        else:
            log.error("Model test FAILED")
        return success
    # ── DISCONNECT ───────────────────────────────────────
    def disconnect_esp32(self):
        log.info("Disconnecting ESP32")
        self.state.esp32_connected = False

    # ── START CONVEYOR ───────────────────────────────────
    def start_conveyor(self):
        if not self.state.esp32_connected:
            log.warning("start_conveyor called but ESP32 not connected — skipped")
            return False
        log.info("Sending START to motor...")
        success = self.motor.start_conveyor()
        if success:
            self.state.conveyor_running = True
            log.info("Conveyor STARTED")
        else:
            log.error("Motor start command FAILED")
        return success

    # ── STOP CONVEYOR ────────────────────────────────────
    def stop_conveyor(self):
        log.info("Sending STOP to motor...")
        success = self.motor.stop_conveyor()
        if success:
            self.state.conveyor_running = False
            log.info("Conveyor STOPPED")
        else:
            log.error("Motor stop command FAILED")
        return success