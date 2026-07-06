'''
Có 2 thực thể bao gồm Product và Slot.
- Product: class dùng để chứa kết quả detect (label, bbox, confidence)
- Slot: class dùng để tạo index ánh xạ các labels detect được
  vào list counting, đồng thời dùng để duyệt sản phẩm lỗi/đúng
'''


class Product:

    def __init__(self, label: str, bbox: list, confidence: float):
        self.label = label
        self.bbox = bbox
        self.confidence = confidence

    def center(self) -> tuple:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class Slot:

    def __init__(self, index: int, label: str, dx: float, dy: float):
        self.index = index
        self.label = label
        self.dx = dx
        self.dy = dy
