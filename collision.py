import math


def check_circle_collision(player, obj):
    """우주선과 원형 오브젝트의 충돌 판정"""

    player_half_width = 8
    player_half_height = 11

    dx = abs(obj.x - player.x)
    dy = abs(obj.y - player.y)

    closest_x = max(dx - player_half_width, 0)
    closest_y = max(dy - player_half_height, 0)

    distance_squared = (
        closest_x ** 2 + closest_y ** 2
    )

    return distance_squared <= obj.radius ** 2


def check_asteroid_collision(player, asteroid):
    """우주선과 소행성의 충돌 판정"""

    return check_circle_collision(player, asteroid)


def check_item_collision(player, item):
    """우주선과 아이템의 충돌 판정"""

    return check_circle_collision(player, item)

def check_bullet_boss_collision(bullet, boss):
    """총알과 타원형 보스의 충돌 판정"""

    # 총알의 사각형 영역
    bullet_left = bullet.x - bullet.width / 2
    bullet_right = bullet.x + bullet.width / 2

    bullet_top = bullet.y - bullet.height / 2
    bullet_bottom = bullet.y + bullet.height / 2

    # 보스 중심에서 가장 가까운 총알 영역의 좌표
    closest_x = max(
        bullet_left,
        min(boss.x, bullet_right)
    )

    closest_y = max(
        bullet_top,
        min(boss.y, bullet_bottom)
    )

    radius_x = boss.width / 2
    radius_y = boss.height / 2

    dx = (closest_x - boss.x) / radius_x
    dy = (closest_y - boss.y) / radius_y

    return dx ** 2 + dy ** 2 <= 1