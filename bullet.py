class Bullet:
    """우주선에서 발사되는 총알"""

    def __init__(
        self,
        x,
        y,
        damage=1,
        speed=180,
        width=3,
        height=9,
        color=(255, 220, 50)
    ):
        self.x = float(x)
        self.y = float(y)

        self.damage = damage
        self.speed = speed

        self.width = width
        self.height = height
        self.color = color

    def update(self, dt):
        """총알을 위쪽으로 이동"""

        self.y -= self.speed * dt

    def is_out_of_bounds(self):
        """게임 영역 상단 이탈 여부"""

        return self.y + self.height // 2 < 50

    def get_region(self):
        """부분 렌더링을 위한 총알 영역 반환"""

        x = int(self.x)
        y = int(self.y)

        return (
            x - self.width // 2 - 1,
            y - self.height // 2 - 1,
            x + (self.width + 1) // 2 + 1,
            y + (self.height + 1) // 2 + 1
        )