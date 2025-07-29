import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# ─── セッション初期化 ──────────────────────────────────────────────
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {
        "経営本部": {
            "経理部": {"業務": ""},
            "人事部": {"業務": ""}
        }
    }

# ─── ユーティリティ関数 ───────────────────────────────────────────
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
        if p in tree:
            tree = tree[p]
        else:
            return None
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
parent_path = st.sidebar.selectbox(
    "親部署を選択",
    [""] + flatten_tree(tree),
    key="add_parent"
)
new_dept = st.sidebar.text_input("新しい部署名", key="add_name")
if st.sidebar.button("部署を追加する"):
    if new_dept:
        parent = get_node_by_path(parent_path.split("/") if parent_path else [], tree)
        if parent is not None and isinstance(parent, dict):
            parent[new_dept] = {"業務": ""}
            st.sidebar.success(f"部署「{new_dept}」を追加しました。")
            st.session_state.add_name = ""  # 入力クリア

# 部署削除
st.sidebar.subheader("🗑️ 部署の削除")
delete_path = st.sidebar.selectbox(
    "削除したい部署を選択",
    [""] + flatten_tree(tree),
    key="del_select"
)
if st.sidebar.button("部署を削除する"):
    if delete_path:
        delete_node(tree, delete_path.split("/"))
        st.sidebar.success(f"部署「{delete_path}」を削除しました。")
        st.session_state.del_select = ""  # 選択クリア

# 業務入力
st.sidebar.subheader("📝 業務入力")
select_path = st.sidebar.selectbox(
    "部署を選択",
    [""] + flatten_tree(tree),
    key="task_select"
)
if select_path:
    node = get_node_by_path(select_path.split("/"), tree)
    if node is not None and isinstance(node, dict):
        current = node.get("業務", "")
        new_task = st.sidebar.text_area("業務内容", current, key="task_area")
        if st.sidebar.button("業務を保存", key="task_save"):
            node["業務"] = new_task
            st.sidebar.success("業務を更新しました。")

# ─── マインドマップ可視化 ───────────────────────────────────────────
st.subheader("🧠 組織マップ")

def build_nodes_edges(tree, parent=None, path="", depth=0):
    nodes, edges = [], []
    for key, val in tree.items():
        full_path = f"{path}/{key}" if path else key
        shape = "diamond" if depth == 0 else "circle"
        node_id = full_path
        nodes.append(Node(id=node_id, label=key, size=30, shape=shape))
        if parent:
            edges.append(Edge(source=parent, target=node_id))
        if isinstance(val, dict):
            subnodes, subedges = build_nodes_edges(val, node_id, full_path, depth+1)
            nodes.extend(subnodes)
            edges.extend(subedges)
    return nodes, edges

nodes, edges = build_nodes_edges(tree)
config = Config(
    width=1000,
    height=700,
    directed=True,
    physics=True,
    hierarchical=True
)
return_value = agraph(nodes=nodes, edges=edges, config=config)

# ─── ノードクリック時に業務内容をメイン画面で表示・編集 ─────────────────
if return_value and return_value.clicked_node_id:
    clicked = return_value.clicked_node_id
    st.markdown(f"### ✏️ 「{clicked}」の業務内容")
    node = get_node_by_path(clicked.split("/"), tree)
    if node is not None and isinstance(node, dict):
        current_content = node.get("業務", "")
        new_content = st.text_area(
            "業務内容を入力してください",
            value=current_content,
            key=f"main_area_{clicked}"
        )
        if st.button("保存", key=f"main_save_{clicked}"):
            node["業務"] = new_content
            st.success("保存しました。")

