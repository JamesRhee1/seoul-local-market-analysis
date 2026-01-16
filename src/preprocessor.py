import pandas as pd
import requests
import os
import sys

# -----------------------------------------------------------------------------
# [보안 설정] 부모 폴더(루트)의 config.py에서 API 키를 가져옵니다.
# -----------------------------------------------------------------------------
# 현재 파일(preprocessor.py)의 부모의 부모 폴더(루트) 경로를 찾음
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

try:
    from config import SEOUL_API_KEY
except ImportError:
    print("[ERROR] config.py 파일을 찾을 수 없습니다. API 키 설정이 필요합니다.")
    SEOUL_API_KEY = ""

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(root_dir, "data")

def merge_location_data():
    """
    수집된 상권 점포 데이터(Fact Table)에 위치 정보(Dimension Table)를 결합
    - Join Key: TRDAR_CD (상권코드)
    """
    # config.py에서 가져온 키 사용
    KEY = SEOUL_API_KEY
    
    if not KEY or KEY == "여기에_인증키를_입력하세요":
        print("[ERROR] 유효한 API 키가 없습니다. config.py를 확인해주세요.")
        return

    # 1. 원본 데이터 로드 확인
    csv_path = os.path.join(DATA_DIR, "seoul_market_data.csv")
    if not os.path.exists(csv_path):
        print("[ERROR] 데이터 파일이 존재하지 않습니다. collector 모듈을 먼저 실행하십시오.")
        return

    # 데이터 타입 통일 (Merge Key인 상권코드를 문자열로 변환)
    print("[INFO] 원본 데이터 로딩 중...")
    try:
        fact_df = pd.read_csv(csv_path)
        fact_df['TRDAR_CD'] = fact_df['TRDAR_CD'].astype(str)
        print(f"[INFO] 원본 데이터 로드 완료: {len(fact_df)} rows")
    except Exception as e:
        print(f"[ERROR] CSV 파일 읽기 실패: {e}")
        return

    # 2. 위치 메타데이터(상권 영역) API 수집
    SERVICE_LOC = "TbgisTrdarRelm"
    
    all_loc = []
    start = 1
    BATCH_SIZE = 1000
    
    print("[INFO] 위치 메타데이터(Dimension Table) 수집 시작...")
    
    while True:
        url = f"http://openapi.seoul.go.kr:8088/{KEY}/json/{SERVICE_LOC}/{start}/{start + BATCH_SIZE - 1}/"
        try:
            res = requests.get(url).json()
            if SERVICE_LOC in res and 'row' in res[SERVICE_LOC]:
                rows = res[SERVICE_LOC]['row']
                all_loc.extend(rows)
                
                # 다음 페이지 이동
                start += BATCH_SIZE
                
                if len(rows) < BATCH_SIZE:
                    break
            else:
                break
        except Exception as e:
            print(f"[ERROR] 위치 데이터 수집 중 오류: {e}")
            break
            
    # 중복 제거 및 필요한 컬럼 추출
    if not all_loc:
        print("[ERROR] 위치 데이터를 가져오지 못했습니다. API 키나 서버 상태를 확인하세요.")
        return

    dim_df = pd.DataFrame(all_loc)[['TRDAR_CD', 'SIGNGU_CD_NM']].drop_duplicates()
    dim_df['TRDAR_CD'] = dim_df['TRDAR_CD'].astype(str)
    
    print(f"[INFO] 위치 메타데이터 확보: {len(dim_df)}건")
    
    # 3. 데이터 결합 (Left Join)
    print("[INFO] 데이터 결합(Merge) 진행 중...")
    merged_df = pd.merge(fact_df, dim_df, on='TRDAR_CD', how='left')
    
    # 결합 결과 검증 (매칭 실패 건수 확인)
    missing_cnt = merged_df['SIGNGU_CD_NM'].isnull().sum()
    if missing_cnt > 0:
        print(f"[WARN] 자치구 매칭 실패 데이터: {missing_cnt}건 (해당 데이터는 위치 정보가 없음)")
    
    # 4. 최종 결과 저장
    final_path = os.path.join(DATA_DIR, "seoul_market_final.csv")
    merged_df.to_csv(final_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 전처리 완료. 최종 데이터 저장됨: {final_path}")

if __name__ == "__main__":
    merge_location_data()