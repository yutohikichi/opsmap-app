import streamlit as st
import urllib.parse

st.set_page_config(page_title="OpsMap", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング")

# 初期データ
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {}

if "layout_direction" not in st.session_state:
    st.session_state.layout_direction = "vertical"

if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

tree = st.session_state.tree_data

# ユーティリティ関数
def flatten_tree(tree, prefix=""):
    flat = []
    for key, val in tree.items():
        path = f"{prefix}/{key}" if prefix else key
        flat.append(path)
        if isinstance(val, dict) and not ("業務" in val):
            flat.extend(flatten_tree(val, path))
    return flat

def get_node_by_path(path_list, tree):
    current = tree
    for p in path_list:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current

def delete_node(tree, path_list):
    if len(path_list) == 1:
        tree.pop(path_list[0], None)
    else:
        if path_list[0] in tree:
            delete_node(tree[path_list[0]], path_list[1:])

# ページ切り替えチェック
selected_node = st.session_state.get("selected_node")

if selected_node:
    clicked = selected_node
    node = get_node_by_path(clicked.split("/"), tree)

    if isinstance(node, dict) and "業務" in node:
        st.subheader(f"📝 業務詳細ページ：「{clicked}」")

        task = node.get("業務", "")
        freq = node.get("頻度", "毎週")
        imp = node.get("重要度", 3)
        effort = node.get("工数", 0.0)
        estimate = node.get("時間目安", 0.0)

        with st.form("task_form"):
            new_task = st.text_area("業務内容", value=task, height=150)
            new_freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"], index=["毎日", "毎週", "毎月", "その他"].index(freq))
            new_imp = st.slider("重要度 (1〜5)", 1, 5, value=imp)
            new_effort = st.number_input("工数 (時間/週)", min_value=0.0, value=effort, step=0.5)
            new_estimate = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, value=estimate, step=5.0)
            
            submitted = st.form_submit_button("保存（業務詳細ページ）")
            if submitted:
                node["業務"] = new_task
                node["頻度"] = new_freq
                node["重要度"] = new_imp
                node["工数"] = new_effort
                node["時間目安"] = new_estimate
                st.success("✅ 保存しました。")

        if st.button("🔙 トップに戻る"):
            st.session_state.selected_node = None
            st.rerun()

else:
    # サイドバーの設定
    with st.sidebar:
        st.subheader("➕ 部署の追加")
        parent_path = st.selectbox("親部署を選択", [""] + flatten_tree(tree), key="add_parent")
        new_dept = st.text_input("新しい部署名を入力", key="add_name")
        if st.button("部署を追加する", key="add_button"):
            if new_dept:
                if parent_path:
                    parent = get_node_by_path(parent_path.split("/"), tree)
                else:
                    parent = tree
                if isinstance(parent, dict):
                    parent[new_dept] = {}
                    st.success(f"部署「{new_dept}」を追加しました。")
                    st.rerun()

        st.subheader("🗑️ 部署の削除")
        delete_path = st.selectbox("削除したい部署を選択", [""] + flatten_tree(tree), key="del_select")
        if st.button("部署を削除する", key="delete_button"):
            if delete_path:
                delete_node(tree, delete_path.split("/"))
                st.success(f"部署「{delete_path}」を削除しました。")
                st.rerun()

        st.subheader("📄 業務の追加")
        if flatten_tree(tree):
            target_dept_path = st.selectbox("業務を追加する部署を選択", flatten_tree(tree), key="task_add_target")
            new_task_name = st.text_input("業務名", key="task_add_name")
            if st.button("業務を追加する", key="task_add_button"):
                if new_task_name and target_dept_path:
                    dept_node = get_node_by_path(target_dept_path.split("/"), tree)
                    if isinstance(dept_node, dict):
                        dept_node[new_task_name] = {"業務": "", "頻度": "毎週", "重要度": 3, "工数": 0.0, "時間目安": 0.0}
                        st.success(f"業務「{new_task_name}」を追加しました。")
                        st.rerun()

    st.subheader("🧠 組織マップ（ツリー表示）")

    def display_tree_interactive(tree, level=0, path=""):
        for key, val in tree.items():
            current_path = f"{path}/{key}" if path else key
            indent = "　" * level
            
            if isinstance(val, dict) and "業務" in val:
                # 業務ノード - クリック可能なボタン
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"📝 {key}", key=f"task_{current_path.replace('/', '_')}", help="クリックして詳細編集"):
                        st.session_state.selected_node = current_path
                        st.rerun()
                with col2:
                    task_content = val.get("業務", "未設定")
                    freq = val.get("頻度", "毎週")
                    imp = val.get("重要度", 3)
                    st.write(f"{indent}業務内容: {task_content[:50]}{'...' if len(task_content) > 50 else ''}")
                    st.write(f"{indent}頻度: {freq}, 重要度: {imp}")
            else:
                # 部署ノード
                st.write(f"{indent}◇ **{key}**")
                if isinstance(val, dict):
                    display_tree_interactive(val, level + 1, current_path)

    if tree:
        display_tree_interactive(tree)
        
        # 追加でグラフィカル表示も試す（オプション）
        st.subheader("📊 グラフィカル表示（実験的）")
        
        try:
            from streamlit_agraph import agraph, Node, Edge, Config
            
            def build_nodes_edges(tree, parent=None, path=""):
                nodes, edges = [], []
                for key, val in tree.items():
                    full_path = f"{path}/{key}" if path else key

                    is_task_node = isinstance(val, dict) and "業務" in val
                    label = f"📝{key}" if is_task_node else f"◇{key}"
                    shape = "box" if is_task_node else "diamond"
                    size = 25 if is_task_node else 30
                    color = "#FFE4B5" if is_task_node else "#87CEEB"

                    nodes.append(Node(id=full_path, label=label, shape=shape, size=size, color=color))
                    if parent:
                        edges.append(Edge(source=parent, target=full_path))

                    if isinstance(val, dict) and not ("業務" in val):
                        sub_nodes, sub_edges = build_nodes_edges(val, full_path, full_path)
                        nodes.extend(sub_nodes)
                        edges.extend(sub_edges)

                return nodes, edges

            nodes, edges = build_nodes_edges(tree)
            direction = "UD" if st.session_state.layout_direction == "vertical" else "LR"
            
            config = Config(
                width=800, 
                height=500, 
                directed=True, 
                physics=False, 
                hierarchical=True, 
                hierarchical_sort_method="directed", 
                hierarchical_direction=direction
            )
            
            # agraphを表示（クリック機能は無効化）
            st.info("⚠️ グラフィカル表示ではクリック機能が無効です。上のツリー表示で業務をクリックしてください。")
            agraph(nodes=nodes, edges=edges, config=config)
            
        except Exception as e:
            st.warning(f"グラフィカル表示でエラーが発生しました: {str(e)}")
            st.info("ツリー表示をご利用ください。")
            
    else:
        st.info("まず部署を追加してください。")
        help_text = """### 使い方
1. 左のサイドバーから「部署の追加」で組織構造を作成
2. 「業務の追加」で各部署に業務を追加
3. ツリー表示の業務（📝ボタン）をクリックして詳細編集"""
        st.markdown(help_text)