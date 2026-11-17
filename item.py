import random


class EnergyOrb:
    """점수 획득용 에너지 구슬"""

    def __init__(self):
        self.radius = 5

        self.x = random.randint(15, 225)
        self.y = -self.radius

        # 소행성보다 느리게 이동
        self.speed = random.uniform(25, 40)

        # 좌우로 약간 움직임
        self.vx = random.uniform(-8, 8)

    def update(self, dt):
        """에너지 구슬 위치 갱신"""

        self.x += self.vx * dt
        self.y += self.speed * dt

        # 화면 좌우 경계에서 반사
        if self.x < self.radius:
            self.x = self.radius
            self.vx = abs(self.vx)

        elif self.x > 240 - self.radius:
            self.x = 240 - self.radius
            self.vx = -abs(self.vx)

    def is_out_of_bounds(self):
        """화면 아래쪽을 벗어났는지 확인"""

        return self.y - self.radius > 215