# Streamlitアプリ試作版（FlowBuilder + 業務可視化アプリ）
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="BackOps360 FlowBuilder", layout="wide")

# ---------- ファイル保存/読み込みユーティリティ ----------
FLOW_PATH = "flow_data.json"

def load_flow():
    if os.path.exists(FLOW_PATH):
        with open(FLOW_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "flow_id": "flow_001",
            "flow_name": "請求書発行フロー",
            "description": "請求内容確認から請求書送付までの流れ",
            "nodes": [],
            "connections": []
        }

def save_flow(flow):
    with open(FLOW_PATH, "w", encoding="utf-8") as f:
        json.dump(flow, f, ensure_ascii=False, indent=2)

flow = load_flow()

st.sidebar.title("🔧 Flow設定")
flow["flow_name"] = st.sidebar.text_input("フロー名", value=flow["flow_name"])
flow["description"] = st.sidebar.text_area("説明", value=flow["description"])
if st.sidebar.button("💾 保存する"):
    save_flow(flow)
    st.sidebar.success("保存しました")

st.title("📘 BackOps360 FlowBuilder")
st.caption("業務とスキルを可視化するバックオフィス支援アプリ")

st.subheader("📊 スキルマトリクス（業務 × スキル）")
all_skills = sorted(set(skill for node in flow["nodes"] for skill in node.get("skills", [])))
matrix_data = []
for node in flow["nodes"]:
    row = {"業務": node.get("label", "")}
    for skill in all_skills:
        row[skill] = "✅" if skill in node.get("skills", []) else ""
    matrix_data.append(row)
df_matrix = pd.DataFrame(matrix_data)
st.dataframe(df_matrix, use_container_width=True)

st.subheader("📈 スキル別自己評価平均グラフ")
skill_scores = {}
skill_counts = {}
for node in flow["nodes"]:
    for skill in node.get("skills", []):
        skill_scores[skill] = skill_scores.get(skill, 0) + node.get("self_rating", 0)
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
avg_skill_ratings = {
    skill: round(skill_scores[skill] / skill_counts[skill], 2)
    for skill in skill_scores
}
df_avg = pd.DataFrame({
    "スキル": list(avg_skill_ratings.keys()),
    "平均評価": list(avg_skill_ratings.values())
})
fig_bar = px.bar(df_avg, x="スキル", y="平均評価", range_y=[0, 5])
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📥 CSVエクスポート - 業務プロセスデータ")
def flatten_node(node):
    return {
        "業務ID": node.get("node_id"),
        "業務名": node.get("label"),
        "種別": node.get("type"),
        "詳細": node.get("details"),
        "担当者": ", ".join(node.get("owners", [])),
        "スキル": ", ".join(node.get("skills", [])),
        "自己評価": node.get("self_rating", 0),
        "工数(分)": node.get("effort", 0),
        "頻度": node.get("frequency", ""),
        "重要度": node.get("priority", 0),
        "優先度スコア": node.get("effort", 0) * {
            "月1回": 1, "週1回": 4, "毎日": 20
        }.get(node.get("frequency", ""), 1) * node.get("priority", 0),
        "担当者数": len(node.get("owners", []))
    }
df_nodes = pd.DataFrame([flatten_node(n) for n in flow["nodes"]])

st.subheader("📊 業務優先度 × 属人化リスクレーダーチャート")
if not df_nodes.empty:
    radar_data = df_nodes[["業務名", "優先度スコア", "担当者数"]].copy()
    radar_data["属人化リスク"] = radar_data["担当者数"].apply(lambda x: 5 - min(x, 5))
    radar_fig = px.line_polar(radar_data, r="優先度スコア", theta="業務名", line_close=True, name="優先度スコア")
    radar_fig.add_barpolar(r=radar_data["属人化リスク"], theta=radar_data["業務名"], name="属人化リスク")
    st.plotly_chart(radar_fig, use_container_width=True)

csv = df_nodes.to_csv(index=False).encode("utf-8")
st.download_button("📤 CSVとしてダウンロード", data=csv, file_name="業務プロセス一覧.csv", mime="text/csv")
