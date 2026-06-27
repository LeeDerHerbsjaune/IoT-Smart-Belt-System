import time
import queue
import threading

from ultils.geometry import PointPolygon
from ultils.log import get_logger

from domain.domain.rules import (
    ProductInspector,
    PositionalVotingRule
)

from ultils.config.constants import STEP_MOVE_TIME

log = get_logger("ConveyorUseCase")


class ConveyorUseCase:

    def __init__(self, state, yolo, sahi, motor, servo):

        self.state = state

        self.yolo = yolo
        self.sahi = sahi

        self.motor = motor
        self.servo = servo

        self.rule = PositionalVotingRule()

        self.inspection_queue = queue.Queue(maxsize=1)

        self.worker = threading.Thread(
            target=self._inspection_worker,
            daemon=True
        )

        self.worker.start()

    #########################################################

    def process(self, frame, polygon):

        if frame is None:
            return

        if len(polygon) < 4:
            return

        if not self.state.conveyor_running:
            return

        products = self.yolo.detect(frame)

        target = None

        for product in products:

            if not ProductInspector.is_trigger_square(product):
                continue

            if not PointPolygon.point_in_polygon(
                product.center(),
                polygon
            ):
                continue

            target = product
            break

        if target is None:
            return

        log.info("Square detected")

        self.motor.stop_conveyor()

        self.state.conveyor_running = False
        self.state.pred_done = False
        self.state.action_done = False
        self.state.triggered = False

        self.rule.reset()

        try:

            self.inspection_queue.put_nowait(True)

        except queue.Full:
            pass

    #########################################################

    def _inspection_worker(self):

        while True:

            try:

                self.inspection_queue.get(timeout=1)

                while self.rule.frame_count < self.rule.n_frames:

                    if self.rule.frame_count > 0:

                        self.motor.start_conveyor()

                        time.sleep(STEP_MOVE_TIME)

                        self.motor.stop_conveyor()

                        time.sleep(0.08)

                    frame = self.state.current_frame.copy()

                    yolo_products = self.yolo.detect(frame)

                    square = None

                    for p in yolo_products:

                        if ProductInspector.is_trigger_square(p):

                            square = p
                            break

                    if square is None:
                        continue

                    x1, y1, x2, y2 = map(int, square.bbox)

                    roi = frame[y1:y2, x1:x2]

                    sahi_products = self.sahi.detect(roi)

                    self.rule.add_frame(sahi_products)

                    log.info(
                        f"Frame "
                        f"{self.rule.frame_count}/"
                        f"{self.rule.n_frames}"
                    )

                passed, detail = self.rule.evaluate()

                for slot in detail:

                    log.info(detail[slot])

                if passed:

                    log.info("PASS")

                    self.state.triggered = False

                else:

                    log.warning("FAIL")

                    self.state.triggered = True

                self.state.pred_done = True

                if self.state.triggered:

                    self.servo.push()

                    time.sleep(0.2)

                    self.servo.Pulling_out()

                    time.sleep(0.2)

                self.motor.start_conveyor()

                self.state.conveyor_running = True
                self.state.action_done = True

                self.inspection_queue.task_done()

            except queue.Empty:

                continue

            except Exception as ex:

                log.exception(ex)