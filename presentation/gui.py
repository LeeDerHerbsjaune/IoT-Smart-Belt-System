import tkinter as tk
from PIL import Image, ImageTk
from presentation.arena_selector import AreaSelector
class GUI:
# =============================================================================================================== #
#                                                  GUI SETUP                                                      #
# =============================================================================================================== #             
    def __init__(self, root, controller, usecase, state):
        self.root = root
        self.controller = controller
        self.state = state
        self.usecase = usecase
        self.setup_window()
        self.setup_gui()
        self.render_all()
        self.render_area()
    # =========================================================
    # WINDOW
    # =========================================================

    def setup_window(self):

        self.root.title("YOLO Conveyor System")

        self.root.geometry("1200x700")

    # =========================================================
    # GUI
    # =========================================================

    def setup_gui(self):

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------
        # LEFT PANEL
        # -------------------------------------------------

        left_panel = tk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #=====================================================================================================
        # Camera Canvas =====================================================
        #=====================================================================================================
        self.camera_canvas = tk.Canvas(
            left_panel,
            width=800,
            height=500,
            bg="black"
        )

        self.camera_canvas.pack(padx=10, pady=10)
        self.canvas_image = self.camera_canvas.create_image(0, 0, anchor=tk.NW)

        camera_controls = tk.Frame(left_panel)
        camera_controls.pack(fill=tk.X, padx=10)

        url_camera_label = tk.Label(camera_controls, text="Camera URL:")
        url_camera_label.pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(camera_controls)

        self.url_entry.insert(0, "Index camera or URL")

        self.url_entry.pack(fill=tk.X, padx=5, pady=5)

        self.start_camera_btn = tk.Button(
            camera_controls,
            text="Start Camera",
            command=lambda: self.controller.camera.on_start_clicked(self.url_entry.get()),
            bg="#757575",
            fg="white",
            padx=10,
            pady=5
        )

        self.start_camera_btn.pack(side=tk.LEFT, padx=5)

        self.stop_camera_btn = tk.Button(
            camera_controls,
            text="Stop Camera",
            command=self.controller.camera.on_stop_clicked,
            bg="#666666",
            fg="white",
            padx=10,
            pady=5
        )

        self.stop_camera_btn.pack(side=tk.LEFT, padx=5)
        #=====================================================================================================
        # Conveyor Controls =====================================================
        #=====================================================================================================

        conveyor_controls = tk.Frame(left_panel)
        conveyor_controls.pack(fill=tk.X, padx=10, pady=10)

        self.start_conveyor_btn = tk.Button(
            conveyor_controls,
            text="START",
            command=lambda: self.controller.conveyor.on_start_clicked(),
            bg="#636463",
            fg="white",
            padx=20,
            pady=8
        )

        self.start_conveyor_btn.pack(side=tk.LEFT, padx=5)

        self.stop_conveyor_btn = tk.Button(
            conveyor_controls,
            text="STOP",
            command=lambda: self.controller.conveyor.on_stop_clicked(),
            bg="#525252",
            fg="white",
            padx=20,
            pady=8
        )

        self.stop_conveyor_btn.pack(side=tk.LEFT, padx=5)

        # # -------------------------------------------------
        # # RIGHT PANEL
        # # -------------------------------------------------

        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Connection Section

        connection_frame = tk.LabelFrame(
            right_panel,
            text="ESP32 Connection"
        )

        connection_frame.pack(fill=tk.X, padx=10, pady=10)

        self.ip_entry = tk.Entry(connection_frame)

        self.ip_entry.insert(0, "192.168.1.100")

        self.ip_entry.pack(fill=tk.X, padx=5, pady=5)

        self.connect_btn = tk.Button(
            connection_frame,
            text="Connect",
            command=lambda: self.controller.conveyor.on_connect_clicked(self.ip_entry.get()),
            bg="#535353",
            fg="white"
        )

        self.connect_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.test_model_btn = tk.Button(
            connection_frame,
            text="Test Model",
            command=lambda: self.controller.conveyor.on_test_model_clicked(),
            bg="#535353",
            fg="white"
        )

        self.test_model_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.disconnect_btn = tk.Button(
            connection_frame,
            text="Disconnect",
            command=lambda: self.controller.conveyor.on_disconnect_clicked(),
            bg="#575757",
            fg="white"
        )

        self.disconnect_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Area Selection Section (chuyển từ left_panel sang đây)

        area_frame = tk.LabelFrame(
            right_panel,
            text="Set Arena"
        )

        area_frame.pack(fill=tk.X, padx=10, pady=10)

        self.arena_selector = AreaSelector(
            self.camera_canvas,
            self.state,
            control_parent=area_frame,
            canvas_width=800,
            canvas_height=500
        )
        self.arena_selector.pack_controls(fill=tk.X, padx=5, pady=5)

        area_buttons = tk.Frame(area_frame)
        area_buttons.pack(fill=tk.X, padx=5, pady=5)

        self.select_btn = tk.Button(
            area_buttons,
            text="Set Area",
            command=self.arena_selector.start,
            bg="#686a69",
            fg="white",
            padx=10,
            pady=5
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(
            area_buttons,
            text="Clear Area",
            command=self.arena_selector.clear,
            bg="#7d7d7d",
            fg="white",
            padx=10,
            pady=5
        )

        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Detected Labels Section — hiện nhãn ngay trên camera, không dùng khung text riêng

        labels_frame = tk.LabelFrame(
            right_panel,
            text="Detected Labels"
        )

        labels_frame.pack(fill=tk.X, padx=10, pady=10)

        self.labels_visible = False

        self.toggle_labels_btn = tk.Button(
            labels_frame,
            text="Show Labels on Camera",
            command=self.toggle_labels_display,
            bg="#535353",
            fg="white",
            padx=10,
            pady=5
        )
        self.toggle_labels_btn.pack(anchor=tk.W, padx=5, pady=5)

        # Status

        self.connection_status_label = tk.Label(
            right_panel,
            text=""
        )

        self.connection_status_label.pack(
            anchor=tk.W,
            padx=10,
            pady=5
        )

        self.camera_status_label = tk.Label(
            right_panel,
            text="Camera Stopped",
            bg="#575757",
            foreground="green" 
        )

        self.camera_status_label.pack(
            anchor=tk.W,
            padx=10,
            pady=5
        )

        self.conveyor_status_label = tk.Label(
            right_panel,
            text=""
        )

        self.conveyor_status_label.pack(
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.setting_area_label = tk.Label(
            right_panel,
            text=""
        )

        self.setting_area_label.pack(
            anchor=tk.W,
            padx=10,
            pady=5
        )    # =========================================================
    # RENDER
    # =========================================================

    def render_all(self):

        self.render_camera_state()
        self.render_connection_state()
        self.render_conveyor_state()
        self.render_area()

    # ---------------------------------------------------------

    def render_camera_state(self):
        if self.state.camera_running:
            self.start_camera_btn.config(
                state=tk.DISABLED
            )

            self.stop_camera_btn.config(
                state=tk.NORMAL
            )

            self.camera_status_label.config(
                text="Camera: Running", 
                foreground="green"
            )

        else:

            self.start_camera_btn.config(
                state=tk.NORMAL
            )

            self.stop_camera_btn.config(
                state=tk.DISABLED
            )

            self.camera_status_label.config(
                text="Camera: Stopped"
            )

    # ---------------------------------------------------------

    def render_connection_state(self):

        if self.state.esp32_connected:

            self.connect_btn.config(
                state=tk.DISABLED
            )

            self.disconnect_btn.config(
                state=tk.NORMAL
            )

            self.connection_status_label.config(
                text="ESP32: Connected",
                foreground="green"
            )

        else:

            self.connect_btn.config(
                state=tk.NORMAL
            )

            self.disconnect_btn.config(
                state=tk.DISABLED
            )

            self.connection_status_label.config(
                text="ESP32: Disconnected"
            )

    # ---------------------------------------------------------

    def render_conveyor_state(self):

        if self.state.conveyor_running:

            self.start_conveyor_btn.config(
                state=tk.DISABLED
            )

            self.stop_conveyor_btn.config(
                state=tk.NORMAL
            )

            self.conveyor_status_label.config(
                text="Conveyor: Running"
            )

        else:

            self.start_conveyor_btn.config(
                state=tk.NORMAL
            )

            self.stop_conveyor_btn.config(
                state=tk.DISABLED
            )

            self.conveyor_status_label.config(
                text="Conveyor: Stopped"
            )
    def start_ui_loop(self):

        self.update_frame()
        self.update_ui()
        self.root.after(
            30,
            self.start_ui_loop
        )
    def update_ui(self):

        self.render_camera_state()
        self.render_connection_state()
        self.render_conveyor_state()
        self.render_area()
        self.render_labels()

        self.render_frame()
    def update_frame(self):

        frame = self.state.current_frame

        polygon = self.arena_selector.polygon

        self.usecase.process(frame=frame, polygon=polygon)
    def render_frame(self):

        with self.state.frame_lock:

            frame = self.state.current_frame

        if frame is None:
            return

        image = Image.fromarray(frame)

        photo = ImageTk.PhotoImage(image)

        self.camera_canvas.itemconfig(
            self.canvas_image,
            image=photo
        )

        self.camera_canvas.image = photo
    def render_area(self):
        if self.state.beset:
            self.select_btn.config(
                state=tk.DISABLED
            )

            self.clear_btn.config(
                state=tk.NORMAL
            )

            self.setting_area_label.config(
                text="Arena: Set"
            )
        else:
            self.select_btn.config(
                state=tk.NORMAL
            )

            self.clear_btn.config(
                state=tk.DISABLED
            )

            self.setting_area_label.config(
                text="Arena: Not set"
            )

    # ---------------------------------------------------------

    def toggle_labels_display(self):

        self.labels_visible = not self.labels_visible

        if self.labels_visible:
            self.toggle_labels_btn.config(text="Hide Labels on Camera")
            self.render_labels()
        else:
            self.toggle_labels_btn.config(text="Show Labels on Camera")
            self.camera_canvas.delete("detected_label")

    def render_labels(self):

        self.camera_canvas.delete("detected_label")

        if not self.labels_visible:
            return

        for item in self.state.detected_labels:

            label = item.get("label")
            center = item.get("center")
            bbox = item.get("bbox")

            if bbox is not None:
                x1, y1, x2, y2 = bbox
                self.camera_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="cyan",
                    width=2,
                    tags="detected_label"
                )
                text_x, text_y = x1, y1 - 10
            elif center is not None:
                text_x, text_y = center[0], center[1] - 10
            else:
                continue

            self.camera_canvas.create_text(
                text_x, text_y,
                text=str(label),
                fill="cyan",
                font=("Arial", 11, "bold"),
                tags="detected_label",
                anchor="sw"
            )