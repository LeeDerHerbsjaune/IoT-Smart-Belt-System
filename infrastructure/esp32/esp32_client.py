import requests
from ultils.log import get_logger

log = get_logger("ESP32Client")

class ESP32Client:
    def __init__(self, IP, timeout):
        self.ip = IP
        self.timeout = timeout
        log.debug(f"ESP32Client created | ip={IP} | timeout={timeout}s")

    def set_ip(self, ip):
        log.debug(f"IP updated: {self.ip} → {ip}")
        self.ip = ip

    def send(self, path):
        url = f"http://{self.ip}/{path}"
        log.debug(f"HTTP GET → {url}")
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            log.debug(f"HTTP 200 ← {url}")
            return True
        except requests.RequestException as ex:
            log.error(f"HTTP FAILED ← {url} | {ex}")
            return False

    def ping(self):
        log.debug(f"Pinging {self.ip}...")
        result = self.send("")
        log.debug(f"Ping result: {'OK' if result else 'FAIL'}")
        return result


class Motor:
    def __init__(self, client):
        self.client = client
        self._log = get_logger("Motor")

    def start_conveyor(self):
        self._log.info("Motor → START (state=1)")
        return self.client.send("motorControl?state=1")

    def stop_conveyor(self):
        self._log.info("Motor → STOP (state=0)")
        return self.client.send("motorControl?state=0")
    def test_model(self):
        self._log.debug(f"Testing model")
        return True


class Servo:
    def __init__(self, client):
        self.client = client
        self._log = get_logger("Servo")

    def push(self):
        self._log.info("Servo → PUSH (angle=180)")
        return self.client.send("setServo?angle=180")

    def Pulling_out(self):
        self._log.info("Servo → PULL (angle=0)")
        return self.client.send("setServo?angle=0")