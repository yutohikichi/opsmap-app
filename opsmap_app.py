# Streamlitアプリ試作版（FlowBuilder + 業務可視化アプリ + FlowBuilder機能 + スキルマップ + スケジューラ）
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os
import graphviz
from datetime import datetime, timedelta

st.set_page_config(page_title="BackOps360 FlowBuilder", layout="wide")

# ---------- ファイル保存/読み込みユーティリティ ----------
FLOW_PATH = "flow_data.json"

def load_flow():
    if os.path.exists(FLOW_PATH):
        try:
            with open(FLOW_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("❌ flow_data.json の読み込み中にエラーが発生しました。ファイル形式が不正です。初期化します。")
            return {
                "flow_id": "flow_001",
                "flow_name": "請求書発行フロー",
                "description": "請求内容確認から請求書送付までの流れ",
                "nodes": [],
                "connections": []
            }
    else:
        return {
            "flow_id": "flow_001",
            "flow_name": "請求書発行フロー",
            "description": "請求内容確認から請求書送付までの流れ",
            "nodes": [],
            "connections": []
        }

def save_flow(flow):
    try:
        with open(FLOW_PATH, "w", encoding="utf-8") as f:
            json.dump(flow, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ 保存に失敗しました: {e}")

flow = load_flow()

st.sidebar.title("🔧 Flow設定")
flow["flow_name"] = st.sidebar.text_input("フロー名", value=flow["flow_name"])
flow["description"] = st.sidebar.text_area("説明", value=flow["description"])
if st.sidebar.button("💾 保存する"):
    save_flow(flow)
    st.sidebar.success("保存しました")

# ▼ ノード編集・削除（省略：前回と同様）...
# ▼ OpsMap™（省略：前回と同様）...
# ▼ Smart Task Dictionary（省略：前回と同様）...
# ▼ FlowBuilder（省略：前回と同様）...
# ▼ スキルマップ＋キャリアナビゲーション（省略：前回と同様）...

# ▼ 業務カレンダー＋スケジューラ
st.title("🗓 業務スケジューラ & カレンダー")
st.markdown("""
- 頻度・工数・担当者情報からスケジュールを自動構成
- 繁忙期・週次/月次/年次を一覧表示
""")

calendar_data = []
today = datetime.today()
for node in flow.get("nodes", []):
    label = node.get("label")
    if not label:
        continue
    freq = node.get("frequency", "週次")
    assignee = node.get("assignee", "未設定")
    duration = node.get("effort", 1)  # 工数（時間）

    for i in range(4):
        if freq == "日次":
            start = today + timedelta(days=i)
        elif freq == "週次":
            start = today + timedelta(weeks=i)
        elif freq == "月次":
            start = today + timedelta(weeks=4*i)
        else:
            continue

        calendar_data.append({
            "業務": label,
            "担当者": assignee,
            "開始日": start.strftime("%Y-%m-%d"),
            "工数(h)": duration
        })

if calendar_data:
    df_calendar = pd.DataFrame(calendar_data)
    st.dataframe(df_calendar)

    try:
        fig = px.timeline(df_calendar, x_start="開始日", x_end="開始日", y="業務", color="担当者",
                          title="🗓 業務カレンダー（今後4週分）",
                          labels={"開始日": "日付"})
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ タイムライン描画エラー: {e}")
else:
    st.info("業務に頻度情報が設定されていないか、ノードが未登録です。")
