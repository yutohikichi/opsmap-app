import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ─── ページ設定 ─────────────────────────────────────────────────
st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# ─── セッション初期化 ──────────────────────────────────────────────
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {
        "経営本部": {
            "経理部": {},
            "人事部": {}
        }
    }
if "tasks" not in st.session_state:
    st.session_state.tasks = {}

# ─── ヘルパー関数 ─────────────────────────────────────────────────
def flatten_tree(tree, prefix=""):
    flat = []
    for key, val in tree.items():
        path = f"{prefix}/{key}" if prefix else key
        flat.append(path)
        if isinstance(val, dict):
            flat.extend(flatten_tree(val, path))
    return flat

def get_node_by_path(path_list, tree):
    for p in path_list:
        tree = tree.get(p, {})
    return tree

def delete_node(tree, path_list):
    if len(path_list) == 1:
        tree.pop(path_list[0], None)
    else:
        delete_node(tree[path_list[0]], path_list[1:])

# ─── サイドバー：部署追加・削除 ─────────────────────────────────────
tree = st.session_state.tree_data

st.sidebar.subheader("➕ 部署の追加")
parent_path = st.sidebar.selectbox("親部署を選択", [""] + flatten_tree(tree), key="add_parent")
new_dept = st.sidebar.text_input("新しい部署名を入力", key="add_name")
if st.sidebar.button("部署を追加する"):
    if new_dept:
        parent = get_node_by_path(parent_path.split("/") if parent_path else [], tree)
        if isinstance(parent, dict):
            parent[new_dept] = {}
            st.sidebar.success(f"部署「{new_dept}」を追加しました。")
            st.session_state.add_name = ""

st.sidebar.subheader("🗑️ 部署の削除")
delete_path = st.sidebar.selectbox("削除したい部署を選択", [""] + flatten_tree(tree), key="del_select")
if st.sidebar.button("部署を削除する"):
    if delete_path:
        delete_node(tree, delete_path.split("/"))
        st.sidebar.success(f"部署「{delete_path}」を削除しました。")
        st.session_state.del_select = ""

# ─── マインドマップ可視化 ───────────────────────────────────────────
st.subheader("🧠 組織マップ")

def build_nodes_edges(tree, parent=None, path="", depth=0):
    nodes, edges = [], []
    for key, val in tree.items():
        full_path = f"{path}/{key}" if path else key
        shape = "diamond" if depth == 0 else "circle"
        nodes.append(Node(id=full_path, label=key, size=30, shape=shape))
        if parent:
            edges.append(Edge(source=parent, target=full_path))
        if isinstance(val, dict):
            sn, se = build_nodes_edges(val, full_path, full_path, depth+1)
            nodes.extend(sn); edges.extend(se)
    return nodes, edges

nodes, edges = build_nodes_edges(tree)
config = Config(width=1000, height=700, directed=True, physics=True, hierarchical=True)
return_value = agraph(nodes=nodes, edges=edges, config=config)

# ─── ノードクリック時に「業務一覧＋追加フォーム」表示 ─────────────────
# 旧 API (clicked_node_id) or 新 API (selectedNode) の両対応
clicked = None
if return_value:
    # 古いバージョンの agraph
    if hasattr(return_value, "clicked_node_id"):
        clicked = return_value.clicked_node_id
    # 新しいバージョンの agraph（辞書を返す）
    elif isinstance(return_value, dict):
        clicked = (return_value.get("selectedNode")
                   or return_value.get("selected_node")
                   or return_value.get("nodeSelected"))

if clicked:
    st.markdown(f"## 📋 「{clicked}」の業務一覧と入力")
    # 初期化：部署ごとのタスクリスト
    tasks = st.session_state.tasks.setdefault(clicked, [])
    
    # 既存タスクの一覧表示
    if tasks:
        for i, t in enumerate(tasks, 1):
            st.markdown(f"**{i}. {t['name']}**  "
                        f"(頻度:{t['frequency']} 重要度:{t['importance']} 工数:{t['effort']}h/週 目安:{t['estimate']}分)")
            st.markdown(f"> 目的: {t['purpose']}")
    else:
        st.info("まだ業務が登録されていません。")
    
    st.markdown("---")
    # 新規業務追加フォーム
    with st.form(key=f"form_{clicked}", clear_on_submit=True):
        name       = st.text_input("業務名", key=f"name_{clicked}")
        purpose    = st.text_input("目的", key=f"purpose_{clicked}")
        frequency  = st.selectbox("頻度", ["毎日","毎週","毎月","その他"], key=f"freq_{clicked}")
        importance = st.slider("重要度(1-5)", 1,5,3, key=f"imp_{clicked}")
        effort     = st.number_input("工数(時間/週)", 0.0, 168.0, 0.0, 0.5, key=f"eff_{clicked}")
        estimate   = st.number_input("作業時間目安(分/タスク)", 0.0, 1440.0, 0.0, 5.0, key=f"est_{clicked}")
        submitted  = st.form_submit_button("➕ 業務を追加")
        if submitted:
            st.session_state.tasks[clicked].append({
                "name": name,
                "purpose": purpose,
                "frequency": frequency,
                "importance": importance,
                "effort": effort,
                "estimate": estimate
            })
            st.success("新しい業務を追加しました！")


