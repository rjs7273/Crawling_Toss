# csv 파일 저장 및 데이터 관리

import os
import pandas as pd


def get_latest_id(csv_filename):
    """기존 CSV 파일에서 첫 번째 ID 가져오기"""
    if os.path.exists(csv_filename):
        df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
        if not df_existing.empty:
            return str(df_existing.iloc[0]["id"])
    return "0"

def save_to_csv(data, csv_filename):
    """새로운 데이터 CSV에 저장 (티커 정보 포함)"""
    df_new = pd.DataFrame(data)

    if os.path.exists(csv_filename):
        df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
        df_new = df_new.drop_duplicates(subset=["id"], keep="first")
        df_combined = pd.concat([df_new, df_existing], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(csv_filename, index=False, encoding="utf-8-sig")
