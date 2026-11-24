import json
from pathlib import Path
from datetime import datetime


class HighScore:
    """최고 점수 및 달성 시간 관리"""

    def __init__(self):
        self.file_path = (
            Path(__file__).resolve().parent
            / "data"
            / "high_score.json"
        )

        self.score = 0
        self.level = 0
        self.achieved_at = None

        self.load()

    def load(self):
        """저장된 최고 기록 불러오기"""

        if not self.file_path.exists():
            return

        try:
            with self.file_path.open(
                "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            score = int(data["high_score"])
            level = int(data["level"])
            achieved_at = data["achieved_at"]

            if score < 0 or level < 0:
                raise ValueError("잘못된 기록")

            if achieved_at is not None:
                datetime.fromisoformat(achieved_at)

            self.score = score
            self.level = level
            self.achieved_at = achieved_at

        except (OSError, ValueError, TypeError, KeyError):
            print("최고 기록을 불러오지 못했습니다.")

    def save(self):
        """최고 기록을 JSON 파일에 저장"""

        data = {
            "high_score": self.score,
            "level": self.level,
            "achieved_at": self.achieved_at
        }

        try:
            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            temp_path = self.file_path.with_suffix(".tmp")

            with temp_path.open(
                "w", encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            temp_path.replace(self.file_path)

        except OSError as error:
            print(f"최고 기록 저장 실패: {error}")

    def update(self, score, level):
        """최고 기록 갱신 여부 확인 및 저장"""

        if score <= self.score:
            return False

        self.score = score
        self.level = level

        self.achieved_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.save()

        print(f"최고 기록 갱신! SCORE: {self.score}")

        return True