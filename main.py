
import time
import board
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789


# ========================================
# 1. LCD 초기화
# ========================================

spi = board.SPI()

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

disp = adafruit_rgb_display.st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=240,
    height=240,
    y_offset=80,
    rotation=180,
    baudrate=24000000
)

# 백라이트 설정
backlight = digitalio.DigitalInOut(board.D26)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True


# ========================================
# 2. 화면 및 폰트 설정
# ========================================

WIDTH = 240
HEIGHT = 240

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 50)
RED = (255, 70, 70)

image = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
draw = ImageDraw.Draw(image)

font_title = ImageFont.load_default()
font_ui = ImageFont.load_default()


# ========================================
# 3. 우주 배경
# ========================================

def draw_background():
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)

    stars = [
        (15, 25), (65, 45), (110, 20),
        (180, 35), (220, 65), (35, 100),
        (90, 85), (155, 110), (205, 130),
        (20, 170), (75, 195), (180, 185),
        (225, 215), (120, 225)
    ]

    for x, y in stars:
        draw.point((x, y), fill=WHITE)


# ========================================
# 4. 우주선 그리기
# ========================================

def draw_spaceship(x, y):
    # 우주선 본체
    draw.polygon(
        [
            (x, y - 15),
            (x - 11, y + 12),
            (x, y + 7),
            (x + 11, y + 12)
        ],
        fill=CYAN
    )

    # 조종석
    draw.ellipse(
        (x - 3, y - 5, x + 3, y + 2),
        fill=WHITE
    )


# ========================================
# 5. 게임 화면 출력
# ========================================

def draw_game_screen():
    draw_background()

    # 상단 제목
    draw.text(
        (55, 8),
        "STAR SURVIVOR",
        font=font_title,
        fill=CYAN
    )

    # 구분선
    draw.line((10, 27, 230, 27), fill=CYAN, width=1)

    # 점수와 체력
    draw.text((10, 35), "SCORE: 0000", font=font_ui, fill=YELLOW)
    draw.text((155, 35), "HP: 100", font=font_ui, fill=RED)

    # 우주선 초기 위치
    draw_spaceship(120, 170)

    # 하단 안내
    draw.line((10, 215, 230, 215), fill=CYAN, width=1)
    draw.text((65, 224), "READY TO START", font=font_ui, fill=WHITE)

    disp.image(image)


# ========================================
# 6. 실행
# ========================================

if __name__ == "__main__":
    try:
        draw_game_screen()
        print("STAR SURVIVOR 화면 출력 완료")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("게임 화면 종료")

    finally:
        backlight.value = False
