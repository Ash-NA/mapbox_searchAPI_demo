import os
import pandas as pd
import requests
import uuid
import json

# Mapbox APIのエンドポイント
api_endpoint = "https://api.mapbox.com/search/v1/suggest/{search_text}"

# 設定ファイルからアクセストークンを読み込む
with open("config.js", "r") as config_file:
    config = json.load(config_file)
    access_token = config.get("access_token")

if not access_token:
    raise ValueError("アクセストークンが設定ファイルに見つかりません。")

# 対象のディレクトリ
input_directory = "input"  # 自分のディレクトリを指定してください
output_directory = "output"  # 結果を保存するディレクトリを指定してください

# ディレクトリ内のCSVファイルを処理
for root, dirs, files in os.walk(input_directory):
    for filename in files:
        if filename.endswith(".csv"):
            input_csv_path = os.path.join(root, filename)

            # CSVファイルの読み込み
            df = pd.read_csv(input_csv_path)

            # 新しい列を作成してAPIからの結果を格納
            df["matching_name"] = ""

            # APIリクエストと結果の取得
            for index, row in df.iterrows():
                search_text = row["ADDRESS"]
                url = api_endpoint.format(search_text=search_text)
                params = {
                    "language": "ja",
                    "limit": 10,
                    "session_token": str(uuid.uuid4()),
                    "country": "JP",
                    "access_token": access_token,
                    "types" : "address",
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if "suggestions" in data and len(data["suggestions"]) > 0:
                        matching_name = data["suggestions"][0]["matching_name"]
                        df.at[index, "matching_name"] = matching_name

            # 結果ファイルのパスを生成
            output_csv_filename = f"{os.path.splitext(filename)[0]}_result.csv"
            output_csv_path = os.path.join(output_directory, output_csv_filename)

            # 必要なカラムのみを選択して結果を保存
            selected_columns = ["INVOICE_NUMBER", "ADDRESS", "matching_name"]
            df[selected_columns].to_csv(output_csv_path, index=False)

            print(f"{filename} の結果を {output_csv_filename} に保存しました。")
