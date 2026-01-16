# 🛒 Seoul Local Market Analysis Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41.0-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)

서울시 열린데이터 광장 API를 활용하여 상권 데이터를 수집, 전처리하고 시각화하는 **E2E(End-to-End) 데이터 파이프라인 및 대시보드** 프로젝트입니다.

## 📸 대시보드 주요 화면

| **메인 대시보드 (Dashboard Main)** | **지역별 상세 분석 (Regional Analysis)** |
|:---:|:---:|
| ![Main Screen](images/dashboard_main.png) | ![Chart](images/regional_chart.png) |
> *현재 대시보드는 서울시 상권 API를 통해 수집된 **약 300,000건의 대규모 데이터**를 기반으로 분석한 결과입니다.*

---
## 🎯 Project Motivation: Why Hyperlocal Data?

이 프로젝트는 **당근마켓의 핵심 가치인 '하이퍼로컬(Hyperlocal)' 데이터**를 엔지니어링 관점에서 다루기 위해 시작되었습니다.

지역 생활 커뮤니티 플랫폼에서 **'동네 가게(Local Business)'의 생애주기(개업/폐업)** 를 파악하는 것은 매우 중요한 도메인 지식입니다. 저는 서울시 상권 데이터를 활용하여 다음과 같은 엔지니어링 및 비즈니스 목표를 달성하고자 했습니다.

1.  **로컬 데이터 파이프라인 구축:** 방대한 지역 상권 데이터를 안정적으로 수집·적재하여, **비즈프로필(Biz Profile)** 등 로컬 광고 타겟팅에 활용 가능한 데이터 셋을 구축하는 과정을 시뮬레이션했습니다.
2.  **데이터 기반의 동네 이해:** 단순한 수집을 넘어, 자치구별/업종별 활성도를 시각화함으로써 **"어떤 동네가 뜨고 있는지"** 를 데이터로 증명하는 대시보드를 구현했습니다.
3.  **대용량 처리 최적화:** 약 30만 건의 데이터를 로컬 환경에서 효율적으로 처리하기 위해 API 페이지네이션과 메모리 최적화를 고려한 파이프라인을 설계했습니다.

---

## 🚀 주요 기능 (Key Features)

### 1. 안정적인 데이터 수집 파이프라인 (`src/collector.py`)
- **페이지네이션 자동 처리:** API의 페이지네이션을 자동으로 순회하며 대용량 데이터를 누락 없이 수집합니다.
- **수집량 제어(Safety Limit):** API 서버 과부하 방지 및 빠른 테스트를 위해 `limit` 파라미터를 지원합니다. (기본값: 20,000건 / 제한 해제 시 약 60만 건 전수 조사 가능)
- **예외 처리(Error Handling):** 네트워크 불안정이나 API 응답 오류 발생 시에도 프로세스가 중단되지 않고 적절히 예외를 처리하도록 구현했습니다.

### 2. 데이터 전처리 및 가공 (`src/preprocessor.py`)
- **스타 스키마(Star Schema) 설계:** 점포 정보(Fact Table)와 위치/상권 정보(Dimension Table)를 결합(Merge)하여 분석에 최적화된 형태로 가공합니다.
- **인메모리 처리:** API로 수집된 메타데이터를 메모리 내에서 즉시 매핑하여 파일 I/O 비용을 최소화하고 처리 속도를 높였습니다.

### 3. 인터랙티브 대시보드 (`app.py`)
- **Streamlit & Plotly 시각화:** 사용자가 직접 필터를 조작하여 실시간으로 변화하는 데이터를 동적으로 확인할 수 있습니다.
- **안전 종료 기능:** 로컬 환경에서의 불필요한 리소스 점유를 막기 위해, OS 프로세스 제어(`os.kill`)를 활용한 '서버 안전 종료' 기능을 구현했습니다.

### 4. 보안 관리 (Security)
- **API 키 분리:** 민감한 인증키는 소스코드에 하드코딩하지 않고 `config.py`로 분리하여 관리하며, `.gitignore` 설정을 통해 깃허브 저장소에 노출되지 않도록 처리했습니다.

---

## 🛠️ 프로젝트 구조

```bash
seoul-local-market-analysis/
├── 📂 data/                  # 수집 및 전처리된 CSV 데이터
├── 📂 images/                # README에 사용된 대시보드 스크린샷
├── 📂 src/
│   ├── collector.py         # 서울시 API 데이터 수집 모듈
│   └── preprocessor.py      # 데이터 병합 및 정제 모듈
├── .gitignore               # 보안 및 설정 파일 제외 설정
├── app.py                   # Streamlit 대시보드 메인 애플리케이션
├── config_template.py       # API 키 설정 예시 파일
├── requirements.txt         # 의존성 패키지 목록
└── README.md                # 프로젝트 문서
```

---

## 💻 실행 방법 (How to Run)

이 프로젝트는 로컬 환경에서 다음과 같은 순서로 실행할 수 있습니다.

### 1. 환경 설정 (Prerequisites)
프로젝트를 클론(Clone)하고 필요한 라이브러리를 설치합니다.
```bash
# 1. 저장소 복제
git clone [https://github.com/JamesRhee1/seoul-local-market-analysis.git](https://github.com/JamesRhee1/seoul-local-market-analysis.git)
cd seoul-local-market-analysis

# 2. 필수 패키지 설치
pip install -r requirements.txt
```

### 2. API Key Setup (Optional)
💡 **Note:** 이 저장소에는 **약 300,000건의 전처리된 데이터(`data/seoul_market_final.csv`)가 이미 포함**되어 있습니다.
데이터를 새로 수집하지 않고 **대시보드만 실행할 경우, 이 단계는 건너뛰어도 됩니다.**

만약 최신 데이터를 직접 수집(`collector.py`)하려면, 서울 열린데이터 광장 인증키 설정이 필요합니다.

1. `config_template.py` 파일의 이름을 `config.py`로 변경합니다.
2. [서울 열린데이터 광장](https://data.seoul.go.kr/)에서 발급받은 인증키를 입력합니다.

```python
# config.py

# 서울 열린데이터 광장 인증키 입력
SEOUL_API_KEY = "YOUR_ACCESS_KEY_HERE"