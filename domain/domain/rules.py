from domain.domain.entities import Slot
from ultils.config.constants import SQUARE_PRODUCTS, RIGHT_PRODUCTS


class ProductInspector:

    @staticmethod
    def is_trigger_square(product) -> bool:
        """Kiểm tra sản phẩm có phải anchor Square không."""
        return product.label in SQUARE_PRODUCTS

    @staticmethod
    def is_right_product(product) -> bool:
        """Chỉ lấy sản phẩm đúng (R-*) vào reference và voting."""
        return product.label in RIGHT_PRODUCTS


class PositionalVotingRule:
    """
    Voting theo vị trí tương đối so với anchor Square.

    Luồng hoạt động:
      1. Frame đầu tiên có Square → build reference từ tọa độ thực tế detect được
         (chỉ lấy R-* products, bỏ qua W-* và Square)
      2. Các frame sau → so khớp nearest-neighbor trong phạm vi (err_x, err_y)
         → counting[slot] += 1
      3. Sau n_frames → evaluate(): slot nào count > frame_count/2 là PASS

    Ưu điểm so với STANDARD_LAYOUT cứng:
      - Tự thích nghi với góc nghiêng, vị trí đặt camera thực tế
      - Không cần calibrate tay từng lần lắp đặt
    """

    def __init__(self,
                 n_frames: int = 10,
                 err_x: float = 15,
                 err_y: float = 15):

        self.n_frames = n_frames
        self.err_x = err_x
        self.err_y = err_y

        self.reference: list[Slot] = []
        self.counting: list[int] = []
        self.frame_count: int = 0
        self.reference_ready: bool = False

    # ------------------------------------------------------------------
    def reset(self):
        self.reference.clear()
        self.counting.clear()
        self.frame_count = 0
        self.reference_ready = False

    # ------------------------------------------------------------------
    def _build_reference(self, products) -> bool:
        """
        Xây dựng layout tham chiếu từ frame đầu tiên detect được.
        - Anchor: Square có confidence cao nhất
        - Chỉ lấy R-* products (sản phẩm đúng) vào reference
        - dx, dy tính từ tâm Square → tâm từng sản phẩm
        Trả về False nếu không đủ điều kiện.
        """
        square_list = [p for p in products if ProductInspector.is_trigger_square(p)]
        if not square_list:
            return False

        square = max(square_list, key=lambda p: p.confidence)
        sx, sy = square.center()

        # Chỉ lấy R-* products làm reference
        right_products = [
            p for p in products
            if ProductInspector.is_right_product(p)
        ]

        if not right_products:
            return False

        # Tính offset tương đối so với anchor
        others = []
        for p in right_products:
            px, py = p.center()
            others.append((p.label, px - sx, py - sy))

        # Sắp xếp theo (dy, dx) để gán index nhất quán
        others.sort(key=lambda x: (x[2], x[1]))

        for i, (label, dx, dy) in enumerate(others):
            self.reference.append(Slot(i, label, dx, dy))
            self.counting.append(0)

        self.reference_ready = True
        return True

    # ------------------------------------------------------------------
    def add_frame(self, products) -> bool:
        """
        Thêm một frame vào vòng voting.
        Trả về True khi đã đủ n_frames (sẵn sàng evaluate).
        """
        square_list = [p for p in products if ProductInspector.is_trigger_square(p)]
        if not square_list:
            return False

        # Frame đầu tiên → build reference từ tọa độ thực tế
        if not self.reference_ready:
            ok = self._build_reference(products)
            if not ok:
                return False
            self.frame_count += 1
            return self.frame_count >= self.n_frames

        square = max(square_list, key=lambda p: p.confidence)
        sx, sy = square.center()

        # Chỉ lấy R-* products để so khớp — bỏ qua W-* và Square
        current = []
        for p in products:
            if not ProductInspector.is_right_product(p):
                continue
            px, py = p.center()
            current.append((p.label, px - sx, py - sy))

        # Nearest-neighbor matching — tránh lệch index khi frame detect thiếu sản phẩm
        matched_slots = set()

        for label, dx, dy in current:
            best_slot = None
            best_dist = float('inf')

            for slot in self.reference:
                if slot.index in matched_slots:
                    continue
                if slot.label != label:
                    continue

                ddx = abs(dx - slot.dx)
                ddy = abs(dy - slot.dy)

                if ddx <= self.err_x and ddy <= self.err_y:
                    dist = ddx + ddy
                    if dist < best_dist:
                        best_dist = dist
                        best_slot = slot

            if best_slot is not None:
                self.counting[best_slot.index] += 1
                matched_slots.add(best_slot.index)

        self.frame_count += 1
        return self.frame_count >= self.n_frames

    # ------------------------------------------------------------------
    def evaluate(self) -> tuple[bool, list]:
        """
        Trả về (passed, detail).
        passed = True nếu TẤT CẢ slot R-* đều xuất hiện đủ số frame.
        """
        result = []
        passed = True
        threshold = self.frame_count / 2

        for slot in self.reference:
            cnt = self.counting[slot.index]
            ok = cnt > threshold
            result.append({
                "slot":  slot.index,
                "label": slot.label,
                "count": cnt,
                "pass":  ok,
            })
            if not ok:
                passed = False

        return passed, result