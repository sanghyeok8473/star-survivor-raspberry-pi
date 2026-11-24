
import time
import random
import math

from display import Display
from controls import Controls
from player import Player
from asteroid import Asteroid
from collision import (
    check_asteroid_collision,
    check_item_collision
)
from item import EnergyOrb, HeartItem
from high_score import HighScore

class Game:
    """STAR SURVIVOR 게임 진행 관리"""

    def __init__(self):
        self.display = Display()
        self.controls = Controls()
        self.player = Player()

        # 최고 기록 관리
        self.high_score = HighScore()

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
        
        # 아이템 통합 관리
        self.items = []

        # 에너지 구슬 생성 타이머
        self.orb_spawn_timer = 0.0

        # 체력 회복 아이템 등장 기록
        self.heart_spawned_levels = set()
        
        self.level_up_timer = 0.0
        self.level_up_visible = False
        self.paused = False
        self.pause_button_was_pressed = False

        # A 버튼 무적 스킬
        self.skill_duration = 5.0
        self.skill_cooldown = 30.0

        self.skill_timer = 0.0
        self.skill_cooldown_timer = 0.0
        self.skill_button_was_pressed = False
        self.skill_cooldown_display = 0

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
        self.items = []
        self.orb_spawn_timer = 0.0
        self.heart_spawned_levels = set()

        self.level_up_timer = 0.0
        self.level_up_visible = False

        self.paused = False
        self.pause_button_was_pressed = False

        self.skill_timer = 0.0
        self.skill_cooldown_timer = 0.0
        self.skill_cooldown_display = 0

        # 재시작에 사용한 A 버튼이 곧바로 스킬을 발동하지 않도록 처리
        self.skill_button_was_pressed = True

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
            show_start_message=False,
            level=self.level
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
            self.lives,
            level=self.level
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
                        self.skill_button_was_pressed = True
                        previous_time = current_time

                        self.display.clear_start_message()

                        print("게임 시작!")

                    time.sleep(0.05)
                    continue

                # B 버튼 일시정지 처리
                pause_pressed = self.controls.is_pause_pressed()

                # 새로 눌렀을 때만 상태 전환
                if pause_pressed and not self.pause_button_was_pressed:
                    self.paused = not self.paused

                    if self.paused:
                        self.display.show_pause()
                        print("게임 일시정지")
                    else:
                        self.display.hide_pause()

                        # 게임 재개 시 시간 기준 초기화
                        previous_time = time.monotonic()

                        # 일시정지 중 A 버튼 입력이 스킬을 발동하지 않도록 처리
                        self.skill_button_was_pressed = (
                            self.controls.is_start_pressed()
                        )

                        self.pause_button_was_pressed = pause_pressed

                        print("게임 재개")

                        # 다음 프레임부터 게임 로직 실행
                        continue

                self.pause_button_was_pressed = pause_pressed

                # 일시정지 중에는 게임 로직 실행하지 않음
                if self.paused:
                    time.sleep(0.02)
                    continue

                # 프레임 경과 시간이 음수가 되지 않도록 제한
                dt = max(0.0, min(current_time - previous_time, 0.05))
                previous_time = current_time

                regions = []

                # 스킬 발동 전 상태 저장
                previous_skill_active = self.skill_timer > 0

                # A 버튼 스킬 입력
                skill_pressed = self.controls.is_start_pressed()

                if (
                    skill_pressed
                    and not self.skill_button_was_pressed
                    and self.skill_cooldown_timer <= 0
                ):
                    self.skill_timer = self.skill_duration
                    self.skill_cooldown_timer = self.skill_cooldown

                    print("보호막 스킬 발동!")

                self.skill_button_was_pressed = skill_pressed

                # 스킬 지속 시간 및 쿨타임 감소
                self.skill_timer = max(0.0, self.skill_timer - dt)

                self.skill_cooldown_timer = max(
                    0.0, self.skill_cooldown_timer - dt
                )

                # 현재 스킬 활성화 상태
                skill_active = self.skill_timer > 0

                # 보호막 시작 또는 종료 시 화면 갱신
                if previous_skill_active != skill_active:
                    px, py = int(self.player.x), int(self.player.y)

                    regions.append((
                        px - 19, py - 21,
                        px + 20, py + 22
                    ))

                    if not skill_active:
                        print("보호막 스킬 종료")

                # 쿨타임 숫자가 달라질 때만 갱신
                remaining = math.ceil(self.skill_cooldown_timer)

                if remaining != self.skill_cooldown_display:
                    self.skill_cooldown_display = remaining

                    # 스킬 아이콘 상태만 변경
                    self.display.skill_cooldown_remaining = (
                        self.skill_cooldown_timer
                    )

                    # 기존 부분 렌더링 과정에서 아이콘을 함께 갱신
                    regions.append((194, 172, 233, 211))

                # 생존 시간 및 레벨 갱신
                self.survival_time += dt
                new_level = min(5, int(self.survival_time // 20) + 1)

                if new_level != self.level:
                    self.level = new_level

                    self.level_up_timer = 1.2
                    self.level_up_visible = True

                    # 레벨업 순간 글씨 확대
                    self.display.update_level(
                        self.level,
                        visible=True,
                        enlarged=True
                    )

                    print(f"LEVEL UP! LEVEL {self.level}")

                    # 3레벨마다 체력 회복 아이템 1회 생성
                    if (
                        self.level % 3 == 0
                        and self.level not in self.heart_spawned_levels
                    ):
                        heart = HeartItem()

                        self.items.append(heart)
                        self.heart_spawned_levels.add(self.level)

                        # 생성된 아이템의 화면 영역 갱신
                        regions.append(heart.get_region())

                        print(
                            f"체력 회복 아이템 등장! "
                            f"LEVEL {self.level}"
                        )

                # 레벨업 애니메이션
                previous_level_up_visible = self.level_up_visible

                if self.level_up_timer > 0:
                    self.level_up_timer = max(
                        0.0,
                        self.level_up_timer - dt
                    )

                    if self.level_up_timer > 0:
                        # 확대된 글씨가 0.2초 간격으로 깜빡임
                        self.level_up_visible = (
                            int(self.level_up_timer / 0.2) % 2 == 0
                        )

                        if self.level_up_visible != previous_level_up_visible:
                            self.display.update_level(
                                self.level,
                                visible=self.level_up_visible,
                                enlarged=True
                            )
                    else:
                        # 애니메이션 종료: 원래 크기와 색상으로 복구
                        self.level_up_visible = True

                        self.display.update_level(
                            self.level,
                            visible=True,
                            enlarged=False
                        )
                else:
                    self.level_up_visible = True

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

                energy_count = sum(
                    1 for item in self.items
                    if item.item_type == "energy"
                )

                if (
                    self.orb_spawn_timer >= 4.0
                    and energy_count < 2
                ):
                    orb = EnergyOrb()

                    self.items.append(orb)
                    self.orb_spawn_timer = 0.0

                    regions.append(orb.get_region())

                # 전체 아이템 이동 및 제거 처리
                remaining_items = []

                for item in self.items:
                    old_x = int(item.x)
                    old_y = int(item.y)

                    old_region = item.get_region()

                    item.update(dt)

                    new_x = int(item.x)
                    new_y = int(item.y)

                    new_region = item.get_region()

                    # 유지 시간 초과 또는 화면 이탈
                    if item.should_remove():
                        regions.append(old_region)
                        regions.append(new_region)
                        continue

                    # 위치가 변경된 경우에만 화면 갱신
                    if old_x != new_x or old_y != new_y:
                        regions.append(old_region)
                        regions.append(new_region)

                    remaining_items.append(item)

                self.items = remaining_items

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
                        old_x - 19, old_y - 21,
                        old_x + 20, old_y + 22
                    ))

                    regions.append((
                        new_x - 19, new_y - 21,
                        new_x + 20, new_y + 22
                    ))

                # 충돌 후 무적 시간 감소
                self.invincible_timer = max(
                    0.0, self.invincible_timer - dt
                )

                # 무적 시간 동안 우주선 깜빡임
                if self.invincible_timer > 0 and not skill_active:
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
                if self.invincible_timer <= 0 and not skill_active:
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

                                # 최고 기록 갱신 여부 확인
                                new_record = self.high_score.update(
                                    self.score,
                                    self.level
                                )

                                # 게임 종료 화면 출력
                                self.display.show_game_over(
                                    self.score,
                                    self.level,
                                    self.high_score.score,
                                    self.high_score.achieved_at,
                                    new_record
                                )

                            break

                # GAME OVER 상태면 다음 프레임으로 이동
                if self.game_over:
                    continue

                # 아이템 획득 판정
                remaining_items = []

                for item in self.items:
                    if check_item_collision(self.player, item):

                        # 에너지 구슬 획득
                        if item.item_type == "energy":
                            self.score += item.score_value

                            print(
                                f"에너지 구슬 획득! "
                                f"현재 점수: {self.score}"
                            )

                            self.display.update_score(self.score)

                        # 체력 회복 아이템 획득
                        elif item.item_type == "heart":
                            previous_lives = self.lives

                            self.lives = min(
                                3,
                                self.lives + item.heal_amount
                            )

                            if self.lives != previous_lives:
                                self.display.update_lives(self.lives)

                                print(
                                    f"체력 회복! "
                                    f"현재 목숨: {self.lives}"
                                )

                            else:
                                print("체력이 이미 최대입니다.")

                        # 획득한 아이템 영역 복원
                        regions.append(item.get_region())

                    else:
                        remaining_items.append(item)

                self.items = remaining_items
                
                # 변경 영역만 LCD에 출력
                self.display.update_game_objects(
                    regions,
                    self.stars,
                    self.asteroids,
                    new_x,
                    new_y,
                    show_player=self.player_visible,
                    items=self.items,
                    shield_active=skill_active
                )

                time.sleep(0.01)
            

        except KeyboardInterrupt:
            print("게임 종료 요청")

        finally:
            self.running = False
            self.controls.cleanup()
            self.display.shutdown()
