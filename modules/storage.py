# import os
# import pandas as pd

# def get_latest_id(csv_filename):
#     """기존 CSV 파일에서 첫 번째 ID 가져오기 (빈 파일 처리)"""
#     if os.path.exists(csv_filename) and os.path.getsize(csv_filename) > 0:
#         df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
#         return str(df_existing.iloc[0]["id"]) if not df_existing.empty else "0"
#     return "0"

# def save_to_csv(data, csv_filename):
#     """새로운 데이터 CSV에 저장 (티커 정보 + 종목명 포함)"""
#     df_new = pd.DataFrame(data)

#     if os.path.exists(csv_filename) and os.path.getsize(csv_filename) > 0:
#         df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
#         df_new = df_new.drop_duplicates(subset=["id"], keep="first")
#         df_combined = pd.concat([df_new, df_existing], ignore_index=True)
#     else:
#         df_combined = df_new

#     df_combined.to_csv(csv_filename, index=False, encoding="utf-8-sig")


import os
import pandas as pd

def get_latest_id(csv_filename):
    """기존 CSV 파일에서 첫 번째 ID 가져오기 (빈 파일 처리)"""
    if os.path.exists(csv_filename):
        if os.path.getsize(csv_filename) > 0:  # 파일이 존재하고 크기가 0보다 클 때만 실행
            df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
            return str(df_existing.iloc[0]["id"]) if not df_existing.empty else "0"
    return "0"

def save_to_csv(data, csv_filename):
    """새로운 데이터 CSV에 저장 (빈 파일 처리)"""
    df_new = pd.DataFrame(data)

    if os.path.exists(csv_filename):
        if os.path.getsize(csv_filename) > 0:  # 파일이 존재하지만 비어있는 경우 방지
            df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
            df_new = df_new.drop_duplicates(subset=["id"], keep="first")
            df_combined = pd.concat([df_new, df_existing], ignore_index=True)
        else:
            df_combined = df_new  # 파일이 있지만 비어 있으면 새 데이터만 저장
    else:
        df_combined = df_new  # 파일이 없으면 새 데이터로 생성

    df_combined.to_csv(csv_filename, index=False, encoding="utf-8-sig")
