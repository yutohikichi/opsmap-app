import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ─── ページ設定 ─────────────────────────────────────────────────
st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# ─── セッション初期化 ──────────────────────────────────────────────
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {"経営本部": {"経理部": {}, "人事部": {}}}
if "tasks" not in st.session_state:
    st.session_state.tasks = {}

# ─── ヘルパー関数 ─────────────────────────────────────────────────
def flatten_tree(tree, prefix=""):
    flat = []
    for k, v in tree.items():
        path = f"{prefix}/{k}" if prefix else k
        flat.append(path)
        if isinstance(v, dict):
            flat.extend(flatten_tree(v, path))
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

st.sidebar.subheader("🗑️ 部署の削除")
delete_path = st.sidebar.selectbox("削除したい部署を選択", [""] + flatten_tree(tree), key="del_select")
if st.sidebar.button("部署を削除する"):
    if delete_path:
        delete_node(tree, delete_path.split("/"))
        st.sidebar.success(f"部署「{delete_path}」を削除しました。")

# ─── マインドマップ可視化 ───────────────────────────────────────────
st.subheader("🧠 組織マップ")
def build_nodes_edges(tree, parent=None, path="", depth=0):
    nodes, edges = [], []
    for k, v in tree.items():
        full = f"{path}/{k}" if path else k
        shape = "diamond" if depth == 0 else "circle"
        nodes.append(Node(id=full, label=k, size=30, shape=shape))
        if parent:
            edges.append(Edge(source=parent, target=full))
        if isinstance(v, dict):
            sn, se = build_nodes_edges(v, full, full, depth+1)
            nodes.extend(sn); edges.extend(se)
    return nodes, edges

nodes, edges = build_nodes_edges(tree)
config = Config(width=900, height=600, directed=True, physics=True, hierarchical=True)
ret = agraph(nodes=nodes, edges=edges, config=config)

# ─── クリックされた部署を取得 ────────────────────────────────────
clicked = None
if ret:
    if hasattr(ret, "clicked_node_id"):
        clicked = ret.clicked_node_id
    elif isinstance(ret, dict):
        clicked = (ret.get("selectedNode")
                   or ret.get("selected_node")
                   or ret.get("nodeSelected"))

# ─── サイドバー：クリック部署の業務入力フォーム ───────────────────
if clicked:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"📝 「{clicked}」の業務入力")
    # リスト初期化
    tasks = st.session_state.tasks.setdefault(clicked, [])
    # 既存タスク表示
    if tasks:
        for i, t in enumerate(tasks, 1):
            st.sidebar.markdown(
                f"{i}. **{t['name']}** (頻度:{t['frequency']} 重要度:{t['importance']} 工数:{t['effort']}h)"
            )
    else:
        st.sidebar.info("まだ業務がありません。")

    # フォームで新規タスク追加
    with st.sidebar.form(key=f"form_{clicked}", clear_on_submit=True):
        name       = st.text_input("業務名", key=f"name_{clicked}")
        frequency  = st.selectbox("頻度", ["毎日","毎週","毎月","その他"], key=f"freq_{clicked}")
        importance = st.slider("重要度 (1-5)", 1, 5, 3, key=f"imp_{clicked}")
        effort     = st.number_input("工数 (時間/週)", 0.0, 168.0, 0.0, 0.5, key=f"eff_{clicked}")
        submitted  = st.form_submit_button("➕ 追加")
        if submitted:
            st.session_state.tasks[clicked].append({
                "name": name,
                "frequency": frequency,
                "importance": importance,
                "effort": effort
            })
            st.sidebar.success("業務を追加しました！")



