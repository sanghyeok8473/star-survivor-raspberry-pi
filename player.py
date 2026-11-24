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

    def fire(self, dt):
        """발사 주기에 따라 총알 생성"""

        self.fire_timer += dt

        if self.fire_timer < self.fire_interval:
            return []

        self.fire_timer -= self.fire_interval

        # 기본 무기: 우주선 중앙에서 총알 1개 발사
        return [
            Bullet(
                x=self.x,
                y=self.y - 20,
                damage=1
            )
        ]