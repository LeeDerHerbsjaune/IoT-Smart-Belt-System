from ultils.config.constants import (
    STANDARD_LAYOUT,
    SQUARE_PRODUCTS
)


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

    def add_frame(self, products):

        squares = [
            p for p in products
            if ProductInspector.is_trigger_square(p)
        ]

        if not squares:
            return False

        anchor = max(
            squares,
            key=lambda p: p.confidence
        )

        ax, ay = anchor.center()

        used_slot = [False] * len(STANDARD_LAYOUT)

        for product in products:

            if product == anchor:
                continue

            px, py = product.center()

            dx = px - ax
            dy = py - ay

            best_slot = None
            best_dist = float("inf")

            # Chỉ tìm trong các slot cùng label
            for i, slot in enumerate(STANDARD_LAYOUT):

                if used_slot[i]:
                    continue

                if slot.label != product.label:
                    continue

                dist = (
                    (dx - slot.dx) ** 2 +
                    (dy - slot.dy) ** 2
                )

                if dist < best_dist:
                    best_dist = dist
                    best_slot = i

            if best_slot is None:
                continue

            used_slot[best_slot] = True

            slot = STANDARD_LAYOUT[best_slot]

            if (
                abs(dx - slot.dx) <= self.err_x and
                abs(dy - slot.dy) <= self.err_y
            ):
                self.counting[best_slot] += 1

        self.frame_count += 1

        return self.frame_count >= self.n_frames

    def evaluate(self):

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
                "pass": passed
            })

            if not passed:
                overall = False

        return overall, result