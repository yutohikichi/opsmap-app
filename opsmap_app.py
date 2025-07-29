import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ─── ページ設定 ─────────────────────────────────────────────────
st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# ─── セッション初期化 ──────────────────────────────────────────────
if "tree_data" not in st.session_state:
    # 初期データに全項目を入れておく
    st.session_state.tree_data = {
        "経営本部": {
            "経理部": {"業務": "", "頻度": "毎週", "重要度": 3, "工数": 0.0, "時間目安": 0.0},
            "人事部": {"業務": "", "頻度": "毎週", "重要度": 3, "工数": 0.0, "時間目安": 0.0},
        }
    }

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

# ─── サイドバー：部署追加・削除・業務入力 ──────────────────────────
tree = st.session_state.tree_data

# 部署追加
st.sidebar.subheader("➕ 部署の追加")
parent_path = st.sidebar.selectbox("親部署を選択", [""] + flatten_tree(tree), key="add_parent")
new_dept = st.sidebar.text_input("新しい部署名を入力", key="add_name")
if st.sidebar.button("部署を追加する"):
    if new_dept:
        parent = get_node_by_path(parent_path.split("/") if parent_path else [], tree)
        if isinstance(parent, dict):
            parent[new_dept] = {"業務": "", "頻度": "毎週", "重要度": 3, "工数": 0.0, "時間目安": 0.0}
            st.sidebar.success(f"部署「{new_dept}」を追加しました。")
            st.session_state.add_name = ""

# 部署削除
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

# ─── ノードクリック時：業務詳細フォーム表示 ─────────────────────────
if return_value and return_value.clicked_node_id:
    clicked = return_value.clicked_node_id
    st.markdown(f"### ✏️ 「{clicked}」の業務詳細を編集")
    node = get_node_by_path(clicked.split("/"), tree)
    if isinstance(node, dict):
        # 各項目の初期値取得
        task = node.get("業務", "")
        freq = node.get("頻度", "毎週")
        imp  = node.get("重要度", 3)
        effort = node.get("工数", 0.0)
        estimate = node.get("時間目安", 0.0)

        # 入力フォーム
        new_task     = st.text_area("業務内容", value=task, height=150)
        new_freq     = st.selectbox("頻度", ["毎日","毎週","毎月","その他"], index=["毎日","毎週","毎月","その他"].index(freq))
        new_imp      = st.slider("重要度 (1-5)", min_value=1, max_value=5, value=imp)
        new_effort   = st.number_input("工数 (時間/週)", min_value=0.0, value=effort, step=0.5)
        new_estimate = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, value=estimate, step=5.0)

        if st.button("保存", key=f"save_{clicked}"):
            node["業務"]     = new_task
            node["頻度"]     = new_freq
            node["重要度"]   = new_imp
            node["工数"]     = new_effort
            node["時間目安"] = new_estimate
            st.success("業務詳細を保存しました。")


