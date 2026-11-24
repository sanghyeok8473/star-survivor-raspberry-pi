
import board
import digitalio
import adafruit_rgb_display.st7789
import math

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
        self.boss_font = ImageFont.load_default(size=10)

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
        self.skill_cooldown_remaining = 0.0
        self.skill_font = ImageFont.load_default(size=15)
        self.level_up_font = ImageFont.load_default(size=16)
        self.shield_color = (80, 255, 160)

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

        # 시작 안내 문구를 지운 후 스킬 아이콘 다시 표시
        self.update_skill_icon(0)

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

    def update_weapon_level(self, weapon_level):
        """화면 하단 무기 레벨 및 강화 게이지 갱신"""

        weapon_level = max(1, min(6, weapon_level))

        box = (0, 216, self.WIDTH, self.HEIGHT)

        background_draw = ImageDraw.Draw(self.background)

        # 기존 하단 영역 초기화
        background_draw.rectangle(
            (0, 216, self.WIDTH - 1, self.HEIGHT - 1),
            fill=self.BLACK
        )

        # 무기 레벨 텍스트
        weapon_text = (
            "WEAPON MAX"
            if weapon_level == 6
            else f"WEAPON LV.{weapon_level}"
        )

        background_draw.text(
            (10, 222),
            weapon_text,
            font=self.hud_font,
            fill=(210, 170, 255)
        )

        # 무기 강화 게이지 6칸
        for i in range(6):
            x = 124 + i * 18

            color = (
                (180, 100, 255)
                if i < weapon_level
                else (35, 35, 45)
            )

            background_draw.rectangle(
                (x, 222, x + 13, 233),
                fill=color,
                outline=(110, 80, 140)
            )

        # 화면 버퍼에 반영
        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        self.draw = ImageDraw.Draw(self.image)

        # 하단 HUD 영역만 LCD에 전송
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
                large_font = self.level_up_font

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

    def draw_skill_icon_overlay(self):
        """현재 화면 버퍼에 스킬 아이콘 그리기 (LCD 전송 없음)"""

        cx, cy = 213, 191
        radius = 17

        draw = ImageDraw.Draw(self.image)

        cooling = self.skill_cooldown_remaining > 0

        outline = (75, 90, 100) if cooling else self.CYAN
        fill = (18, 25, 32) if cooling else (0, 45, 65)

        draw.ellipse(
            (cx-radius, cy-radius, cx+radius, cy+radius),
            fill=fill,
            outline=outline,
            width=2
        )

        shield_color = (45, 65, 75) if cooling else (0, 100, 140)
        shield_outline = (75, 95, 105) if cooling else self.CYAN

        draw.polygon(
            [
                (cx, cy - 12),
                (cx + 10, cy - 7),
                (cx + 9, cy + 5),
                (cx, cy + 13),
                (cx - 9, cy + 5),
                (cx - 10, cy - 7)
            ],
            fill=shield_color,
            outline=shield_outline
        )

        if cooling:
            text = str(math.ceil(self.skill_cooldown_remaining))
            font = self.skill_font

            bbox = draw.textbbox((0, 0), text, font=font)

            x = cx - (bbox[2] - bbox[0]) // 2
            y = cy - (bbox[3] - bbox[1]) // 2 - bbox[1]

            draw.text(
                (x, y),
                text,
                font=font,
                fill=(230, 230, 230)
            )
        else:
            draw.line(
                (cx, cy - 7, cx, cy + 7),
                fill=self.WHITE,
                width=2
            )
            draw.line(
                (cx - 6, cy, cx + 6, cy),
                fill=self.WHITE,
                width=2
            )

        self.draw = ImageDraw.Draw(self.image)


    def update_skill_icon(self, cooldown=0):
        """스킬 아이콘 영역 갱신"""

        self.skill_cooldown_remaining = cooldown

        box = (194, 172, 233, 211)

        # 아이콘 영역의 배경을 복원
        self.image.paste(
            self.background.crop(box),
            (box[0], box[1])
        )

        self.draw_skill_icon_overlay()
        self._show_region(box)

    def show_pause(self):
        """게임 화면 중앙에 일시정지 박스 표시"""

        box = (48, 95, 192, 145)

        # 일시정지 직전 화면 저장
        self.pause_background = self.image.crop(box).copy()

        draw = ImageDraw.Draw(self.image)

        # 중앙 박스
        draw.rectangle(
            (48, 95, 191, 144),
            fill=(0, 15, 30),
            outline=self.CYAN,
            width=2
        )

        # 중앙 정렬 텍스트 출력
        def centered_text(y, text, font, color):
            bbox = draw.textbbox((0, 0), text, font=font)

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = 120 - text_width // 2
            y = y - text_height // 2 - bbox[1]

            draw.text(
                (x, y),
                text,
                font=font,
                fill=color
            )

        # PAUSED 문구
        centered_text(
            110,
            "PAUSED",
            ImageFont.load_default(size=20),
            self.YELLOW
        )

        # 게임 재개 안내
        centered_text(
            132,
            "PRESS B TO RESUME",
            self.font,
            self.WHITE
        )

        self.draw = ImageDraw.Draw(self.image)
        self._show_region(box)


    def hide_pause(self):
        """일시정지 이전 화면 복구"""

        box = (48, 95, 192, 145)

        if not hasattr(self, "pause_background"):
            return

        self.image.paste(
            self.pause_background,
            (box[0], box[1])
        )

        self.draw = ImageDraw.Draw(self.image)
        self._show_region(box)

        del self.pause_background
    
    def draw_spaceship(self, x, y, shield_active=False):
        """우주선 및 보호막 출력"""

        if shield_active:
            # 우주선 주변 원형 보호막
            self.draw.ellipse(
                (x - 17, y - 19, x + 17, y + 19),
                fill=(0, 35, 30),
                outline=self.shield_color,
                width=2
            )

        ship_color = self.shield_color if shield_active else self.CYAN

        self.draw.polygon(
            [
                (x, y - 15),
                (x - 11, y + 12),
                (x, y + 7),
                (x + 11, y + 12)
            ],
            fill=ship_color
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

    def draw_boss(self, boss):
        """대형 소행성 보스 출력"""

        left, top, right, bottom = boss.get_hitbox()

        # 대형 소행성 본체
        self.draw.ellipse(
            (left, top, right, bottom),
            fill=(120, 115, 110),
            outline=(190, 180, 165),
            width=2
        )

        # 표면의 크레이터
        craters = [
            (58, 94, 10),
            (100, 88, 7),
            (145, 105, 11),
            (182, 94, 8),
            (86, 111, 5),
            (126, 88, 4)
        ]

        for x, y, radius in craters:
            self.draw.ellipse(
                (
                    x - radius,
                    y - radius // 2,
                    x + radius,
                    y + radius // 2
                ),
                fill=(70, 65, 62),
                outline=(150, 140, 130),
                width=1
            )

    def draw_boss_hp(self, boss):
        """보스 체력 및 HP 게이지 출력"""

        # 체력 표시 영역 초기화
        self.draw.rectangle(
            (28, 53, 212, 71),
            fill=self.BLACK
        )

        text = f"BOSS HP {boss.hp}/{boss.max_hp}"

        bbox = self.draw.textbbox(
            (0, 0),
            text,
            font=self.boss_font
        )

        text_width = bbox[2] - bbox[0]

        self.draw.text(
            (120 - text_width // 2, 53),
            text,
            font=self.boss_font,
            fill=self.RED
        )

        # 게이지 배경
        self.draw.rectangle(
            (30, 64, 210, 70),
            fill=(55, 20, 20),
            outline=(150, 65, 65)
        )

        # 현재 체력 비율
        hp_ratio = boss.hp / boss.max_hp
        bar_width = int(179 * hp_ratio)

        if bar_width > 0:
            self.draw.rectangle(
                (31, 65, 30 + bar_width, 69),
                fill=self.RED
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

    def draw_heart_item(self, x, y, radius):
        """체력 회복 아이템 출력"""

        x = int(x)
        y = int(y)

        # 바깥쪽 붉은 광채
        self.draw.ellipse(
            (
                x - radius - 2,
                y - radius - 2,
                x + radius + 2,
                y + radius + 2
            ),
            fill=(85, 15, 25),
            outline=(180, 45, 60),
            width=1
        )

        # 기존 HUD 하트 그리기 함수 재활용
        self.draw_heart(
            x - 7,
            y - 7,
            self.RED
        )

        # 하트의 밝은 반사광
        self.draw.ellipse(
            (x - 5, y - 5, x - 3, y - 3),
            fill=(255, 210, 210)
        )

    def draw_weapon_item(self, x, y, radius):
        """무기 강화 아이템 출력"""

        x = int(x)
        y = int(y)

        # 바깥쪽 보라색 광채
        self.draw.ellipse(
            (
                x - radius - 2,
                y - radius - 2,
                x + radius + 2,
                y + radius + 2
            ),
            fill=(50, 15, 80),
            outline=(130, 60, 190),
            width=1
        )

        # 아이템 본체
        self.draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),
            fill=(145, 60, 220),
            outline=(210, 170, 255)
        )

        # 노란색 번개 모양
        self.draw.polygon(
            [
                (x + 1, y - 6),
                (x - 4, y + 1),
                (x, y + 1),
                (x - 2, y + 6),
                (x + 5, y - 2),
                (x + 1, y - 2),
                (x + 3, y - 6)
            ],
            fill=self.YELLOW
        )

    def draw_item(self, item):
        """아이템 종류에 따라 화면 출력"""

        if item.item_type == "energy":
            self.draw_energy_orb(
                item.x,
                item.y,
                item.radius
            )

        elif item.item_type == "heart":
            self.draw_heart_item(
                item.x,
                item.y,
                item.radius
            )

        elif item.item_type == "weapon":
            self.draw_weapon_item(
                item.x,
                item.y,
                item.radius
            )

    def draw_bullet(self, bullet):
        """총알 출력"""

        x = int(bullet.x)
        y = int(bullet.y)

        left = max(0, x - bullet.width // 2)
        right = min(
            self.WIDTH - 1,
            x + (bullet.width - 1) // 2
        )

        top = max(50, y - bullet.height // 2)
        bottom = min(
            214,
            y + (bullet.height - 1) // 2
        )

        if left > right or top > bottom:
            return

        # 총알 본체
        self.draw.rectangle(
            (left, top, right, bottom),
            fill=bullet.color
        )

        # 총알 중앙의 밝은 빛
        if left <= x <= right:
            self.draw.line(
                (x, top, x, bottom),
                fill=self.WHITE,
                width=1
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

        # 시작 화면에도 사용 가능한 스킬 아이콘 표시
        self.update_skill_icon(0)

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
        player_x, player_y, show_player=True,
        items=None, shield_active=False, 
        bullets=None, boss=None
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

            # 대형 소행성 보스 출력
            if boss is not None:
                boss_region = boss.get_region()

                if (
                    left < boss_region[2]
                    and right > boss_region[0]
                    and top < boss_region[3]
                    and bottom > boss_region[1]
                ):
                    self.draw_boss(boss)

            for asteroid in asteroids:
                x = int(asteroid.x)
                y = int(asteroid.y)
                r = asteroid.radius

                if (
                    left < x + r + 1 and right > x - r
                    and top < y + r + 1 and bottom > y - r
                ):
                    self.draw_asteroid(x, y, r)

            # 총알 출력
            for bullet in (bullets or []):
                bullet_region = bullet.get_region()

                if (
                    left < bullet_region[2]
                    and right > bullet_region[0]
                    and top < bullet_region[3]
                    and bottom > bullet_region[1]
                ):
                    self.draw_bullet(bullet)

            # 아이템 출력
            for item in (items or []):
                x = int(item.x)
                y = int(item.y)
                r = item.radius + 2

                if (
                    left < x + r + 1
                    and right > x - r
                    and top < y + r + 1
                    and bottom > y - r
                ):
                    self.draw_item(item)

            # 스킬 아이콘을 먼저 그리기
            skill_box = (194, 172, 233, 211)

            if (
                left < skill_box[2]
                and right > skill_box[0]
                and top < skill_box[3]
                and bottom > skill_box[1]
            ):
                self.draw_skill_icon_overlay()

            # 우주선은 스킬 아이콘보다 위에 표시
            ship_radius_x = 18 if shield_active else 12
            ship_radius_y = 20 if shield_active else 16

            if (
                show_player
                and left < player_x + ship_radius_x
                and right > player_x - ship_radius_x
                and top < player_y + ship_radius_y
                and bottom > player_y - ship_radius_y
            ):
                self.draw_spaceship(
                    player_x,
                    player_y,
                    shield_active=shield_active
                )

            # 보스 체력 게이지를 최상위에 출력
            if boss is not None:
                hp_region = boss.get_hp_region()

                if (
                    left < hp_region[2]
                    and right > hp_region[0]
                    and top < hp_region[3]
                    and bottom > hp_region[1]
                ):
                    self.draw_boss_hp(boss)

            self._show_region((left, top, right, bottom))

    def show_game_over(
        self,
        score,
        level,
        high_score,
        achieved_at,
        new_record=False
    ):
        """게임 종료 및 최고 기록 화면 출력"""

        self.image = Image.new(
            "RGB",
            (self.WIDTH, self.HEIGHT),
            self.BLACK
        )

        self.draw = ImageDraw.Draw(self.image)

        title_font = ImageFont.load_default(size=25)
        info_font = ImageFont.load_default(size=16)
        record_font = ImageFont.load_default(size=26)
        label_font = ImageFont.load_default(size=13)
        date_font = ImageFont.load_default(size=12)

        def centered_text(y, text, font, color):
            bbox = self.draw.textbbox(
                (0, 0),
                text,
                font=font
            )

            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2

            self.draw.text(
                (x, y - bbox[1]),
                text,
                font=font,
                fill=color
            )

        # 게임 종료 제목
        centered_text(
            20, "GAME OVER",
            title_font, self.RED
        )

        # 현재 게임 결과
        centered_text(
            58, f"SCORE: {score:04d}",
            info_font, self.YELLOW
        )

        centered_text(
            81, f"LEVEL: {level}",
            info_font, self.CYAN
        )

        self.draw.line(
            (25, 108, 215, 108),
            fill=self.CYAN,
            width=1
        )

        # 최고 기록 제목
        if new_record:
            centered_text(
                118, "NEW HIGH SCORE!",
                label_font, self.YELLOW
            )
        else:
            centered_text(
                118, "HIGH SCORE",
                label_font, self.WHITE
            )

        # 최고 점수
        centered_text(
            139, f"{high_score:04d}",
            record_font, self.YELLOW
        )

        # 최고 기록 달성 시간
        record_date = (
            achieved_at
            if achieved_at
            else "NO RECORD YET"
        )

        centered_text(
            170, record_date,
            date_font, self.WHITE
        )

        self.draw.line(
            (25, 196, 215, 196),
            fill=self.CYAN,
            width=1
        )

        # 재시작 안내
        centered_text(
            210, "PRESS A TO RESTART",
            self.font, self.WHITE
        )

        self.disp.image(self.image)

    def shutdown(self):
        """LCD 백라이트 종료"""

        self.backlight.value = False
