# sahi_detector.py
from sahi.predict import get_sliced_prediction
from domain.domain.entities import Product
from ultils.log import get_logger

log = get_logger("SahiDetector")

class SahiDetector:
    def __init__(self, detection_model):
        self.model = detection_model
        log.debug("SahiDetector initialized")

    def detect(self, image):
        log.info(f"SAHI sliced prediction | image shape={image.shape}")
        result = get_sliced_prediction(
            image,
            self.model,
            slice_height=256,
            slice_width=256,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2,
            verbose=False
        )

        objects = []
        for obj in result.object_prediction_list:
            label = obj.category.name
            bbox = obj.bbox.to_xyxy()
            
            # Map trực tiếp sang thực thể Product
            product = Product(label, bbox, obj.score.value)
            objects.append(product)
            
            log.debug(f"  → {label} | conf={obj.score.value:.2f}")

        log.info(f"SAHI result: {len(objects)} total objects detected.")
        return objects