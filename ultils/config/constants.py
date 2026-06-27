from domain.domain.entities import Slot
W_PRODUCTS = ['W-Cpolygon', 'W-Circle', 'W-S-Circle', 'W-Trapezoid', 'W-Square']

SQUARE_PRODUCTS = ['W-Square', 'R-Square']


TRIGGER_PRODUCTS = W_PRODUCTS

STRICT_MATCH = True
NUM_INSPECTION_FRAMES = 3

STEP_MOVE_TIME = 0.15  

'''hằng số sử dụng cho việc duyệt labels và so sánh với chuẩn
    STANDARD_LAYOUT dùng làm khoảng cách chuẩn theo tỷ lệ
    ERR cho phép có mỗi lần duyệt mảng
    VOTING 
'''

STANDARD_LAYOUT = [

    Slot(
        "R-Circle",
        -80,
        -40
    ),

    Slot(
        "R-Circle",
        80,
        -40
    ),

    Slot(
        "Polygon",
        0,
        20
    ),

    Slot(
        "W-Circle",
        -70,
        80
    ),

    Slot(
        "W-Circle",
        70,
        80
    )
]
POSITION_ERR_X = 0.1
POSITION_ERR_Y = 0.1

POSITION_VOTING_FRAMES = 10
POSITION_PASS_RATIO = 0.5