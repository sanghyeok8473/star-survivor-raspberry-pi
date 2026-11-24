from bullet import Bullet

class Player:
    """우주선의 위치와 이동을 관리하는 클래스"""

    def __init__(self):
        # 우주선 초기 위치
        self.x = 120
        self.y = 170

        # 이동 속도
        self.speed = 8

        # 우주선이 이동할 수 있는 화면 범위
        self.min_x = 12
        self.max_x = 228
        self.min_y = 55
        self.max_y = 200

        # 무기 관련 설정
        self.weapon_level = 1
        self.max_weapon_level = 6

        # 총알 발사 주기
        self.fire_interval = 0.3
        self.fire_timer = 0.0

    def move(self, dx, dy):
        """입력 방향에 따라 우주선 이동"""

        # 대각선 이동 속도 보정
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x += dx * self.speed
        self.y += dy * self.speed

        # 화면 경계 제한
        self.x = max(self.min_x, min(self.x, self.max_x))
        self.y = max(self.min_y, min(self.y, self.max_y))

    def upgrade_weapon(self, amount=1):
        """무기 강화 및 최대 레벨 제한"""

        previous_level = self.weapon_level

        self.weapon_level = min(
            self.max_weapon_level,
            self.weapon_level + amount
        )

        return self.weapon_level > previous_level

    def fire(self, dt):
        """무기 레벨에 따라 총알 생성"""

        self.fire_timer += dt

        if self.fire_timer < self.fire_interval:
            return []

        self.fire_timer -= self.fire_interval

        # 무기 레벨별 발사 위치
        if self.weapon_level == 1:
            offsets = [0]

        elif self.weapon_level == 2:
            offsets = [-6, 6]

        else:
            offsets = [-10, 0, 10]

        # 무기 레벨별 총알 속성
        weapon_stats = {
            1: (1, 3, 9, (255, 220, 50)),
            2: (1, 3, 9, (255, 220, 50)),
            3: (1, 3, 9, (255, 220, 50)),
            4: (2, 5, 11, (0, 220, 255)),
            5: (3, 7, 13, (180, 100, 255)),
            6: (4, 9, 15, (255, 70, 180))
        }

        damage, width, height, color = (
            weapon_stats[self.weapon_level]
        )

        bullets = []

        for offset in offsets:
            bullets.append(
                Bullet(
                    x=self.x + offset,
                    y=self.y - 20,
                    damage=damage,
                    speed=180,
                    width=width,
                    height=height,
                    color=color
                )
            )

        return bullets