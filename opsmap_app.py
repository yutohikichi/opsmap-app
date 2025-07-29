import streamlit as st
from graphviz import Digraph
from collections import defaultdict

# 初期化
if "departments" not in st.session_state:
    st.session_state.departments = []
if "tasks" not in st.session_state:
    st.session_state.tasks = defaultdict(list)

# ページ設定
st.set_page_config(page_title="OpsMap™", layout="wide")
st.title("🧠 OpsMap™ 組織構造 × 業務棚卸しツール")

# 展開方向の選択
direction = st.radio("🧭 マインドマップの展開方向", ["横展開", "縦展開"], horizontal=True)

# マインドマップ描画関数
def draw_mindmap(departments, direction="横展開"):
    dot = Digraph()
    dot.attr(rankdir="LR" if direction == "横展開" else "TB")
    for dept in departments:
        dot.node(dept["name"])
    for dept in departments:
        if dept["parent"]:
            dot.edge(dept["parent"], dept["name"])
    return dot

# 部署登録フォーム
with st.form("add_dept"):
    st.subheader("🏢 部署を追加")
    dept_name = st.text_input("部署名")
    parent = st.selectbox("上位部署", ["（なし）"] + [d["name"] for d in st.session_state.departments])
    submitted = st.form_submit_button("➕ 登録")
    if submitted:
        if dept_name and not any(d["name"] == dept_name for d in st.session_state.departments):
            st.session_state.departments.append({
                "name": dept_name,
                "parent": None if parent == "（なし）" else parent
            })
            st.success(f"{dept_name} を追加しました ✅")
        else:
            st.warning("未入力または重複しています")

# 組織図表示
if st.session_state.departments:
    st.subheader("📌 組織マインドマップ")
    st.graphviz_chart(draw_mindmap(st.session_state.departments, direction))
else:
    st.info("まずは部署を追加してください。")

# 業務入力欄
st.subheader("📝 部署別の業務登録")
for dept in st.session_state.departments:
    with st.expander(f"📂 {dept['name']} の業務を登録"):
        with st.form(f"task_form_{dept['name']}"):
            task = st.text_input("業務名", key=f"task_{dept['name']}")
            purpose = st.text_input("目的", key=f"purpose_{dept['name']}")
            freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"], key=f"freq_{dept['name']}")
            effort = st.number_input("工数（時間/週）", min_value=0.0, max_value=168.0, step=0.5, key=f"effort_{dept['name']}")
            importance = st.slider("重要度", 1, 5, 3, key=f"importance_{dept['name']}")
            confirm = st.form_submit_button("✅ 業務を登録")
            if confirm and task:
                st.session_state.tasks[dept["name"]].append({
                    "業務名": task,
                    "目的": purpose,
                    "頻度": freq,
                    "工数": effort,
                    "重要度": importance
                })
                st.success("業務を登録しました")

# 業務一覧
st.subheader("📊 部署別の業務一覧")
for dept, tasklist in st.session_state.tasks.items():
    if tasklist:
        st.markdown(f"### 🏷 {dept}")
        for t in tasklist:
            st.markdown(f"- **{t['業務名']}** | 目的: {t['目的']} | 頻度: {t['頻度']} | 工数: {t['工数']}h/週 | 重要度: {t['重要度']}")


