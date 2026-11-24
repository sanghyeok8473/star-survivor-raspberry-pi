class Boss:
    """대형 소행성 보스"""

    def __init__(self, level):
        self.level = level
        self.boss_number = level // 5

        # 보스 위치 및 크기
        self.x = 120
        self.y = 98
        self.width = 180
        self.height = 50

        # 등장 횟수에 따라 체력 증가
        self.max_hp = 100 + (self.boss_number - 1) * 50
        self.hp = self.max_hp

        # 보스 처치 보상
        self.score_value = 500

    def take_damage(self, damage):
        """총알에 의한 피해 처리"""

        self.hp = max(0, self.hp - damage)

    def is_defeated(self):
        """보스 처치 여부"""

        return self.hp <= 0

    def get_hitbox(self):
        """보스 본체의 충돌 판정 영역"""

        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2
        )

    def get_region(self):
        """체력 게이지를 포함한 전체 렌더링 영역"""

        return (28, 53, 213, 126)

    def get_hp_region(self):
        """체력 게이지 갱신 영역"""

        return (28, 53, 213, 72)