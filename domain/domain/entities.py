'''
có 2 thực thể bao gồm product và slot.
product là class dùng để detect khi đưa vào cùng hình học, slot class là class dùng cho việc tạo index để ánh xạ các labels dectect được 
vào trong list couting cùng như dùng để duyệt sản phẩm lỗi hay đúng
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

    def __init__(self,
                 label,
                 ref_dx,
                 ref_dy):
        self.label = label
        self.ref_dx = ref_dx
        self.ref_dy = ref_dy