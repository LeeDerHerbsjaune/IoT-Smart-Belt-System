# IoT Smart Belt System

An IoT system for a "smart belt" that combines camera streams, object detection models (YOLO / Faster R-CNN / SAHI), and an ESP32 microcontroller to control hardware (motors/actuators). The application provides a Tkinter-based GUI for configuration, camera monitoring, arena selection, and controlling/receiving data from the ESP32.

## Key Features

- Tkinter GUI for control and visualization.
- Camera streaming and image-processing pipeline with support for multiple detection backends (YOLO, Faster R-CNN, SAHI).
- ESP32 connectivity and control (serial/client interfaces) for actuators.
- Modular services: camera_service, detection_service, esp32_service.
- Packaging support via PyInstaller (`main.spec`) and helper scripts (`build.py`, `build.bat`).

## Stack

- Language: Python (primary)
- GUI: Tkinter
- Detection frameworks: YOLO / Faster R-CNN / SAHI (third-party libraries; may require PyTorch or framework-specific packages)
- Hardware communication: Serial / Client for ESP32

## Suggested Requirements

This repository does not include a complete `requirements.txt`. The following packages are commonly needed; adjust according to the detection backend you use:

- Python 3.8+
- numpy
- opencv-python
- pillow
- torch, torchvision (if using PyTorch-based models)
- sahi
- pyserial (for ESP32 serial communication)
- Any YOLO-specific packages (e.g., yolov5) if used

Example setup:

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install numpy opencv-python pillow torch torchvision sahi pyserial
```

Consider adding a `requirements.txt` to the repository to lock dependencies.

## Quick start (run)

From a fresh clone, after installing dependencies and configuring your environment:

```bash
# run the main application
python main.py
```

Packaging with PyInstaller:

```bash
pyinstaller main.spec
# or use the provided build scripts (if configured):
python build.py
# on Windows
build.bat
```

## Project structure

```
application/
  services/        # Business services: camera_service.py, detection_service.py, esp32_service.py
  state/           # Application state management (APPstate.py)

domain/
  domain/          # Domain models / business entities (if any)

infrastructure/
  camera/          # Camera stream interfaces and helpers
  esp32/           # ESP32 client and communication helpers
  fasterRCNN/      # Faster R-CNN integration (if present)
  sahi/            # SAHI integration
  yolo/            # YOLO integration

presentation/
  gui.py           # Main GUI (Tkinter)
  controller_*     # Controllers for camera, ESP32, and main flow
  arena_selector.py# Arena selection UI

ultils/
  geometry.py
  log.py
  config/          # Configuration files and helpers

main.py            # Entrypoint: initializes services, controllers, and GUI
main.spec          # PyInstaller specification
build.py / build.bat# Build/packaging scripts
logs/               # Application logs
```

## How it works (overview)

- `main.py` creates the AppState and initializes the main services and controllers, then starts the Tkinter GUI loop.
- The GUI lets a user select a camera, choose an arena (region of interest), and enable/disable detection and control flows.
- `camera_service` provides image frames to the pipeline; `detection_service` runs the selected model and returns detections; `esp32_service` sends commands to the ESP32 (e.g., to move actuators) based on application logic.
- Detection backends live under `infrastructure/` and can be swapped based on configuration.

## Configuration

- Check `ultils/config/` and `ultils/run_info.json` for existing settings (camera addresses, ESP32 port, detection parameters, etc.).
- Add a `requirements.txt` and a clearer configuration file (e.g., `config.yaml` or `.env`) for easier setup.
- Ensure model weight files and paths are placed where the detection modules expect them or update the configuration paths.

## Development notes

- Create a `requirements.txt` to simplify environment setup for contributors.
- Detection modules may require pretrained weights—document where to download them and where to place them.
- Add unit or integration tests for critical services where feasible.

## Contributing

- Open an issue for bugs or feature requests.
- Submit pull requests with a description of changes and testing instructions.

## License

No license file was detected in the repository. Add a LICENSE file (for example MIT, Apache-2.0) to clarify terms.

## Author

LeeDerHerbsjaune
