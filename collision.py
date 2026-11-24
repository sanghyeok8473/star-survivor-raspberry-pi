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