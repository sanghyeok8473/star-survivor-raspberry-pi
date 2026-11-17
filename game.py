
import time
import random

from display import Display
from controls import Controls
from player import Player
from asteroid import Asteroid


class Game:
    """STAR SURVIVOR 게임 진행 관리"""

    def __init__(self):
        self.display = Display()
        self.controls = Controls()
        self.player = Player()

        self.score = 0
        self.lives = 3
        self.running = False
        self.started = False
        self.level = 1
        self.survival_time = 0.0
        self.asteroids = []
        self.asteroid_spawn_timer = 0.0

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
        self.running = True
        self.started = False

        print("STAR SURVIVOR 시작!")

        self.display.initialize_game_screen(
            int(self.player.x),
            int(self.player.y),
            self.stars,
            self.score,
            self.lives
        )

        previous_time = time.monotonic()

        try:
            while self.running:
                current_time = time.monotonic()

                # A 버튼을 누르기 전까지 대기
                if not self.started:
                    if self.controls.is_start_pressed():
                        self.started = True
                        previous_time = current_time
                        print("게임 시작!")

                    time.sleep(0.05)
                    continue

                dt = min(current_time - previous_time, 0.05)
                previous_time = current_time

                regions = []

                # 생존 시간 및 레벨 갱신
                self.survival_time += dt
                new_level = min(5, int(self.survival_time // 20) + 1)

                if new_level != self.level:
                    self.level = new_level
                    print(f"LEVEL {self.level}")

                max_asteroids = self.level + 1
                spawn_interval = max(
                    0.8, 2.0 - (self.level - 1) * 0.3
                )

                min_speed = 35 + (self.level - 1) * 10
                max_speed = 65 + (self.level - 1) * 10

                # 소행성 생성
                self.asteroid_spawn_timer += dt

                if (
                    self.asteroid_spawn_timer >= spawn_interval
                    and len(self.asteroids) < max_asteroids
                ):
                    asteroid = Asteroid(min_speed, max_speed)
                    self.asteroids.append(asteroid)
                    self.asteroid_spawn_timer = 0.0

                # 소행성 이동 및 이전/현재 위치 기록
                remaining_asteroids = []

                for asteroid in self.asteroids:
                    old_x = int(asteroid.x)
                    old_y = int(asteroid.y)
                    r = asteroid.radius

                    asteroid.update(dt)

                    new_x = int(asteroid.x)
                    new_y = int(asteroid.y)

                    if old_x != new_x or old_y != new_y:
                        regions.append((
                            old_x - r - 2,
                            old_y - r - 2,
                            old_x + r + 3,
                            old_y + r + 3
                        ))

                        regions.append((
                            new_x - r - 2,
                            new_y - r - 2,
                            new_x + r + 3,
                            new_y + r + 3
                        ))

                    if not asteroid.is_out_of_bounds():
                        remaining_asteroids.append(asteroid)

                self.asteroids = remaining_asteroids

                # 배경 별 이동
                for star in self.stars:
                    old_x = int(star["x"])
                    old_y = int(star["y"])
                    size = star["size"]

                    star["y"] += star["speed"] * dt * 30

                    if star["y"] > 214:
                        star["y"] = 50
                        star["x"] = random.randint(5, 230)

                    new_x = int(star["x"])
                    new_y = int(star["y"])

                    if old_x != new_x or old_y != new_y:
                        regions.append((
                            old_x - 1, old_y - 1,
                            old_x + size + 1, old_y + size + 1
                        ))

                        regions.append((
                            new_x - 1, new_y - 1,
                            new_x + size + 1, new_y + size + 1
                        ))

                # 우주선 이동
                dx, dy = self.controls.get_direction()

                old_x = int(self.player.x)
                old_y = int(self.player.y)

                if dx != 0 or dy != 0:
                    self.player.move(dx, dy)

                new_x = int(self.player.x)
                new_y = int(self.player.y)

                if old_x != new_x or old_y != new_y:
                    regions.append((
                        old_x - 12, old_y - 16,
                        old_x + 13, old_y + 14
                    ))

                    regions.append((
                        new_x - 12, new_y - 16,
                        new_x + 13, new_y + 14
                    ))

                # 변경 영역만 LCD에 출력
                self.display.update_game_objects(
                    regions,
                    self.stars,
                    self.asteroids,
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
