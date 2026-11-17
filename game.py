
import time
import random

from display import Display
from controls import Controls
from player import Player
from asteroid import Asteroid
from collision import check_asteroid_collision, check_orb_collision
from item import EnergyOrb

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
        self.invincible_timer = 0.0
        self.player_visible = True
        self.game_over = False
        self.restart_button_released = False
        self.orbs = []
        self.orb_spawn_timer = 0.0

        # 배경 별 생성
        self.stars = []

        for _ in range(12):
            self.stars.append({
                "x": random.randint(5, 230),
                "y": random.randint(50, 210),
                "speed": random.uniform(1.0, 3.0),
                "size": random.choice([1, 2])
            })

    def reset_game(self):
        """게임 재시작을 위한 상태 초기화"""

        self.player = Player()

        self.score = 0
        self.lives = 3
        self.level = 1
        self.survival_time = 0.0

        self.asteroids = []
        self.asteroid_spawn_timer = 0.0
        self.invincible_timer = 0.0

        self.game_over = False
        self.restart_button_released = False
        self.started = True
        self.player_visible = True
        self.orbs = []
        self.orb_spawn_timer = 0.0

        # 배경 별 위치 초기화
        for star in self.stars:
            star["x"] = random.randint(5, 230)
            star["y"] = random.randint(50, 210)

        # 새로운 게임 화면 출력
        self.display.initialize_game_screen(
            int(self.player.x),
            int(self.player.y),
            self.stars,
            self.score,
            self.lives,
            show_start_message=False
        )

        print("게임 재시작!")

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

                # GAME OVER 상태에서는 게임 진행 중지
                if self.game_over:
                    pressed = self.controls.is_start_pressed()

                    # 버튼을 한 번 놓은 뒤 다시 눌러야 재시작
                    if not pressed:
                        self.restart_button_released = True

                    elif self.restart_button_released:
                        self.reset_game()
                        previous_time = time.monotonic()

                    time.sleep(0.05)
                    continue

                # A 버튼을 누르기 전까지 대기
                if not self.started:
                    if self.controls.is_start_pressed():
                        self.started = True
                        previous_time = current_time

                        self.display.clear_start_message()

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

                # 에너지 구슬 생성
                self.orb_spawn_timer += dt

                if self.orb_spawn_timer >= 4.0 and len(self.orbs) < 2:
                    self.orbs.append(EnergyOrb())
                    self.orb_spawn_timer = 0.0

                # 에너지 구슬 이동
                remaining_orbs = []

                for orb in self.orbs:
                    old_x = int(orb.x)
                    old_y = int(orb.y)
                    r = orb.radius + 2

                    orb.update(dt)

                    new_orb_x = int(orb.x)
                    new_orb_y = int(orb.y)

                    if old_x != new_orb_x or old_y != new_orb_y:
                        regions.append((
                            old_x - r - 2,
                            old_y - r - 2,
                            old_x + r + 3,
                            old_y + r + 3
                        ))

                        regions.append((
                            new_orb_x - r - 2,
                            new_orb_y - r - 2,
                            new_orb_x + r + 3,
                            new_orb_y + r + 3
                        ))

                    if not orb.is_out_of_bounds():
                        remaining_orbs.append(orb)

                self.orbs = remaining_orbs

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

                # 충돌 후 무적 시간 감소
                self.invincible_timer = max(
                    0.0, self.invincible_timer - dt
                )

                # 무적 시간 동안 우주선 깜빡임
                if self.invincible_timer > 0:
                    # 약 0.12초 간격으로 표시/숨김 전환
                    player_visible = int(self.invincible_timer / 0.12) % 2 == 0
                else:
                    player_visible = True

                # 표시 상태가 바뀌면 우주선 영역 갱신
                if player_visible != self.player_visible:
                    regions.append((
                        new_x - 12,
                        new_y - 16,
                        new_x + 13,
                        new_y + 14
                    ))

                self.player_visible = player_visible

                # 소행성과 우주선 충돌 판정
                if self.invincible_timer <= 0:
                    for asteroid in self.asteroids:
                        if check_asteroid_collision(self.player, asteroid):

                            # 목숨이 0 미만으로 내려가지 않도록 제한
                            self.lives = max(0, self.lives - 1)

                            # 충돌 후 1초 무적
                            self.invincible_timer = 1.0

                            self.player_visible = False

                            regions.append((
                                new_x - 12,
                                new_y - 16,
                                new_x + 13,
                                new_y + 14
                            ))

                            print(f"소행성 충돌! 남은 목숨: {self.lives}")

                            # LCD 하트 갱신
                            self.display.update_lives(self.lives)

                            # 목숨이 모두 소진되면 GAME OVER
                            if self.lives == 0:
                                self.game_over = True
                                self.restart_button_released = False

                                print(
                                    f"GAME OVER! "
                                    f"최종 점수: {self.score}, "
                                    f"도달 레벨: {self.level}"
                                )

                                self.display.show_game_over(
                                    self.score,
                                    self.level
                                )

                            break

                # GAME OVER 상태면 다음 프레임으로 이동
                if self.game_over:
                    continue

                # 에너지 구슬 획득 판정
                remaining_orbs = []

                for orb in self.orbs:
                    if check_orb_collision(self.player, orb):
                        self.score += 100

                        print(f"에너지 구슬 획득! 현재 점수: {self.score}")

                        self.display.update_score(self.score)

                        # 획득한 구슬 영역을 다시 그리도록 기록
                        r = orb.radius + 2

                        regions.append((
                            int(orb.x) - r - 2,
                            int(orb.y) - r - 2,
                            int(orb.x) + r + 3,
                            int(orb.y) + r + 3
                        ))

                    else:
                        remaining_orbs.append(orb)

                self.orbs = remaining_orbs

                # 변경 영역만 LCD에 출력
                self.display.update_game_objects(
                    regions,
                    self.stars,
                    self.asteroids,
                    new_x,
                    new_y,
                    show_player=self.player_visible,
                    orbs=self.orbs
                )

                time.sleep(0.01)

        except KeyboardInterrupt:
            print("게임 종료 요청")

        finally:
            self.running = False
            self.controls.cleanup()
            self.display.shutdown()
