import time
import queue
import threading

from ultils.geometry import PointPolygon
from ultils.log import get_logger

from domain.domain.rules import (        # FIX: bỏ domain lặp (domain.domain.rules → domain.rules)
    ProductInspector,
    PositionalVotingRule,
)

from ultils.config.constants import (
    STEP_MOVE_TIME,
    POSITION_VOTING_FRAMES,
    POSITION_ERR_X,
    POSITION_ERR_Y,
)

log = get_logger("ConveyorUseCase")

MAX_SQUARE_RETRY = 30   # tránh loop vô hạn nếu mất Square liên tục


class ConveyorUseCase:

    def __init__(self, state, yolo, sahi, motor, servo):
        self.state = state
        self.yolo = yolo
        self.sahi = sahi
        self.motor = motor
        self.servo = servo

        # FIX: truyền constants vào rule thay vì hardcode trong PositionalVotingRule
        self.rule = PositionalVotingRule(
            n_frames=POSITION_VOTING_FRAMES,
            err_x=POSITION_ERR_X,
            err_y=POSITION_ERR_Y,
        )

        self.inspection_queue = queue.Queue(maxsize=1)

        self.worker = threading.Thread(
            target=self._inspection_worker,
            daemon=True,
        )
        self.worker.start()

    # ------------------------------------------------------------------
    @staticmethod
    def _extract_bbox(product):
        """
        Lấy bounding box (x1, y1, x2, y2) từ object product, thử vài tên
        attribute phổ biến. CHỈNH LẠI nếu class Product dùng tên khác
        (ví dụ product.xyxy thay vì product.bbox).
        """
        for attr in ("bbox", "box", "xyxy", "rect"):
            if hasattr(product, attr):
                value = getattr(product, attr)
                if callable(value):
                    value = value()
                return tuple(value)
        return None

    # ------------------------------------------------------------------
    @staticmethod
    def _extract_label(product):
        """
        Lấy tên nhãn từ object product, thử vài tên attribute phổ biến.
        CHỈNH LẠI dòng này nếu class Product dùng tên attribute khác
        (ví dụ product.class_name thay vì product.label).
        """
        for attr in ("class_name", "label", "name", "cls_name"):
            if hasattr(product, attr):
                return getattr(product, attr)
        return str(product)

    # ------------------------------------------------------------------
    def process(self, frame, polygon):
        """
        Được gọi liên tục từ main loop.
        Khi phát hiện Square trong vùng polygon → dừng băng tải và trigger kiểm tra.
        """
        if frame is None:
            return
        if len(polygon) < 4:
            return
        if not self.state.conveyor_running:
            return

        products = self.yolo.detect(frame)

        self.state.detected_labels = [
            {
                "label": self._extract_label(p),
                "center": p.center(),
                "bbox": self._extract_bbox(p),
            }
            for p in products
        ]

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

    # ------------------------------------------------------------------
    def _inspection_worker(self):
        """Worker thread — chạy liên tục, nhận signal từ queue."""
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

    # ------------------------------------------------------------------
    def _run_inspection_cycle(self):
        """
        Chu kỳ kiểm tra chính:
          1. Chạy băng tải từng bước nhỏ (STEP_MOVE_TIME)
          2. YOLO detect → xác nhận Square còn trong frame (làm anchor)
          3. SAHI detect toàn bộ frame → lấy tất cả sản phẩm
          4. Voting qua n_frames
          5. Evaluate → servo push nếu FAIL
        """
        retry = 0

        while self.rule.frame_count < self.rule.n_frames:

            if retry >= MAX_SQUARE_RETRY:
                log.error(
                    f"Mất Square anchor {MAX_SQUARE_RETRY} lần liên tiếp "
                    f"— hủy chu kỳ kiểm tra, restart conveyor"
                )
                self._safe_recover()
                return

            # Bước băng tải nhỏ (bỏ qua ở frame đầu tiên)
            if self.rule.frame_count > 0:
                self.motor.start_conveyor()
                time.sleep(STEP_MOVE_TIME)
                self.motor.stop_conveyor()
                time.sleep(0.08)   # chờ rung tắt

            frame = self.state.current_frame
            if frame is None:
                log.warning("current_frame is None — chờ frame kế tiếp")
                retry += 1
                time.sleep(0.05)
                continue

            frame = frame.copy()

            # Bước 1: YOLO detect nhanh — chỉ để xác nhận Square còn anchor trong frame
            yolo_products = self.yolo.detect(frame)
            square = next(
                (p for p in yolo_products if ProductInspector.is_trigger_square(p)),
                None,
            )

            if square is None:
                log.warning(
                    f"Không tìm thấy Square ở frame này (retry {retry + 1}/{MAX_SQUARE_RETRY})"
                )
                retry += 1
                continue

            retry = 0   # reset khi tìm lại được anchor

            # Bước 2: SAHI detect toàn bộ frame để lấy đủ tất cả sản phẩm (kể cả nhỏ)
            sahi_products = self.sahi.detect(frame)

            self.rule.add_frame(sahi_products)

            log.info(f"Frame {self.rule.frame_count}/{self.rule.n_frames}")

        # --- Evaluate ---
        passed, detail = self.rule.evaluate()

        for item in detail:
            log.info(item)

        if passed:
            log.info("✅ PASS")
            self.state.triggered = False
        else:
            log.warning("❌ FAIL")
            self.state.triggered = True

        self.state.pred_done = True

        # Servo đẩy sản phẩm lỗi ra
        if self.state.triggered:
            self.servo.push()
            time.sleep(0.2)
            self.servo.Pulling_out()
            time.sleep(0.2)

        # Khởi động lại băng tải
        self.motor.start_conveyor()
        self.state.conveyor_running = True
        self.state.action_done = True

    # ------------------------------------------------------------------
    def _safe_recover(self):
        """
        Đảm bảo conveyor luôn được khởi động lại dù có lỗi/timeout,
        tránh kẹt băng tải vô hạn.
        """
        try:
            self.motor.start_conveyor()
        except Exception:
            log.exception("Lỗi khi cố gắng restart conveyor sau sự cố")
        finally:
            self.state.conveyor_running = True
            self.state.action_done = True
            self.state.pred_done = True