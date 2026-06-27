from ultils.config.constants import (
    STANDARD_LAYOUT,
    SQUARE_PRODUCTS,
)
from ultils.log import get_logger

log = get_logger("Rules")


class ProductInspector:

    @staticmethod
    def is_trigger_square(product):
        return product.label in SQUARE_PRODUCTS


class PositionalVotingRule:

    def __init__(self, n_frames=10, err_x=15, err_y=15):
        self.n_frames = n_frames
        self.err_x = err_x
        self.err_y = err_y
        self.counting = [0] * len(STANDARD_LAYOUT)
        self.frame_count = 0

    def reset(self):
        self.counting = [0] * len(STANDARD_LAYOUT)
        self.frame_count = 0

    def add_frame(self, products) -> bool:
        """Trả True nếu frame được tính hợp lệ (có anchor)."""
        squares = [p for p in products if ProductInspector.is_trigger_square(p)]

        if not squares:
            log.warning("add_frame: không tìm thấy Square anchor — bỏ frame này")
            return False

        anchor = max(squares, key=lambda p: p.confidence)
        ax, ay = anchor.center()

        used_slot = [False] * len(STANDARD_LAYOUT)
        unmatched = []

        for product in products:
            if product is anchor:
                continue

            px, py = product.center()
            dx = px - ax
            dy = py - ay

            best_slot = None
            best_dist = float("inf")

            for i, slot in enumerate(STANDARD_LAYOUT):
                if used_slot[i]:
                    continue
                if slot.label != product.label:
                    continue

                # BUG FIX: slot.dx/dy không tồn tại -> phải dùng ref_dx/ref_dy
                dist = (dx - slot.ref_dx) ** 2 + (dy - slot.ref_dy) ** 2

                if dist < best_dist:
                    best_dist = dist
                    best_slot = i

            if best_slot is None:
                unmatched.append(product.label)
                continue

            used_slot[best_slot] = True
            slot = STANDARD_LAYOUT[best_slot]

            # BUG FIX: slot.dx/dy -> slot.ref_dx/ref_dy
            if (
                abs(dx - slot.ref_dx) <= self.err_x and
                abs(dy - slot.ref_dy) <= self.err_y
            ):
                self.counting[best_slot] += 1

        if unmatched:
            log.warning(f"add_frame: {len(unmatched)} product(s) không khớp slot nào: {unmatched}")

        self.frame_count += 1
        return True

    def evaluate(self):
        """Trả (overall: bool, result: list[dict])."""
        if self.frame_count == 0:
            log.error("evaluate() gọi khi frame_count=0 — không có dữ liệu để đánh giá")
            return False, []

        overall = True
        result = []

        for i, slot in enumerate(STANDARD_LAYOUT):
            ratio = self.counting[i] / self.frame_count
            passed = ratio > 0.5

            result.append({
                "slot": i,
                "label": slot.label,
                "ratio": ratio,
                "count": self.counting[i],
                "pass": passed,
            })

            if not passed:
                overall = False

        return overall, result