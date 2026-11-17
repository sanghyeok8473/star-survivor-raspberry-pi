
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
        self.hud_font = ImageFont.load_default(size=12)

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

    def draw_static_background(
        self, score=0, lives=3, level=1,
        show_start_message=True
    ):
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

        # 점수 표시
        draw.text(
            (10, 35), f"SCORE: {score:04d}",
            font=self.hud_font, fill=self.YELLOW
        )

        # 현재 레벨 표시
        level_text = f"LV.{level}"

        bbox = draw.textbbox(
            (0, 0), level_text, font=self.hud_font
        )

        text_width = bbox[2] - bbox[0]

        draw.text(
            (139 - text_width // 2, 35),
            level_text,
            font=self.hud_font,
            fill=self.CYAN
        )

        # 체력 표시: 하트 3개
        self.draw = draw

        for i in range(3):
            color = self.RED if i < lives else (60, 60, 60)
            self.draw_heart(170 + i * 18, 35, color)

        draw.line(
            (10, 215, 230, 215),
            fill=self.CYAN, width=1
        )

        if show_start_message:
            message = "PRESS A TO START"

            bbox = draw.textbbox((0, 0), message, font=self.font)
            text_width = bbox[2] - bbox[0]

            x = (self.WIDTH - text_width) // 2

            draw.text(
                (x, 224),
                message,
                font=self.font,
                fill=self.WHITE
            )

        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

    def clear_start_message(self):
        """게임 시작 시 하단 안내 문구 제거"""

        box = (0, 216, self.WIDTH, self.HEIGHT)

        background_draw = ImageDraw.Draw(self.background)
        background_draw.rectangle(box, fill=self.BLACK)

        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        self.draw = ImageDraw.Draw(self.image)
        self._show_region(box)

    def draw_heart(self, x, y, color):
        """하트 아이콘 출력"""

        self.draw.ellipse(
            (x, y, x + 7, y + 7),
            fill=color
        )

        self.draw.ellipse(
            (x + 6, y, x + 13, y + 7),
            fill=color
        )

        self.draw.polygon(
            [
                (x, y + 4),
                (x + 13, y + 4),
                (x + 6, y + 13)
            ],
            fill=color
        )

    def update_lives(self, lives):
        """남은 목숨에 따라 하트 영역만 갱신"""

        lives = max(0, min(3, lives))
        box = (168, 33, 224, 51)

        # 고정 배경의 하트 영역을 검은색으로 초기화
        background_draw = ImageDraw.Draw(self.background)
        background_draw.rectangle(box, fill=self.BLACK)

        # 배경에 현재 목숨 상태 반영
        self.draw = background_draw

        for i in range(3):
            color = self.RED if i < lives else (60, 60, 60)
            self.draw_heart(170 + i * 18, 35, color)

        # 실제 화면 버퍼에도 반영
        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        self.draw = ImageDraw.Draw(self.image)

        # 하트 영역만 LCD에 전송
        self._show_region(box)

    def update_score(self, score):
        """점수 표시 영역만 갱신"""

        box = (8, 32, 110, 52)

        background_draw = ImageDraw.Draw(self.background)
        background_draw.rectangle(box, fill=self.BLACK)

        background_draw.text(
            (10, 35),
            f"SCORE: {score:04d}",
            font=self.hud_font,
            fill=self.YELLOW
        )

        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        self.draw = ImageDraw.Draw(self.image)
        self._show_region(box)

    def update_level(self, level, visible=True, enlarged=False):
        """레벨 표시 및 레벨업 애니메이션"""

        box = (112, 29, 166, 53)

        # 기본 배경에는 항상 일반 크기의 레벨 표시 유지
        background_draw = ImageDraw.Draw(self.background)
        background_draw.rectangle(box, fill=self.BLACK)

        normal_text = f"LV.{level}"
        normal_font = self.hud_font

        normal_bbox = background_draw.textbbox(
            (0, 0), normal_text, font=normal_font
        )

        normal_width = normal_bbox[2] - normal_bbox[0]

        background_draw.text(
            (139 - normal_width // 2, 35),
            normal_text,
            font=normal_font,
            fill=self.CYAN
        )

        # 화면 표시 영역 초기화
        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        # 레벨업 중에는 기본 글씨를 지우고 확대 표시
        if enlarged:
            screen_draw = ImageDraw.Draw(self.image)
            screen_draw.rectangle(box, fill=self.BLACK)

            if visible:
                large_font = ImageFont.load_default(size=16)

                large_bbox = screen_draw.textbbox(
                    (0, 0), normal_text, font=large_font
                )

                large_width = large_bbox[2] - large_bbox[0]

                screen_draw.text(
                    (139 - large_width // 2, 32),
                    normal_text,
                    font=large_font,
                    fill=self.YELLOW
                )

        self.draw = ImageDraw.Draw(self.image)
        self._show_region(box)
    
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

    def draw_asteroid(self, x, y, radius):
        """소행성 출력"""
        x, y = int(x), int(y)

        self.draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(120, 115, 110),
            outline=(190, 180, 165),
            width=1
        )

        # 소행성 표면의 작은 크레이터
        self.draw.ellipse(
            (x - radius // 2, y - radius // 2,
            x, y),
            fill=(75, 70, 68)
        )

    def draw_energy_orb(self, x, y, radius):
        """에너지 구슬 출력"""

        x = int(x)
        y = int(y)

        # 바깥쪽 광채
        self.draw.ellipse(
            (
                x - radius - 2,
                y - radius - 2,
                x + radius + 2,
                y + radius + 2
            ),
            fill=(0, 65, 85)
        )

        # 구슬 본체
        self.draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),
            fill=(0, 220, 255)
        )

        # 중앙의 밝은 빛
        self.draw.ellipse(
            (x - 2, y - 2, x + 2, y + 2),
            fill=(220, 255, 255)
        )

    def initialize_game_screen(
        self, x, y, stars, score=0, lives=3,
        show_start_message=True, level=1
    ):
        """게임 화면 초기화"""

        self.draw_static_background(
            score, lives, level,
            show_start_message=show_start_message
        )

        for star in stars:
            self.draw_star(star["x"], star["y"], star["size"])

        self.draw_spaceship(x, y)

        self.disp.image(self.image)

    def _refresh_star_patch(self, x, y, size, 
                        player_x, player_y, draw_star=False):
        """별의 작은 영역만 복원하고 갱신"""

        left = max(0, x - 1)
        top = max(0, y - 1)
        right = min(self.WIDTH, x + size + 1)
        bottom = min(self.HEIGHT, y + size + 1)

        self.image.paste(
            self.background.crop((left, top, right, bottom)),
            (left, top)
        )

        self.draw = ImageDraw.Draw(self.image)

        if draw_star:
            self.draw_star(x, y, size)

        # 우주선이 겹치는 영역이면 우주선을 다시 출력
        if player_x is not None and player_y is not None:
            overlap = (
                left < player_x + 12 and
                right > player_x - 12 and
                top < player_y + 13 and
                bottom > player_y - 16
            )

            if overlap:
                self.draw_spaceship(player_x, player_y)

        self._show_region((left, top, right, bottom))
    
    def update_star(self, old_x, old_y, new_x, new_y, size=2,
                    player_x=None, player_y=None):
        """별 이동 및 우주선 겹침 처리"""
        if abs(new_x - old_x) > 10 or abs(new_y - old_y) > 10:

            # 이전 위치의 별 제거
            self._refresh_star_patch(
                old_x, old_y, size,
                player_x, player_y,
                draw_star=False
            )

            # 새로운 위치에 별 출력
            self._refresh_star_patch(
                new_x, new_y, size,
                player_x, player_y,
                draw_star=True
            )

            return


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

    def update_game_objects(
        self, regions, stars, asteroids,
        player_x, player_y, show_player=True, orbs=None, level_up_level=None
    ):
        """변경된 작은 영역만 복원하고 모든 객체를 올바른 순서로 다시 그림"""

        if not regions:
            return

        # 겹치거나 맞닿는 영역만 병합
        merged = []

        for region in regions:
            left = max(0, int(region[0]))
            top = max(50, int(region[1]))
            right = min(self.WIDTH, int(region[2]))
            bottom = min(215, int(region[3]))

            if left >= right or top >= bottom:
                continue

            merged.append((left, top, right, bottom))

        changed = True

        while changed:
            changed = False

            for i in range(len(merged)):
                if changed:
                    break

                for j in range(i + 1, len(merged)):
                    a = merged[i]
                    b = merged[j]

                    overlap = (
                        a[0] <= b[2] and a[2] >= b[0]
                        and a[1] <= b[3] and a[3] >= b[1]
                    )

                    if overlap:
                        merged[i] = (
                            min(a[0], b[0]),
                            min(a[1], b[1]),
                            max(a[2], b[2]),
                            max(a[3], b[3])
                        )
                        merged.pop(j)
                        changed = True
                        break

        # 영역별로 배경을 복원하고 객체를 다시 그림
        for left, top, right, bottom in merged:
            self.image.paste(
                self.background.crop((left, top, right, bottom)),
                (left, top)
            )

            self.draw = ImageDraw.Draw(self.image)

            for star in stars:
                x = int(star["x"])
                y = int(star["y"])
                size = star["size"]

                if (
                    left < x + size and right > x
                    and top < y + size and bottom > y
                ):
                    self.draw_star(x, y, size)

            for asteroid in asteroids:
                x = int(asteroid.x)
                y = int(asteroid.y)
                r = asteroid.radius

                if (
                    left < x + r + 1 and right > x - r
                    and top < y + r + 1 and bottom > y - r
                ):
                    self.draw_asteroid(x, y, r)

            # 에너지 구슬 출력
            for orb in (orbs or []):
                x = int(orb.x)
                y = int(orb.y)
                r = orb.radius + 2

                if (
                    left < x + r + 1
                    and right > x - r
                    and top < y + r + 1
                    and bottom > y - r
                ):
                    self.draw_energy_orb(x, y, orb.radius)

            # 우주선은 항상 최상위 레이어
            if (
                show_player and left < player_x + 12 and right > player_x - 12
                and top < player_y + 13 and bottom > player_y - 16
            ):
                self.draw_spaceship(player_x, player_y)
            
            self._show_region((left, top, right, bottom))

    def show_game_over(self, score, level):
        """게임 종료 화면 출력"""

        self.image = Image.new(
            "RGB",
            (self.WIDTH, self.HEIGHT),
            self.BLACK
        )

        self.draw = ImageDraw.Draw(self.image)

        title_font = ImageFont.load_default(size=25)
        info_font = ImageFont.load_default(size=16)

        def centered_text(y, text, font, color):
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2

            self.draw.text(
                (x, y),
                text,
                font=font,
                fill=color
            )

        centered_text(48, "GAME OVER", title_font, self.RED)
        centered_text(105, f"SCORE: {score:04d}", info_font, self.YELLOW)
        centered_text(135, f"LEVEL: {level}", info_font, self.CYAN)

        self.draw.line(
            (25, 175, 215, 175),
            fill=self.CYAN,
            width=1
        )

        centered_text(
            193,
            "PRESS A TO RESTART",
            self.font,
            self.WHITE
        )

        self.disp.image(self.image)

    def shutdown(self):
        """LCD 백라이트 종료"""

        self.backlight.value = False
