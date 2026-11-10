
import time
import random

from display import Display
from controls import Controls
from player import Player


class Game:
    """STAR SURVIVOR 게임 진행 관리"""

    def __init__(self):
        self.display = Display()
        self.controls = Controls()
        self.player = Player()

        self.score = 0
        self.hp = 100
        self.running = False

        # 배경 별 생성
        self.stars = []

        for _ in range(12):
            self.stars.append({
                "x": random.randint(5, 230),
                "y": random.randint(50, 210),
                "speed": random.uniform(1.0, 3.0),
                "size": random.choice([1, 2])
            })

    def run(self):
        """게임 메인 루프"""

        self.running = True

        print("STAR SURVIVOR 시작!")

        old_x = int(self.player.x)
        old_y = int(self.player.y)

        self.display.initialize_game_screen(
            old_x,
            old_y,
            self.stars,
            self.score,
            self.hp
        )

        previous_time = time.monotonic()

        try:
            while self.running:
                current_time = time.monotonic()

                dt = min(current_time - previous_time, 0.05)
                previous_time = current_time

                # 1. 배경 별 이동
                for star in self.stars:
                    old_star_y = int(star["y"])

                    star["y"] += star["speed"] * dt * 30

                    if star["y"] > 214:
                        star["y"] = 50
                        star["x"] = random.randint(5, 230)

                    new_star_y = int(star["y"])

                    if old_star_y != new_star_y:
                        self.display.update_star(
                            star["x"],
                            old_star_y,
                            star["x"],
                            new_star_y,
                            star["size"],
                            int(self.player.x),
                            int(self.player.y)
                        )

                # 2. 조이스틱 입력
                dx, dy = self.controls.get_direction()

                old_x = int(self.player.x)
                old_y = int(self.player.y)

                if dx != 0 or dy != 0:
                    self.player.move(dx, dy)

                new_x = int(self.player.x)
                new_y = int(self.player.y)

                # 3. 우주선 위치 갱신
                if old_x != new_x or old_y != new_y:
                    self.display.update_spaceship(
                        old_x,
                        old_y,
                        new_x,
                        new_y
                    )

                time.sleep(0.01)

        except KeyboardInterrupt:
            print("게임 종료 요청")

        finally:
            self.running = False
            self.controls.cleanup()
            self.display.shutdown()
