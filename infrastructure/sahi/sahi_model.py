from ultils.config.settings import Settings
from sahi import AutoDetectionModel
from ultils.log import get_logger

log = get_logger("SahiModel")

class BuildSahiModel:
    def __init__(self):
        log.debug("BuildSahiModel created")

    def build_sahi_model(self):
        log.info(
            f"Building SAHI model | path={Settings.YOLO_MODEL_PATH} "
            f"| conf={Settings.SAHI_CONFIDENCE} | device={Settings.DEVICE}"
        )
        model = AutoDetectionModel.from_pretrained(
            model_type="ultralytics",
            model_path=Settings.YOLO_MODEL_PATH,
            confidence_threshold=Settings.SAHI_CONFIDENCE,
            device=Settings.DEVICE
        )
        log.info("SAHI model built OK")
        return model