import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

_BASE_DIR   = Path(__file__).parent
_RUN_INFO   = _BASE_DIR / "run_info.json"
_LOG_DIR    = _BASE_DIR.parent / "logs"
_RUN_ID: str | None = None

LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(run_id)s] "
    "[PID:%(process)d] "
    "[%(levelname)-7s] "
    "[%(name)-20s] "
    "%(message)s"
)


class _MillisFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime("%H:%M:%S") + f".{ct.microsecond // 1000:03d}"


class _RunFilter(logging.Filter):
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id

    def filter(self, record):
        record.run_id = self.run_id
        return True


def _resolve_run_id() -> tuple[str, str, int]:
    """Tính run_id đúng 1 lần cho toàn bộ process."""
    global _RUN_ID
    if _RUN_ID is not None:
        day, num = _RUN_ID.split("#")
        return _RUN_ID, day, int(num)

    today = datetime.now().strftime("%Y-%m-%d")

    if not _RUN_INFO.exists():
        data = {"date": today, "count": 1}
    else:
        data = json.loads(_RUN_INFO.read_text(encoding="utf-8"))
        data = {"date": today, "count": data["count"] + 1} \
            if data["date"] == today \
            else {"date": today, "count": 1}

    _RUN_INFO.write_text(json.dumps(data), encoding="utf-8")
    _RUN_ID = f"{today}#{data['count']:03d}"
    return _RUN_ID, today, data["count"]


def _make_handlers(run_id: str, log_path: Path) -> list[logging.Handler]:
    fmt = _MillisFormatter(LOG_FORMAT)
    rf  = _RunFilter(run_id)

    # Console — INFO trở lên (không spam DEBUG khi chạy)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    console.addFilter(rf)

    # File — DEBUG đầy đủ để xem lại sau
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    fh.addFilter(rf)

    return [console, fh]


_HANDLERS_READY = False


def get_logger(name: str) -> logging.Logger:
    global _HANDLERS_READY

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    run_id, day, count = _resolve_run_id()

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = _LOG_DIR / f"{day}_run{count:03d}.log"

    for h in _make_handlers(run_id, log_path):
        logger.addHandler(h)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Header chỉ in 1 lần đầu tiên trong session
    if not _HANDLERS_READY:
        _HANDLERS_READY = True
        logger.info("=" * 60)
        logger.info(f"SESSION START  run={run_id}  pid={os.getpid()}")
        logger.info(f"Log file → {log_path}")
        logger.info("=" * 60)

    return logger