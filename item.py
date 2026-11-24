import random


class Item:
    """게임 아이템의 공통 기능"""

    def __init__(
        self,
        radius,
        min_speed,
        max_speed,
        lifetime=None,
        start_y=None
    ):
        self.radius = radius

        self.x = random.randint(15, 225)
        self.y = -radius if start_y is None else start_y

        # 아래쪽 이동 속도
        self.speed = random.uniform(min_speed, max_speed)

        # 좌우 이동 속도
        self.vx = random.uniform(-8, 8)

        # 아이템 유지 시간
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt):
        """아이템 위치 및 생존 시간 갱신"""

        self.x += self.vx * dt
        self.y += self.speed * dt

        self.age += dt

        # 화면 좌우 경계에서 반사
        if self.x < self.radius:
            self.x = self.radius
            self.vx = abs(self.vx)

        elif self.x > 240 - self.radius:
            self.x = 240 - self.radius
            self.vx = -abs(self.vx)

    def is_out_of_bounds(self):
        """게임 영역 아래쪽 이탈 여부"""

        return self.y - self.radius > 215

    def is_expired(self):
        """아이템 유지 시간 초과 여부"""

        return (
            self.lifetime is not None
            and self.age >= self.lifetime
        )

    def should_remove(self):
        """아이템 제거 여부"""

        return (
            self.is_out_of_bounds()
            or self.is_expired()
        )

    def get_region(self):
        """부분 렌더링을 위한 아이템 영역 반환"""

        x = int(self.x)
        y = int(self.y)
        r = self.radius + 2

        return (
            x - r - 2,
            y - r - 2,
            x + r + 3,
            y + r + 3
        )


class EnergyOrb(Item):
    """점수 획득용 에너지 구슬"""

    def __init__(self):
        super().__init__(
            radius=5,
            min_speed=25,
            max_speed=40
        )

        self.item_type = "energy"
        self.score_value = 100


class HeartItem(Item):
    """체력 회복 아이템"""

    def __init__(self):
        super().__init__(
            radius=7,
            min_speed=25,
            max_speed=30,
            lifetime=5.0,
            start_y=59
        )

        self.item_type = "heart"
        self.heal_amount = 1