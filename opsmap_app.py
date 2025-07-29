import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import urllib.parse

st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# -----------------------
# 初期データ
# -----------------------
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {}

tree = st.session_state.tree_data

# -----------------------
# ユーティリティ関数
# -----------------------
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

# -----------------------
# ページ切り替えチェック
# -----------------------
selected_node = st.query_params.get("selected_node")

if selected_node:
    # 業務詳細ページ
    clicked = urllib.parse.unquote(selected_node)
    node = get_node_by_path(clicked.split("/"), tree)

    if isinstance(node, dict) and "業務" in node:
        st.subheader(f"📝 業務詳細ページ：「{clicked}」")

        task = node.get("業務", "")
        freq = node.get("頻度", "毎週")
        imp = node.get("重要度", 3)
        effort = node.get("工数", 0.0)
        estimate = node.get("時間目安", 0.0)

        new_task = st.text_area("業務内容", value=task, height=150)
        new_freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"], index=["毎日", "毎週", "毎月", "その他"].index(freq))
        new_imp = st.slider("重要度 (1〜5)", 1, 5, value=imp)
        new_effort = st.number_input("工数 (時間/週)", min_value=0.0, value=effort, step=0.5)
        new_estimate = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, value=estimate, step=5.0)

        if st.button("保存（業務詳細ページ）"):
            node["業務"] = new_task
            node["頻度"] = new_freq
            node["重要度"] = new_imp
            node["工数"] = new_effort
            node["時間目安"] = new_estimate
            st.success("✅ 保存しました。")

        st.markdown(
            '''
            <br>
            <a href="javascript:history.back()">🔙 戻る</a> &nbsp;&nbsp;&nbsp;
            <a href="/">🏠 トップに戻る</a>
            ''',
            unsafe_allow_html=True
        )

else:
    # -----------------------
    # サイドバー: 部署と業務の追加/削除
    # -----------------------
    st.sidebar.subheader("➕ 部署の追加")
    parent_path = st.sidebar.selectbox("親部署を選択", [""] + flatten_tree(tree), key="add_parent")
    new_dept = st.sidebar.text_input("新しい部署名を入力", key="add_name")
    if st.sidebar.button("部署を追加する", key="add_button"):
        if new_dept:
            parent = get_node_by_path(parent_path.split("/") if parent_path else [], tree)
            if isinstance(parent, dict):
                parent[new_dept] = {}
                st.sidebar.success(f"部署「{new_dept}」を追加しました。")

    st.sidebar.subheader("🗑️ 部署の削除")
    delete_path = st.sidebar.selectbox("削除したい部署を選択", [""] + flatten_tree(tree), key="del_select")
    if st.sidebar.button("部署を削除する", key="delete_button"):
        if delete_path:
            delete_node(tree, delete_path.split("/"))
            st.sidebar.success(f"部署「{delete_path}」を削除しました。")

    st.sidebar.subheader("📄 業務の追加")
    target_dept_path = st.sidebar.selectbox("業務を追加する部署を選択", flatten_tree(tree), key="task_add_target")
    new_task_name = st.sidebar.text_input("業務名", key="task_add_name")
    if st.sidebar.button("業務を追加する", key="task_add_button"):
        if new_task_name:
            dept_node = get_node_by_path(target_dept_path.split("/"), tree)
            if isinstance(dept_node, dict):
                dept_node[new_task_name] = {"業務": "", "頻度": "毎週", "重要度": 3, "工数": 0.0, "時間目安": 0.0}
                st.sidebar.success(f"業務「{new_task_name}」を追加しました。")

    # -----------------------
    # マインドマップ表示
    # -----------------------
    st.subheader("🧠 組織マップ")

    def build_nodes_edges(tree, parent=None, path=""):
        nodes, edges = [], []
        for key, val in tree.items():
            full_path = f"{path}/{key}" if path else key

            is_task_node = isinstance(val, dict) and "業務" in val
            label = f"📝{key}" if is_task_node else f"◇{key}"
            shape = "box" if is_task_node else "diamond"
            size = 25 if is_task_node else 30

            nodes.append(Node(id=full_path, label=label, shape=shape, size=size))
            if parent:
                edges.append(Edge(source=parent, target=full_path))

            if isinstance(val, dict):
                sn, se = build_nodes_edges(val, full_path)
                nodes.extend(sn)
                edges.extend(se)

        return nodes, edges

    nodes, edges = build_nodes_edges(tree)
    config = Config(width=1000, height=700, directed=True, physics=True, hierarchical=True)
    return_value = agraph(nodes=nodes, edges=edges, config=config)

    if return_value and return_value.clicked_node_id:
        clicked_id = return_value.clicked_node_id
        node = get_node_by_path(clicked_id.split("/"), tree)
        if isinstance(node, dict) and "業務" in node:
            url_param = urllib.parse.quote(clicked_id)
            st.experimental_set_query_params(selected_node=url_param)
            st.rerun()
