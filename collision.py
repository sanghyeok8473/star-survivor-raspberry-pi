import math


def check_asteroid_collision(player, asteroid):
    """우주선과 소행성의 충돌 여부를 판정"""

    # 우주선의 충돌 영역 (실제 그림보다 약간 작게)
    player_half_width = 8
    player_half_height = 11

    # 우주선 중심과 소행성 중심 사이 거리
    dx = abs(asteroid.x - player.x)
    dy = abs(asteroid.y - player.y)

    # 사각형과 원의 충돌 판정
    closest_x = max(dx - player_half_width, 0)
    closest_y = max(dy - player_half_height, 0)

    distance_squared = closest_x ** 2 + closest_y ** 2

    return distance_squared <= asteroid.radius ** 2