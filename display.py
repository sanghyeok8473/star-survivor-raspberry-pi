
import board
import digitalio
import adafruit_rgb_display.st7789

from PIL import Image, ImageDraw, ImageFont


class Display:
    """LCD 초기화 및 게임 화면 출력을 담당하는 클래스"""

    WIDTH = 240
    HEIGHT = 240

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CYAN = (0, 220, 255)
    YELLOW = (255, 220, 50)
    RED = (255, 70, 70)

    def __init__(self):
        spi = board.SPI()

        self.cs_pin = digitalio.DigitalInOut(board.CE0)
        self.dc_pin = digitalio.DigitalInOut(board.D25)
        self.reset_pin = digitalio.DigitalInOut(board.D24)

        self.disp = adafruit_rgb_display.st7789.ST7789(
            spi,
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            width=self.WIDTH,
            height=self.HEIGHT,
            y_offset=80,
            rotation=180,
            baudrate=24000000
        )

        self.backlight = digitalio.DigitalInOut(board.D26)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = True

        self.image = Image.new(
            "RGB", (self.WIDTH, self.HEIGHT), self.BLACK
        )

        self.background = Image.new(
            "RGB", (self.WIDTH, self.HEIGHT), self.BLACK
        )

        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def _show_region(self, box):
        """지정한 영역만 LCD에 전송"""

        left, top, right, bottom = box

        left = max(0, left)
        top = max(0, top)
        right = min(self.WIDTH, right)
        bottom = min(self.HEIGHT, bottom)

        if left >= right or top >= bottom:
            return

        patch = self.image.crop((left, top, right, bottom))

        # LCD rotation=180에 맞춰 이미지와 좌표 변환
        patch = patch.rotate(180)

        self.disp.image(
            patch,
            rotation=0,
            x=self.WIDTH - right,
            y=self.HEIGHT - bottom
        )

    def draw_static_background(self, score=0, hp=100):
        """고정 HUD와 기본 배경 생성"""

        self.background = Image.new(
            "RGB", (self.WIDTH, self.HEIGHT), self.BLACK
        )

        draw = ImageDraw.Draw(self.background)

        draw.text(
            (55, 8), "STAR SURVIVOR",
            font=self.font, fill=self.CYAN
        )

        draw.line(
            (10, 27, 230, 27),
            fill=self.CYAN, width=1
        )

        draw.text(
            (10, 35), f"SCORE: {score:04d}",
            font=self.font, fill=self.YELLOW
        )

        draw.text(
            (155, 35), f"HP: {hp}",
            font=self.font, fill=self.RED
        )

        draw.line(
            (10, 215, 230, 215),
            fill=self.CYAN, width=1
        )

        draw.text(
            (65, 224), "READY TO START",
            font=self.font, fill=self.WHITE
        )

        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

    def draw_spaceship(self, x, y):
        """우주선 출력"""

        self.draw.polygon(
            [
                (x, y - 15),
                (x - 11, y + 12),
                (x, y + 7),
                (x + 11, y + 12)
            ],
            fill=self.CYAN
        )

        self.draw.ellipse(
            (x - 3, y - 5, x + 3, y + 2),
            fill=self.WHITE
        )

    def draw_star(self, x, y, size=2):
        """별 출력"""

        self.draw.ellipse(
            (x, y, x + size - 1, y + size - 1),
            fill=self.WHITE
        )

    def initialize_game_screen(self, x, y, stars, score=0, hp=100):
        """게임 시작 시 전체 화면 한 번 출력"""

        self.draw_static_background(score, hp)

        for star in stars:
            self.draw_star(star["x"], star["y"], star["size"])

        self.draw_spaceship(x, y)

        self.disp.image(self.image)

    
    def update_star(self, old_x, old_y, new_x, new_y, size=2,
                    player_x=None, player_y=None):
        """별 이동 및 우주선 겹침 처리"""

        left = min(old_x, new_x) - 1
        top = min(old_y, new_y) - 1
        right = max(old_x, new_x) + size + 1
        bottom = max(old_y, new_y) + size + 1

        # 별의 이전 위치를 배경으로 복원
        self.image.paste(
            self.background.crop((left, top, right, bottom)),
            (left, top)
        )

        self.draw = ImageDraw.Draw(self.image)

        # 이동한 별 출력
        self.draw_star(new_x, new_y, size)

        # 별 갱신 영역과 우주선 영역이 겹치는지 확인
        if player_x is not None and player_y is not None:
            ship_left = player_x - 12
            ship_top = player_y - 16
            ship_right = player_x + 12
            ship_bottom = player_y + 13

            overlap = (
                left < ship_right and
                right > ship_left and
                top < ship_bottom and
                bottom > ship_top
            )

            # 겹치면 우주선을 가장 마지막에 다시 그림
            if overlap:
                self.draw_spaceship(player_x, player_y)

        self._show_region((left, top, right, bottom))

    def update_spaceship(self, old_x, old_y, new_x, new_y):
        """우주선의 이전 위치를 지우고 새 위치 출력"""

        left = min(old_x, new_x) - 12
        top = min(old_y, new_y) - 16
        right = max(old_x, new_x) + 13
        bottom = max(old_y, new_y) + 13

        left = max(0, left)
        top = max(0, top)
        right = min(self.WIDTH, right)
        bottom = min(self.HEIGHT, bottom)

        self.image.paste(
            self.background.crop((left, top, right, bottom)),
            (left, top)
        )

        self.draw = ImageDraw.Draw(self.image)
        self.draw_spaceship(new_x, new_y)

        self._show_region((left, top, right, bottom))

    def shutdown(self):
        """LCD 백라이트 종료"""

        self.backlight.value = False
