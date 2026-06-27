class Product:
    def __init__(self, label: str, bbox: list, confidence: float):
        self.label = label
        self.bbox = bbox
        self.confidence = confidence

    def center(self) -> tuple:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)