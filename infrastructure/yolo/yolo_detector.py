from ultralytics import YOLO
from domain.domain.entities import Product
from ultils.config.settings import Settings
from ultils.log import get_logger

log = get_logger("YOLODetector")

class YOLODetector:
    def __init__(self):
        log.info(f"Loading YOLO model from {Settings.YOLO_MODEL_PATH}...")
        self.model = YOLO(Settings.YOLO_MODEL_PATH)
        log.info("YOLO model loaded OK")

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        products = []
        for r in results.boxes.data.cpu().numpy():
            x1, y1, x2, y2, conf, cls_id = r
            label = self.model.names[int(cls_id)]
            products.append(Product(label, (x1, y1, x2, y2), conf))

        if products:
            summary = ", ".join(
                f"{p.label}({p.confidence:.2f})" for p in products
            )
            log.debug(f"detect() → [{summary}]")
        else:
            log.debug("detect() → no objects")
        return products