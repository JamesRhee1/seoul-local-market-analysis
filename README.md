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
├── 📂 data/                  # 수집 및 전처리된 CSV 데이터 (Git 제외 가능)
├── 📂 src/
│   ├── collector.py         # 서울시 API 데이터 수집 모듈
│   └── preprocessor.py      # 데이터 병합 및 정제 모듈
├── .gitignore               # 보안 및 설정 파일 제외 설정
├── app.py                   # Streamlit 대시보드 메인 애플리케이션
├── config_template.py       # API 키 설정 예시 파일
├── requirements.txt         # 의존성 패키지 목록
└── README.md                # 프로젝트 문서