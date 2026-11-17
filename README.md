# STAR SURVIVOR 🚀

Raspberry Pi 4와 240×240 LCD 및 조이스틱을 활용하여 제작한 우주 생존 아케이드 게임 프로젝트입니다.

## 1. 프로젝트 개요

- **게임 이름:** STAR SURVIVOR (우주 생존 작전)
- **개발 환경:** Python 3.13 / Raspberry Pi OS (Linux)
- **하드웨어:** Raspberry Pi 4, LCD-Joystick Module
- **디스플레이:** 240×240 ST7789 LCD (SPI)
- **입력 장치:** GPIO 기반 조이스틱 및 A 버튼
- **개발 언어:** Python
- **주요 라이브러리:** Adafruit Blinka, Adafruit CircuitPython RGB Display, Pillow

## 2. 게임 소개

STAR SURVIVOR는 우주선을 조종하여 소행성을 피하고 에너지 구슬을 수집하면서 생존하는 아케이드 게임입니다.

플레이어는 조이스틱을 이용해 우주선을 상하좌우 및 대각선으로 이동시킬 수 있습니다. 화면에는 별들이 아래쪽으로 흐르는 스크롤 배경을 구현하여 우주 공간을 비행하는 느낌을 제공합니다.

게임이 진행될수록 소행성의 생성 개수와 이동 속도가 증가하며, 플레이어는 소행성을 피하면서 에너지 구슬을 수집하여 높은 점수를 획득하는 것을 목표로 합니다.

## 3. 게임 규칙 및 조작 방법

### 게임 규칙

- 게임 시작 시 하트 3개가 주어집니다.
- 소행성과 충돌하면 하트가 1개 감소합니다.
- 충돌 후 1초 동안 무적 상태가 적용되며, 우주선이 깜빡이는 효과로 표시됩니다.
- 에너지 구슬을 수집하면 100점을 획득합니다.
- 생존 시간 20초마다 레벨이 상승하며, 최대 레벨은 5입니다.
- 레벨이 상승하면 소행성의 최대 생성 개수와 이동 속도가 증가합니다.
- 하트가 모두 소진되면 GAME OVER 화면으로 전환되며 최종 점수와 도달 레벨이 표시됩니다.
- GAME OVER 화면에서 A 버튼을 누르면 게임을 다시 시작할 수 있습니다.

### 조작 방법

| 입력 | 기능 |
|---|---|
| 조이스틱 상하좌우 | 우주선 이동 |
| 조이스틱 대각선 | 대각선 이동 |
| A 버튼 (시작 화면) | 게임 시작 |
| A 버튼 (GAME OVER) | 게임 재시작 |

## 4. 주요 구현 기능

### 게임 진행 및 상태 관리

- 시작 화면 및 A 버튼을 통한 게임 시작
- 게임 진행 상태 및 생존 시간 관리
- 충돌에 따른 하트 감소 및 GAME OVER 처리
- 게임 재시작 시 점수, 목숨, 레벨, 소행성 및 아이템 초기화

### 우주선 및 충돌 시스템

- 조이스틱을 이용한 상하좌우·대각선 이동
- 화면 경계를 벗어나지 않도록 이동 범위 제한
- 우주선과 소행성 간 충돌 판정
- 충돌 후 1초 무적 시간 및 우주선 깜빡임 효과

### 소행성 및 난이도 시스템

- 소행성의 무작위 생성 및 이동
- 수직·대각선 방향 이동
- 화면 밖으로 벗어난 소행성 제거
- 생존 시간에 따른 단계별 난이도 상승
- 최대 레벨 5까지 소행성 개수 및 이동 속도 증가

### 에너지 구슬 및 점수 시스템

- 에너지 구슬의 무작위 생성 및 이동
- 우주선과 에너지 구슬 간 획득 판정
- 구슬 획득 시 100점 추가
- 점수 표시 영역 실시간 갱신
- GAME OVER 화면에서 최종 점수 표시

### LCD 화면 출력 최적화

- ST7789 LCD를 이용한 240×240 화면 출력
- 별 배경 스크롤 효과
- 우주선, 소행성, 에너지 구슬의 레이어 순서 관리
- 변경된 화면 영역만 갱신하는 부분 렌더링
- 겹치는 갱신 영역 병합을 통한 불필요한 LCD 전송 최소화
- 하트 및 점수 표시 영역의 개별 갱신

## 5. 프로젝트 구조

```text
star-survivor-raspberry-pi/
├── main.py           # 프로그램 실행 진입점
├── game.py           # 게임 루프, 상태 및 난이도 관리
├── display.py        # LCD 출력 및 화면 갱신 최적화
├── controls.py       # 조이스틱 및 버튼 입력 처리
├── player.py         # 우주선 위치 및 이동 관리
├── asteroid.py       # 소행성 생성 및 이동
├── item.py           # 에너지 구슬 생성 및 이동
├── collision.py      # 소행성 충돌 및 아이템 획득 판정
├── requirements.txt  # Python 패키지 목록
├── README.md         # 프로젝트 설명 문서
└── .gitignore        # Git 추적 제외 설정
```

## 6. 설치 및 실행 방법

### 1) 실행 환경 준비

Raspberry Pi 4에 Raspberry Pi OS를 설치하고, LCD-Joystick Module을 연결합니다.

게임 실행을 위해 Raspberry Pi의 SPI 인터페이스가 활성화되어 있어야 합니다.

```bash
sudo raspi-config
```

`Interface Options → SPI → Enable`을 선택합니다.

SPI 장치 확인:

```bash
ls /dev/spidev*
```

### 2) 저장소 복제

```bash
git clone https://github.com/sanghyeok8473/star-survivor-raspberry-pi.git
cd star-survivor-raspberry-pi
```

### 3) Python 가상환경 생성 및 활성화

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

### 4) 패키지 설치

```bash
python -m pip install -r requirements.txt
```

### 5) 게임 실행

```bash
python main.py
```

게임을 종료하려면 터미널에서 `Ctrl + C`를 누릅니다.

※ 본 프로젝트는 Raspberry Pi의 GPIO 및 SPI 하드웨어를 사용하므로, 해당 장치가 연결되고 설정된 환경에서 실행해야 합니다.

## 7. 향후 개선 사항

- 최고 점수 저장 및 기록 조회
- 소행성 및 에너지 구슬 생성 밸런스 조정
- 게임 일시정지 기능
- 추가 아이템 또는 보호막 시스템
- 게임 화면 및 시각 효과 개선

## 8. 개발 기록 및 시연

개발 과정과 주요 변경 사항은 GitHub 커밋 기록을 통해 관리합니다.

- **GitHub:** https://github.com/sanghyeok8473/star-survivor-raspberry-pi
- **시연 영상:** 추후 추가 예정
