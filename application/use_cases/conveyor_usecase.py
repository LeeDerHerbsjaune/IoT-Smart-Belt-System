import time
import queue
import threading

from ultils.geometry import PointPolygon
from ultils.log import get_logger

from domain.domain.rules import (
    ProductInspector,
    PositionalVotingRule,
)

from ultils.config.constants import STEP_MOVE_TIME

log = get_logger("ConveyorUseCase")

MAX_SQUARE_RETRY = 30   # tránh loop vô hạn nếu mất Square liên tục


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
            daemon=True,
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
            if not PointPolygon.point_in_polygon(product.center(), polygon):
                continue
            target = product
            break

        if target is None:
            return

        log.info("Square detected — bắt đầu kiểm tra vị trí")

        self.motor.stop_conveyor()
        self.state.conveyor_running = False
        self.state.pred_done = False
        self.state.action_done = False
        self.state.triggered = False

        self.rule.reset()

        try:
            self.inspection_queue.put_nowait(True)
        except queue.Full:
            log.warning("Inspection queue đầy — bỏ qua trigger này")

    #########################################################
    def _inspection_worker(self):
        while True:
            try:
                self.inspection_queue.get(timeout=1)
                self._run_inspection_cycle()
                self.inspection_queue.task_done()

            except queue.Empty:
                continue
            except Exception as ex:
                log.exception(ex)
                self._safe_recover()

    #########################################################
    def _run_inspection_cycle(self):
        retry = 0

        while self.rule.frame_count < self.rule.n_frames:

            if retry >= MAX_SQUARE_RETRY:
                log.error(
                    f"Mất Square anchor {MAX_SQUARE_RETRY} lần liên tiếp "
                    f"— hủy chu kỳ kiểm tra, restart conveyor"
                )
                self._safe_recover()
                return

            if self.rule.frame_count > 0:
                self.motor.start_conveyor()
                time.sleep(STEP_MOVE_TIME)
                self.motor.stop_conveyor()
                time.sleep(0.08)

            frame = self.state.current_frame
            if frame is None:
                log.warning("current_frame is None — chờ frame kế tiếp")
                retry += 1
                time.sleep(0.05)
                continue

            frame = frame.copy()
            yolo_products = self.yolo.detect(frame)

            square = next(
                (p for p in yolo_products if ProductInspector.is_trigger_square(p)),
                None,
            )

            if square is None:
                log.warning(f"Không tìm thấy Square ở frame này (retry {retry+1}/{MAX_SQUARE_RETRY})")
                retry += 1
                continue

            retry = 0  # reset khi tìm lại được anchor

            x1, y1, x2, y2 = map(int, square.bbox)

            # pad thêm margin quanh bbox để SAHI không bị crop hụt các slot lân cận
            pad = 30
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

            roi = frame[y1:y2, x1:x2]
            sahi_products = self.sahi.detect(roi)

            ok = self.rule.add_frame(sahi_products)
            if not ok:
                log.warning("Frame bị bỏ qua do add_frame() không hợp lệ")
                continue

            log.info(f"Frame {self.rule.frame_count}/{self.rule.n_frames}")

        passed, detail = self.rule.evaluate()

        for item in detail:
            log.info(item)

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

    #########################################################
    def _safe_recover(self):
        """Đảm bảo conveyor luôn được khởi động lại dù có lỗi/timeout,
        tránh kẹt băng tải vô hạn."""
        try:
            self.motor.start_conveyor()
        except Exception:
            log.exception("Lỗi khi cố gắng restart conveyor sau sự cố")
        finally:
            self.state.conveyor_running = True
            self.state.action_done = True
            self.state.pred_done = True