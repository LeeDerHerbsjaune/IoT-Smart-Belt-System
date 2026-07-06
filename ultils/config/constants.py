# Nhãn dùng làm anchor trigger (Square luôn có độ tin cậy cao nhất)
SQUARE_PRODUCTS = ['W-Square', 'R-Square']

# Chỉ kiểm tra sản phẩm đúng (R-*) — W-* là sản phẩm lỗi, không đưa vào reference
RIGHT_PRODUCTS = ['R-Cpolygon', 'R-Circle', 'R-S-Circle', 'R-Trapezoid', 'R-Square']

# Thời gian mỗi bước di chuyển băng tải (giây)
STEP_MOVE_TIME = 0.15

# Số frame dùng để voting
POSITION_VOTING_FRAMES = 10

# Sai số cho phép theo pixel (tuyệt đối)
POSITION_ERR_X = 15
POSITION_ERR_Y = 15

# Tỉ lệ frame tối thiểu để pass (>50%)
POSITION_PASS_RATIO = 0.5