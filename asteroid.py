import random


class Asteroid:
    """소행성의 위치와 이동을 관리하는 클래스"""

    def __init__(self, min_speed=35.0, max_speed=65.0):
        self.radius = random.randint(6, 10)

        # 이동 방향: 왼쪽 대각선, 수직, 오른쪽 대각선
        self.direction = random.choice([-1, 0, 1])

        # 방향에 따라 생성 위치 설정
        if self.direction == 1:
            # 왼쪽 상단에서 오른쪽 아래로
            self.x = random.randint(self.radius + 2, 90)

        elif self.direction == -1:
            # 오른쪽 상단에서 왼쪽 아래로
            self.x = random.randint(150, 238 - self.radius)

        else:
            # 상단 전체에서 무작위 생성
            self.x = random.randint(
                self.radius + 2,
                238 - self.radius
            )

        self.y = -self.radius

        # 아래쪽 이동 속도
        self.speed = random.uniform(min_speed, max_speed)

        # 수평 이동 속도
        if self.direction == 0:
            self.vx = 0.0
        else:
            self.vx = self.direction * self.speed * random.uniform(
                0.25, 0.55
            )

    def update(self, dt):
        """경과 시간에 따라 소행성을 이동"""

        self.x += self.vx * dt
        self.y += self.speed * dt

    def is_out_of_bounds(self):
        """소행성이 게임 영역 밖으로 벗어났는지 확인"""

        return (
            self.y - self.radius > 214
            or self.x + self.radius < 0
            or self.x - self.radius > 240
        )