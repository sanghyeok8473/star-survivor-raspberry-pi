
# STAR SURVIVOR 🚀

Raspberry Pi 4와 240×240 LCD를 활용한 우주 생존 아케이드 게임 프로젝트입니다.

## 1. 프로젝트 개요

- 게임 이름: STAR SURVIVOR (우주 생존 작전)
- 개발 환경: Python 3.13 / Linux
- 하드웨어: Raspberry Pi 4, LCD-Joystick Module
- 디스플레이: 240×240 ST7789 LCD
- 입력 장치: Joystick (GPIO)
- 개발 언어: Python

## 2. 게임 소개

플레이어는 우주선을 조종하여 소행성 지대에서 생존하는 아케이드 게임입니다.

우주선은 조이스틱으로 이동하며, 화면에는 별들이 아래쪽으로 흐르는 배경을 구현하여 우주를 비행하는 느낌을 제공합니다.

향후 소행성을 피하고 에너지 구슬을 수집하는 등 다양한 생존 요소를 추가할 예정입니다.

## 3. 주요 기능

### 구현 완료

- 조이스틱을 이용한 우주선 상하좌우 이동
- 대각선 이동 및 화면 경계 제한
- 별 배경 스크롤을 통한 전진 효과
- 우주선 우선 렌더링 처리
- LCD 부분 갱신을 통한 화면 출력 최적화
- 우주선 이동 속도 및 화면 갱신 개선

### 추가 구현 예정

- 소행성 생성 및 이동
- 소행성 충돌 판정
- 체력 감소 및 게임 오버
- 에너지 구슬 수집 및 점수 획득
- 보호막 시스템
- 난이도 증가 시스템
- 게임 일시정지 및 재시작

## 4. 프로젝트 구조

```text
star-survivor-raspberry-pi/
├── main.py          # 게임 실행 진입점
├── game.py          # 게임 진행 및 메인 루프
├── display.py       # LCD 초기화 및 화면 출력
├── controls.py      # 조이스틱 입력 처리
├── player.py        # 우주선 위치 및 이동 관리
├── asteroid.py      # 소행성 기능 (추가 구현 예정)
├── item.py          # 아이템 기능 (추가 구현 예정)
├── collision.py     # 충돌 판정 (추가 구현 예정)
├── assets/          # 게임 이미지 및 리소스
├── tests/           # 테스트 코드
├── requirements.txt # Python 패키지 목록
├── README.md
└── .gitignore
```

## 5. 실행 방법

### 1) 저장소 복제

```bash
git clone https://github.com/sanghyeok8473/star-survivor-raspberry-pi.git
cd star-survivor-raspberry-pi
```

### 2) 가상환경 생성 및 활성화

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) 패키지 설치

```bash
pip install -r requirements.txt
```

### 4) 게임 실행

```bash
python main.py
```

※ Raspberry Pi GPIO 및 SPI 설정이 완료된 환경에서 실행해야 합니다.

## 6. 개발 기록

개발 과정과 주요 변경 사항은 GitHub 저장소에 기록합니다.