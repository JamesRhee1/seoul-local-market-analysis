import requests
import pandas as pd
import os
import sys

# -----------------------------------------------------------------------------
# [보안 설정] 부모 폴더(루트)의 config.py에서 API 키를 가져옵니다.
# -----------------------------------------------------------------------------
# 현재 파일(collector.py)의 부모의 부모 폴더(루트) 경로를 찾음
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

try:
    from config import SEOUL_API_KEY
except ImportError:
    print("[ERROR] config.py 파일을 찾을 수 없습니다. API 키 설정이 필요합니다.")
    SEOUL_API_KEY = ""  # 에러 방지용 빈 값

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------
# 데이터 저장 디렉토리 설정 (루트 기준 data 폴더)
DATA_DIR = os.path.join(root_dir, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def collect_store_data(limit=20000): 
    """
    서울시 상권 점포 데이터를 수집하여 CSV로 저장
    
    Args:
        limit (int): 수집할 최대 데이터 개수. None 또는 0 입력 시 전체(무제한) 수집.
    """
    # config.py에서 가져온 키 사용
    KEY = SEOUL_API_KEY 
    
    if not KEY or KEY == "여기에_인증키를_입력하세요":
        print("[ERROR] 유효한 API 키가 없습니다. config.py를 확인해주세요.")
        return

    SERVICE = "VwsmTrdarStorQq"
    TYPE = "json"
    BATCH_SIZE = 1000
    
    all_data = []
    start_index = 1
    
    # limit이 없으면 "전체 모드", 있으면 "제한 모드"
    target_desc = "All (Unlimited)" if not limit else f"{limit} rows"
    print(f"[INFO] 데이터 수집 프로세스 시작 (Target: {target_desc})")
    
    while True:
        # 리미트가 설정된 경우, 목표치를 넘었는지 미리 체크
        if limit and len(all_data) >= limit:
            print("[INFO] 설정된 제한(Limit)에 도달하여 수집을 종료합니다.")
            break

        end_index = start_index + BATCH_SIZE - 1
        url = f"http://openapi.seoul.go.kr:8088/{KEY}/{TYPE}/{SERVICE}/{start_index}/{end_index}/"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[ERROR] API 호출 실패: Status Code {response.status_code}")
                break
                
            data = response.json()
            
            if SERVICE in data and 'row' in data[SERVICE] and data[SERVICE]['row']:
                rows = data[SERVICE]['row']
                all_data.extend(rows)
                
                # 10,000건 단위로 로그 출력
                if len(all_data) % 10000 == 0:
                    print(f"[INFO] {len(all_data)}건 수집 중...")
                
                start_index += BATCH_SIZE
                
                # 마지막 페이지 체크
                if len(rows) < BATCH_SIZE:
                    print("[INFO] 마지막 페이지 도달 (데이터 끝).")
                    break
            else:
                print("[INFO] 더 이상 유효한 데이터가 없습니다.")
                break
                
        except Exception as e:
            print(f"[ERROR] 프로세스 실행 중 예외 발생: {e}")
            break
            
    # 데이터프레임 변환 및 저장
    if all_data:
        save_path = os.path.join(DATA_DIR, "seoul_market_data.csv")
        try:
            pd.DataFrame(all_data).to_csv(save_path, index=False, encoding="utf-8-sig")
            print(f"[INFO] 파일 저장 완료: {save_path} (Total: {len(all_data)} rows)")
        except Exception as e:
            print(f"[ERROR] 파일 저장 실패: {e}")
    else:
        print("[WARN] 수집된 데이터가 없어 파일을 저장하지 않았습니다.")

if __name__ == "__main__":
    # GitHub 업로드용: 기본 20,000개로 설정
    collect_store_data(limit=20000)