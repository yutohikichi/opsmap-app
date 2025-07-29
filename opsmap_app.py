import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(layout="wide")

st.title("OpsMap™：組織マインドマップ")

# 初期ノード定義（セッションステートに保存）
if "nodes" not in st.session_state:
    st.session_state.nodes = [Node(id="代表", label="代表", size=25)]
    st.session_state.edges = []
    st.session_state.contents = {}  # 各ノードに紐づく業務内容

# UI入力
col1, col2 = st.columns([3, 1])

with col2:
    with st.form("form", clear_on_submit=True):
        parent = st.selectbox("親部署を選択", options=[node.id for node in st.session_state.nodes])
        new_dept = st.text_input("新しい部署名")
        submitted = st.form_submit_button("部署を追加")
        if submitted and new_dept:
            st.session_state.nodes.append(Node(id=new_dept, label=new_dept))
            st.session_state.edges.append(Edge(source=parent, target=new_dept))
            st.session_state.contents[new_dept] = ""  # 業務内容初期化

# マインドマップ表示
config = Config(width=1000, height=600, directed=True, physics=True, hierarchical=True)
return_value = agraph(nodes=st.session_state.nodes,
                      edges=st.session_state.edges,
                      config=config)

# ノードクリック時の処理
if return_value and return_value.clicked_node_id:
    clicked = return_value.clicked_node_id
    st.subheader(f"🗂️ {clicked} の業務内容")

    # 入力＆保存
    content = st.text_area("業務内容を入力", value=st.session_state.contents.get(clicked, ""), height=200)
    if st.button("保存", key=f"save_{clicked}"):
        st.session_state.contents[clicked] = content
        st.success("保存しました ✅")

# 保存表示（デバッグ用）
with st.expander("📋 保存された業務一覧"):
    for dept, desc in st.session_state.contents.items():
        st.markdown(f"**{dept}**: {desc}")
