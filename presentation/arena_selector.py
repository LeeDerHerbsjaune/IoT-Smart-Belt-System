import tkinter as tk


class AreaSelector:
    """
    Phiên bản dùng thanh trượt (Scale) để chỉnh vùng chọn (hình chữ nhật)
    thay vì click 4 điểm trên canvas.

    Vẫn giữ API tương thích với bản cũ:
        - start()
        - clear()
        - polygon (property, trả về list 4 điểm góc)
        - contains(point)
        - state.is_setting / state.beset
    """

    def __init__(self, canvas, state, control_parent=None,
                 canvas_width=None, canvas_height=None):

        self.canvas = canvas
        self.state = state

        # Nếu không truyền parent riêng cho thanh trượt thì đặt cùng canvas
        self.control_parent = control_parent or canvas.master

        # Kích thước canvas để giới hạn thanh trượt
        self.canvas_width = canvas_width or int(canvas["width"])
        self.canvas_height = canvas_height or int(canvas["height"])

        # Biến lưu vị trí & kích thước vùng chọn (hình vuông)
        self.var_x = tk.IntVar(value=50)
        self.var_y = tk.IntVar(value=50)
        self.var_size = tk.IntVar(value=150)

        self.sliders = []
        self._build_sliders()

        # Mặc định khoá sliders cho tới khi bấm "Set Area"
        self.set_sliders_enabled(False)

    # ==========================================
    # TẠO THANH TRƯỢT
    # ==========================================

    def _build_sliders(self):

        self.frame = tk.Frame(self.control_parent)

        def make_slider(label, var, max_value):
            row = tk.Frame(self.frame)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=label, width=8, anchor="w").pack(side="left")

            slider = tk.Scale(
                row,
                from_=0,
                to=max_value,
                orient="horizontal",
                variable=var,
                command=lambda _=None: self.redraw(),
            )
            slider.pack(side="left", fill="x", expand=True)
            self.sliders.append(slider)
            return slider

        max_size = min(self.canvas_width, self.canvas_height)

        make_slider("X", self.var_x, self.canvas_width)
        make_slider("Y", self.var_y, self.canvas_height)
        make_slider("Size", self.var_size, max_size)

    def pack_controls(self, **kwargs):
        """Gọi hàm này để hiển thị panel thanh trượt (giống .pack() bình thường)."""
        self.frame.pack(**kwargs)

    def set_sliders_enabled(self, enabled):
        """Bật/tắt khả năng kéo cả 3 thanh trượt."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for slider in self.sliders:
            slider.config(state=state)

    # ==========================================
    # START
    # ==========================================

    def start(self):

        self.state.is_setting = True
        self.set_sliders_enabled(True)
        self.redraw()
        print("Kéo thanh trượt để chỉnh vùng chọn")

    # ==========================================
    # VẼ LẠI VÙNG CHỌN
    # ==========================================

    def redraw(self):

        if not self.state.is_setting:
            return

        self.canvas.delete("point")
        self.canvas.delete("polygon")

        x1, y1, x2, y2 = self._get_bounds()

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="green",
            width=2,
            tags="polygon"
        )

        for i, (px, py) in enumerate(self.polygon, start=1):
            self.draw_point(px, py, i)

        self.state.beset = True

    def _get_bounds(self):
        x1 = self.var_x.get()
        y1 = self.var_y.get()
        size = self.var_size.get()
        x2 = x1 + size
        y2 = y1 + size
        return x1, y1, x2, y2

    # ==========================================
    # VẼ ĐIỂM (giữ để tương thích, đánh dấu 4 góc)
    # ==========================================

    def draw_point(self, x, y, index):

        r = 5

        self.canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill="red",
            outline="white",
            width=2,
            tags="point"
        )

        self.canvas.create_text(
            x + 10,
            y - 10,
            text=str(index),
            fill="yellow",
            font=("Arial", 10, "bold"),
            tags="point"
        )

    # ==========================================
    # CLEAR
    # ==========================================

    def clear(self):

        self.state.is_setting = False
        self.state.beset = False

        self.set_sliders_enabled(False)

        self.canvas.delete("point")
        self.canvas.delete("polygon")

    # ==========================================
    # GET POLYGON (4 góc hình chữ nhật, theo chiều kim đồng hồ)
    # ==========================================

    @property
    def polygon(self):

        x1, y1, x2, y2 = self._get_bounds()

        return [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
        ]

    # ==========================================
    # CHECK POINT INSIDE (đơn giản hoá vì là hình chữ nhật)
    # ==========================================

    def contains(self, point):

        if self.var_size.get() <= 0:
            return False

        x, y = point
        x1, y1, x2, y2 = self._get_bounds()

        return x1 <= x <= x2 and y1 <= y <= y2