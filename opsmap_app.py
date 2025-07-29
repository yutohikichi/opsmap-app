import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# 初期化
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {
        "経営本部": {
            "経理部": {"業務": ""},
            "人事部": {"業務": ""}
        }
    }

def flatten_tree(tree, prefix=""):
    """階層構造をフラットにしてパスリストに"""
    flat = []
    for key, val in tree.items():
        path = f"{prefix}/{key}" if prefix else key
        flat.append(path)
        if isinstance(val, dict):
            flat.extend(flatten_tree(val, path))
    return flat

def get_node_by_path(path_list, tree):
    """パスリストに沿ってノード取得"""
    for p in path_list:
        if p in tree:
            tree = tree[p]
        else:
            return None
    return tree

def delete_node(tree, path_list):
    """パスリストに沿ってノード削除"""
    if len(path_list) == 1:
        tree.pop(path_list[0], None)
    else:
        delete_node(tree[path_list[0]], path_list[1:])

# ツリーデータ取得
tree_data = st.session_state.tree_data

# サイドバー：部署追加
st.sidebar.subheader("➕ 部署の追加")
parent_path = st.sidebar.selectbox("親部署の選択", [""] + flatten_tree(tree_data))
new_dept = st.sidebar.text_input("新しい部署名を入力")
if st.sidebar.button("部署を追加する") and new_dept:
    parent = get_node_by_path(parent_path.split("/") if parent_path else [], tree_data)
    if parent is not None and isinstance(parent, dict):
        parent[new_dept] = {"業務": ""}
        st.sidebar.success(f"{new_dept} を追加しました。")

# サイドバー：部署の削除
st.sidebar.subheader("🗑️ 部署の削除")
delete_path = st.sidebar.selectbox("削除したい部署を選択", [""] + flatten_tree(tree_data))
if st.sidebar.button("部署を削除する") and delete_path:
    delete_node(tree_data, delete_path.split("/"))
    st.sidebar.success(f"{delete_path} を削除しました。")

# サイドバー：業務の入力
st.sidebar.subheader("📝 業務入力")
select_path = st.sidebar.selectbox("部署の選択", [""] + flatten_tree(tree_data))
if select_path:
    node = get_node_by_path(select_path.split("/"), tree_data)
    if node is not None and isinstance(node, dict):
        current_task = node.get("業務", "")
        new_task = st.sidebar.text_area("業務内容", current_task)
        if st.sidebar.button("業務を保存"):
            node["業務"] = new_task
            st.sidebar.success("業務を更新しました。")

# 可視化：マインドマップ
st.subheader("🧠 組織マップ")

def build_nodes_edges(tree, parent=None, path=""):
    nodes, edges = [], []
    for key, val in tree.items():
        full_path = f"{path}/{key}" if path else key
        label = f"{key}\n{val['業務']}" if isinstance(val, dict) and "業務" in val else key
        node_id = full_path
        nodes.append(Node(id=node_id, label=label, size=30))
        if parent:
            edges.append(Edge(source=parent, target=node_id))
        if isinstance(val, dict):
            subnodes, subedges = build_nodes_edges(val, node_id, full_path)
            nodes.extend(subnodes)
            edges.extend(subedges)
    return nodes, edges

nodes, edges = build_nodes_edges(tree_data)

config = Config(width=1000,
                height=700,
                directed=True,
                physics=True,
                hierarchical=True)

agraph(nodes=nodes, edges=edges, config=config)
