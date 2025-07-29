import streamlit as st
import urllib.parse
import json
from datetime import datetime
import uuid

st.set_page_config(page_title="OpsMap Enhanced", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング + セッション永続化")

# セッション状態の初期化
if "tree_data" not in st.session_state:
    st.session_state.tree_data = {}

if "layout_direction" not in st.session_state:
    st.session_state.layout_direction = "vertical"

if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

if "free_pages" not in st.session_state:
    st.session_state.free_pages = {}

if "canvas_data" not in st.session_state:
    st.session_state.canvas_data = {}

if "node_links" not in st.session_state:
    st.session_state.node_links = {}

if "generated_urls" not in st.session_state:
    st.session_state.generated_urls = {}

if "task_details" not in st.session_state:
    st.session_state.task_details = {}

tree = st.session_state.tree_data

# URLパラメータの処理
query_params = st.experimental_get_query_params()
if "task" in query_params:
    task_id = query_params["task"][0]
    st.session_state.current_page = f"task_detail_{task_id}"

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

def generate_task_url(node_path):
    """業務詳細ページの固有URLを生成する"""
    # 一意のIDを生成
    task_id = str(uuid.uuid4())[:8]
    # 現在のStreamlitアプリのベースURLを想定
    base_url = "http://localhost:8501"  # 実際の環境に合わせて変更
    generated_url = f"{base_url}/?task={task_id}"
    
    # 業務詳細データを作成・保存
    task_data = {
        "task_id": task_id,
        "node_path": node_path,
        "department_path": "/".join(node_path.split("/")[:-1]),  # 最後の要素（業務名）を除く
        "task_name": node_path.split("/")[-1],  # 最後の要素が業務名
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": generated_url,
        "業務": "",
        "頻度": "毎週",
        "重要度": 3,
        "工数": 0.0,
        "時間目安": 0.0,
        "メモ": "",
        "関連リンク": []
    }
    
    # 既存のノードデータがあれば引き継ぎ
    node = get_node_by_path(node_path.split("/"), tree)
    if isinstance(node, dict) and "業務" in node:
        task_data.update({
            "業務": node.get("業務", ""),
            "頻度": node.get("頻度", "毎週"),
            "重要度": node.get("重要度", 3),
            "工数": node.get("工数", 0.0),
            "時間目安": node.get("時間目安", 0.0)
        })
    
    # セッション状態に保存
    st.session_state.task_details[task_id] = task_data
    
    # 生成されたURLを保存
    st.session_state.generated_urls[node_path] = {
        "url": generated_url,
        "task_id": task_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return generated_url, task_id

def get_all_task_files():
    """全ての業務詳細を部署別に取得"""
    task_files = {}
    
    for task_id, task_data in st.session_state.task_details.items():
        dept_path = task_data.get("department_path", "")
        if dept_path:
            # スラッシュをアンダースコアに変換してフォルダ名として使用
            folder_name = dept_path.replace("/", "_")
        else:
            folder_name = "未分類"
        
        if folder_name not in task_files:
            task_files[folder_name] = []
        task_files[folder_name].append(task_id)
    
    return task_files

# 業務詳細ページの表示
def show_task_detail_page(task_id):
    """固有URLを持つ業務詳細ページを表示"""
    task_data = st.session_state.task_details.get(task_id)
    
    if not task_data:
        st.error(f"タスクID {task_id} のデータが見つかりません。")
        if st.button("🏠 メインページに戻る"):
            st.session_state.current_page = "main"
            st.experimental_set_query_params()
            st.rerun()
        return
    
    st.subheader(f"📝 業務詳細ページ：「{task_data['task_name']}」")
    st.markdown(f"**部署:** {task_data['department_path']}")
    st.markdown(f"**作成日:** {task_data['created_at']} | **更新日:** {task_data['updated_at']}")
    
    # データ保存状況の表示
    st.info("💾 データはセッション内で保持されます（ブラウザを閉じるまで有効）")
    
    # URL情報の表示
    with st.expander("🔗 このページのURL情報", expanded=False):
        st.code(task_data['url'], language=None)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 URLをコピー", key="copy_task_url"):
                st.success("URLがクリップボードにコピーされました！")
                st.components.v1.html(f"""
                <script>
                navigator.clipboard.writeText('{task_data['url']}').then(function() {{
                    console.log('URL copied to clipboard');
                }});
                </script>
                """, height=0)
        with col2:
            if st.button("🔗 リンク管理に追加", key="add_to_links"):
                # ノードリンクに自動追加
                node_path = task_data['node_path']
                if node_path not in st.session_state.node_links:
                    st.session_state.node_links[node_path] = []
                
                st.session_state.node_links[node_path].append({
                    "title": f"{task_data['task_name']}の詳細ページ",
                    "url": task_data['url'],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("ノードリンクに追加しました！")
    
    # 業務詳細フォーム
    with st.form("task_detail_form"):
        st.markdown("### 📋 業務詳細")
        
        new_task = st.text_area("業務内容", value=task_data.get("業務", ""), height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            new_freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"], 
                                  index=["毎日", "毎週", "毎月", "その他"].index(task_data.get("頻度", "毎週")))
            new_imp = st.slider("重要度 (1〜5)", 1, 5, value=task_data.get("重要度", 3))
        
        with col2:
            new_effort = st.number_input("工数 (時間/週)", min_value=0.0, 
                                       value=task_data.get("工数", 0.0), step=0.5)
            new_estimate = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, 
                                         value=task_data.get("時間目安", 0.0), step=5.0)
        
        new_memo = st.text_area("メモ・備考", value=task_data.get("メモ", ""), height=100)
        
        submitted = st.form_submit_button("💾 保存")
        
        if submitted:
            # データを更新
            task_data.update({
                "業務": new_task,
                "頻度": new_freq,
                "重要度": new_imp,
                "工数": new_effort,
                "時間目安": new_estimate,
                "メモ": new_memo,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 元のノードデータも更新
            node = get_node_by_path(task_data['node_path'].split("/"), tree)
            if isinstance(node, dict):
                node.update({
                    "業務": new_task,
                    "頻度": new_freq,
                    "重要度": new_imp,
                    "工数": new_effort,
                    "時間目安": new_estimate
                })
            
            # セッション状態を更新
            st.session_state.task_details[task_id] = task_data
            
            st.success("✅ 保存しました。")
            st.rerun()
    
    # 関連リンク管理
    st.markdown("### 🔗 関連リンク")
    
    # 新しいリンクの追加
    with st.expander("➕ 関連リンクを追加"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            link_title = st.text_input("リンクタイトル:", key="task_link_title")
        with col2:
            link_url = st.text_input("URL:", key="task_link_url", placeholder="https://example.com")
        with col3:
            if st.button("➕ 追加", key="add_task_link"):
                if link_title and link_url:
                    if "関連リンク" not in task_data:
                        task_data["関連リンク"] = []
                    
                    task_data["関連リンク"].append({
                        "title": link_title,
                        "url": link_url,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.session_state.task_details[task_id] = task_data
                    st.success(f"リンク「{link_title}」を追加しました！")
                    st.rerun()
    
    # 既存リンクの表示
    if task_data.get("関連リンク"):
        for i, link in enumerate(task_data["関連リンク"]):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.write(f"**{link['title']}**")
            with col2:
                st.markdown(f"[{link['url']}]({link['url']})")
            with col3:
                if st.button("🗑️", key=f"delete_task_link_{i}"):
                    task_data["関連リンク"].pop(i)
                    st.session_state.task_details[task_id] = task_data
                    st.rerun()
    
    # ナビゲーションボタン
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 メインページに戻る", key="back_to_main"):
            st.session_state.current_page = "main"
            st.experimental_set_query_params()
            st.rerun()
    with col2:
        if st.button("📋 全業務一覧", key="view_all_tasks"):
            st.session_state.current_page = "task_list"
            st.rerun()
    with col3:
        if st.button("🔗 リンク管理", key="goto_link_management"):
            st.session_state.current_page = "link_management"
            st.rerun()

# 全業務一覧ページ
def show_task_list_page():
    """部署別に整理された全業務一覧を表示"""
    st.subheader("📋 全業務一覧（部署別）")
    
    task_files = get_all_task_files()
    
    if not task_files:
        st.info("まだ業務詳細ページが作成されていません。")
        return
    
    for dept_folder, task_ids in task_files.items():
        # 部署名を表示（アンダースコアをスラッシュに戻す）
        dept_name = dept_folder.replace("_", "/") if dept_folder != "未分類" else "未分類"
        
        with st.expander(f"📁 {dept_name} ({len(task_ids)}件)", expanded=True):
            for task_id in task_ids:
                task_data = st.session_state.task_details.get(task_id)
                if task_data:
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{task_data['task_name']}**")
                    with col2:
                        st.write(f"更新: {task_data['updated_at']}")
                    with col3:
                        if st.button("👁️ 表示", key=f"view_task_{task_id}"):
                            st.session_state.current_page = f"task_detail_{task_id}"
                            st.experimental_set_query_params(task=task_id)
                            st.rerun()
                    with col4:
                        if st.button("🔗 URL", key=f"copy_task_url_{task_id}"):
                            st.code(task_data['url'], language=None)

# ページナビゲーション
def show_page_navigation():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 ページナビゲーション")
    
    if st.sidebar.button("🏠 メインページ（組織マップ）"):
        st.session_state.current_page = "main"
        st.session_state.selected_node = None
        st.experimental_set_query_params()
        st.rerun()
    
    if st.sidebar.button("📋 全業務一覧"):
        st.session_state.current_page = "task_list"
        st.rerun()
    
    if st.sidebar.button("🔗 ノードリンク管理"):
        st.session_state.current_page = "link_management"
        st.rerun()

# ノードリンク管理機能（簡略版）
def show_link_management():
    st.subheader("🔗 ノードリンク管理")
    
    # 既存ノード一覧の取得
    all_nodes = []
    
    def collect_all_nodes(tree, path=""):
        for key, val in tree.items():
            current_path = f"{path}/{key}" if path else key
            all_nodes.append(current_path)
            if isinstance(val, dict) and not ("業務" in val):
                collect_all_nodes(val, current_path)
    
    if tree:
        collect_all_nodes(tree)
    
    if not all_nodes:
        st.info("まず組織マップで部署や業務を作成してください。")
        return
    
    # 全ノードのリンク一覧
    if st.session_state.node_links:
        st.subheader("📋 全ノードのリンク一覧")
        
        for node_path, links in st.session_state.node_links.items():
            with st.expander(f"🔗 {node_path} ({len(links)}個のリンク)"):
                for link in links:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(f"**{link['title']}**")
                    with col2:
                        st.markdown(f"[{link['url']}]({link['url']}) *(追加日: {link['created_at']})*")

# メインの組織マップ機能
def show_main_page():
    selected_node = st.session_state.get("selected_node")

    if selected_node:
        clicked = selected_node
        node = get_node_by_path(clicked.split("/"), tree)

        if isinstance(node, dict) and "業務" in node:
            st.subheader(f"📝 業務：「{clicked}」")

            # URL発行機能
            st.markdown("### 🔗 業務詳細ページの作成")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if clicked in st.session_state.generated_urls:
                    generated_data = st.session_state.generated_urls[clicked]
                    st.info(f"✅ 業務詳細ページが作成済みです")
                    st.code(generated_data["url"], language=None)
                else:
                    st.info("この業務の詳細ページを作成してください")
            
            with col2:
                if st.button("📄 詳細ページ作成"):
                    generated_url, task_id = generate_task_url(clicked)
                    st.success("業務詳細ページを作成しました！")
                    st.session_state.current_page = f"task_detail_{task_id}"
                    st.experimental_set_query_params(task=task_id)
                    st.rerun()
            
            # 既存の詳細ページがある場合のアクセスボタン
            if clicked in st.session_state.generated_urls:
                task_id = st.session_state.generated_urls[clicked]["task_id"]
                if st.button("👁️ 詳細ページを表示"):
                    st.session_state.current_page = f"task_detail_{task_id}"
                    st.experimental_set_query_params(task=task_id)
                    st.rerun()

            # 簡易編集フォーム
            st.markdown("### ⚡ 簡易編集")
            task = node.get("業務", "")
            freq = node.get("頻度", "毎週")
            imp = node.get("重要度", 3)

            with st.form("quick_edit_form"):
                new_task = st.text_area("業務内容", value=task, height=100)
                new_freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"], 
                                      index=["毎日", "毎週", "毎月", "その他"].index(freq))
                new_imp = st.slider("重要度 (1〜5)", 1, 5, value=imp)
                
                submitted = st.form_submit_button("💾 簡易保存")
                if submitted:
                    node["業務"] = new_task
                    node["頻度"] = new_freq
                    node["重要度"] = new_imp
                    st.success("✅ 保存しました。")

            # ボタン配置
            st.markdown("---")
            if st.button("🔙 トップに戻る", key="back_to_top_main"):
                st.session_state.selected_node = None
                st.rerun()

    else:
        # サイドバーの設定（組織マップ用）
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

        st.subheader("🧠 組織マップ")

        # ツリー表示（クリック機能付き）
        def display_tree_interactive(tree, level=0, path=""):
            for key, val in tree.items():
                current_path = f"{path}/{key}" if path else key
                indent = "　" * level
                
                # リンク情報の表示
                has_links = current_path in st.session_state.node_links
                has_generated_url = current_path in st.session_state.generated_urls
                link_count = len(st.session_state.node_links.get(current_path, []))
                
                link_info = ""
                if has_links:
                    link_info += f" 🔗({link_count})"
                if has_generated_url:
                    link_info += " 📄"
                
                if isinstance(val, dict) and "業務" in val:
                    # 業務ノード - クリック可能なボタン
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button(f"📝 {key}{link_info}", key=f"task_{current_path.replace("/", "_")}", help="クリックして編集"):
                            st.session_state.selected_node = current_path
                            st.rerun()
                    with col2:
                        task_content = val.get("業務", "未設定")
                        freq = val.get("頻度", "毎週")
                        imp = val.get("重要度", 3)
                        st.write(f"{indent}業務内容: {task_content[:50]}{"""...""" if len(task_content) > 50 else ""}")
                        st.write(f"{indent}頻度: {freq}, 重要度: {imp}")
                        
                        # 詳細ページへのリンク
                        if has_generated_url:
                            task_id = st.session_state.generated_urls[current_path]["task_id"]
                            if st.button(f"👁️ 詳細ページ", key=f"view_detail_{current_path.replace("/", "_")}"):
                                st.session_state.current_page = f"task_detail_{task_id}"
                                st.experimental_set_query_params(task=task_id)
                                st.rerun()
                else:
                    # 部署ノード
                    st.write(f"{indent}📁 **{key}**{link_info}")
                    if isinstance(val, dict):
                        display_tree_interactive(val, level + 1, current_path)

        if tree:
            display_tree_interactive(tree)
        else:
            st.info("まず部署を追加してください。")
            help_text = """### 使い方
1. 左のサイドバーから「部署の追加」で組織構造を作成
2. 「業務の追加」で各部署に業務を追加
3. 業務をクリックして「📄 詳細ページ作成」で固有URLの詳細ページを作成
4. 詳細ページではセッション内でデータの編集・保存が可能
5. 「📋 全業務一覧」で部署別に整理された業務一覧を確認

**注意**: データはセッション内でのみ保持されます（ブラウザを閉じるまで有効）"""
            st.markdown(help_text)

# メイン処理
show_page_navigation()

# 現在のページに応じて表示を切り替え
current_page = st.session_state.current_page

if current_page == "main":
    show_main_page()
elif current_page == "task_list":
    show_task_list_page()
elif current_page == "link_management":
    show_link_management()
elif current_page.startswith("task_detail_"):
    task_id = current_page.replace("task_detail_", "")
    show_task_detail_page(task_id)
else:
    show_main_page()

