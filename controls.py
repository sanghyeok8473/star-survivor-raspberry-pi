
import board
import digitalio


class Controls:
    """조이스틱 입력을 관리하는 클래스"""

    def __init__(self):
        self.buttons = {
            "up": board.D17,
            "down": board.D22,
            "left": board.D27,
            "right": board.D23,
            "start": board.D5
        }

        self.inputs = {}

        for name, pin in self.buttons.items():
            button = digitalio.DigitalInOut(pin)
            button.direction = digitalio.Direction.INPUT
            self.inputs[name] = button

    def get_direction(self):
        """조이스틱 입력 방향 반환"""

        dx = 0
        dy = 0

        if not self.inputs["left"].value:
            dx -= 1

        if not self.inputs["right"].value:
            dx += 1

        if not self.inputs["up"].value:
            dy -= 1

        if not self.inputs["down"].value:
            dy += 1

        return dx, dy

    def is_start_pressed(self):
        """A 버튼 입력 여부 반환"""
        return not self.inputs["start"].value

    def cleanup(self):
        """GPIO 입력 자원 정리"""

        for button in self.inputs.values():
            button.deinit()