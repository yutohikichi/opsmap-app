import streamlit as st
import urllib.parse
import json
from datetime import datetime

st.set_page_config(page_title="OpsMap Enhanced", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング + 自由描画・ページ作成")

# 初期データ
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

# ページナビゲーション
def show_page_navigation():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 ページナビゲーション")
    
    if st.sidebar.button("🏠 メインページ（組織マップ）"):
        st.session_state.current_page = "main"
        st.session_state.selected_node = None
        st.rerun()
    
    if st.sidebar.button("🎨 自由描画ツール"):
        st.session_state.current_page = "drawing"
        st.rerun()
    
    if st.sidebar.button("📝 自由ページ作成"):
        st.session_state.current_page = "free_page"
        st.rerun()
    
    # 既存の自由ページ一覧
    if st.session_state.free_pages:
        st.sidebar.markdown("**作成済み自由ページ:**")
        for page_id, page_data in st.session_state.free_pages.items():
            if st.sidebar.button(f"📄 {page_data['title']}", key=f"goto_{page_id}"):
                st.session_state.current_page = f"view_page_{page_id}"
                st.rerun()

# 自由描画ツールページ
def show_drawing_tool():
    st.subheader("🎨 自由描画ツール")
    
    try:
        from streamlit_drawable_canvas import st_canvas
        
        # 描画設定
        col1, col2 = st.columns([1, 3])
        
        with col1:
            drawing_mode = st.selectbox(
                "描画ツール:", 
                ("freedraw", "line", "rect", "circle", "transform", "polygon"),
                help="描画モードを選択してください"
            )
            
            stroke_width = st.slider("線の太さ:", 1, 25, 3)
            stroke_color = st.color_picker("線の色:", "#000000")
            fill_color = st.color_picker("塗りつぶし色:", "#FF0000")
            bg_color = st.color_picker("背景色:", "#FFFFFF")
            
            canvas_name = st.text_input("キャンバス名:", "新しい描画")
        
        with col2:
            # キャンバス
            canvas_result = st_canvas(
                fill_color=f"rgba({int(fill_color[1:3], 16)}, {int(fill_color[3:5], 16)}, {int(fill_color[5:7], 16)}, 0.3)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color=bg_color,
                height=400,
                width=600,
                drawing_mode=drawing_mode,
                key="drawing_canvas",
            )
        
        # 保存ボタンを描画設定の下に移動
        with col1:
            if st.button("💾 描画を保存"):
                if canvas_name and canvas_result and canvas_result.json_data:
                    st.session_state.canvas_data[canvas_name] = {
                        "json_data": canvas_result.json_data,
                        "image_data": canvas_result.image_data,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success(f"描画「{canvas_name}」を保存しました！")
                elif not canvas_result or not canvas_result.json_data:
                    st.warning("描画内容がありません。何か描いてから保存してください。")
                else:
                    st.warning("キャンバス名を入力してください。")
        
        # 保存済み描画一覧
        if st.session_state.canvas_data:
            st.subheader("💾 保存済み描画")
            for name, data in st.session_state.canvas_data.items():
                with st.expander(f"📊 {name} ({data['created_at']})"):
                    if data.get("image_data") is not None:
                        st.image(data["image_data"], caption=name)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🗑️ 削除", key=f"del_{name}"):
                            del st.session_state.canvas_data[name]
                            st.rerun()
                    with col2:
                        if st.button(f"📋 復元", key=f"restore_{name}"):
                            st.info("キャンバスに復元するには、上のキャンバスをリセットしてから実装予定です")
    
    except ImportError:
        st.error("streamlit-drawable-canvasがインストールされていません。")
        st.code("pip install streamlit-drawable-canvas")
        st.info("代替として、テキストベースの描画メモ機能を提供します。")
        
        # 代替機能
        st.subheader("📝 描画メモ")
        drawing_memo = st.text_area("描画のアイデアやメモを記録:", height=200)
        memo_name = st.text_input("メモ名:", "新しいメモ")
        
        if st.button("💾 メモを保存"):
            if memo_name and drawing_memo:
                st.session_state.canvas_data[memo_name] = {
                    "memo": drawing_memo,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success(f"メモ「{memo_name}」を保存しました！")

# 自由ページ作成機能
def show_free_page_creator():
    st.subheader("📝 自由ページ作成")
    
    # 新規ページ作成
    with st.expander("➕ 新しいページを作成", expanded=True):
        page_title = st.text_input("ページタイトル:")
        page_content = st.text_area("ページ内容:", height=200, 
                                   help="Markdown記法が使用できます")
        
        # URL追加機能
        st.markdown("**🔗 URLリンクの追加**")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            link_title = st.text_input("リンクタイトル:", key="link_title")
        with col2:
            link_url = st.text_input("URL:", key="link_url", 
                                   placeholder="https://example.com")
        with col3:
            if st.button("➕ リンク追加"):
                if link_title and link_url:
                    link_markdown = f"[{link_title}]({link_url})"
                    # セッション状態を使ってページ内容を更新
                    if "temp_page_content" not in st.session_state:
                        st.session_state.temp_page_content = page_content
                    st.session_state.temp_page_content += f"\n\n{link_markdown}"
                    st.success(f"リンク「{link_title}」を追加しました！")
                    st.rerun()
        
        # 一時的なページ内容を表示
        if "temp_page_content" in st.session_state:
            st.text_area("プレビュー:", value=st.session_state.temp_page_content, height=100, disabled=True)
            final_content = st.session_state.temp_page_content
        else:
            final_content = page_content
        
        # ページ保存
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 ページを保存"):
                if page_title and final_content:
                    page_id = f"page_{len(st.session_state.free_pages) + 1}"
                    st.session_state.free_pages[page_id] = {
                        "title": page_title,
                        "content": final_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success(f"ページ「{page_title}」を保存しました！")
                    # 一時的なコンテンツをクリア
                    if "temp_page_content" in st.session_state:
                        del st.session_state.temp_page_content
                    st.session_state.current_page = f"view_page_{page_id}"
                    st.rerun()
                else:
                    st.warning("ページタイトルと内容を入力してください。")
        
        with col2:
            if st.button("🗑️ 内容をクリア"):
                if "temp_page_content" in st.session_state:
                    del st.session_state.temp_page_content
                st.rerun()
    
    # 既存ページ一覧
    if st.session_state.free_pages:
        st.subheader("📄 作成済みページ")
        for page_id, page_data in st.session_state.free_pages.items():
            with st.expander(f"📄 {page_data['title']} ({page_data['created_at']})"):
                st.markdown(page_data['content'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"👁️ 表示", key=f"view_{page_id}"):
                        st.session_state.current_page = f"view_page_{page_id}"
                        st.rerun()
                with col2:
                    if st.button(f"✏️ 編集", key=f"edit_{page_id}"):
                        st.session_state.current_page = f"edit_page_{page_id}"
                        st.rerun()
                with col3:
                    if st.button(f"🗑️ 削除", key=f"delete_{page_id}"):
                        del st.session_state.free_pages[page_id]
                        st.rerun()

# 自由ページ表示
def show_free_page(page_id):
    if page_id in st.session_state.free_pages:
        page_data = st.session_state.free_pages[page_id]
        
        st.subheader(f"📄 {page_data['title']}")
        st.markdown(f"*作成日: {page_data['created_at']} | 更新日: {page_data['updated_at']}*")
        
        # ページ内容表示
        st.markdown("---")
        st.markdown(page_data['content'])
        
        # 操作ボタン
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏️ 編集"):
                st.session_state.current_page = f"edit_page_{page_id}"
                st.rerun()
        with col2:
            if st.button("🔙 ページ一覧に戻る"):
                st.session_state.current_page = "free_page"
                st.rerun()
        with col3:
            if st.button("🏠 メインに戻る"):
                st.session_state.current_page = "main"
                st.rerun()

# 自由ページ編集
def show_free_page_editor(page_id):
    if page_id in st.session_state.free_pages:
        page_data = st.session_state.free_pages[page_id]
        
        st.subheader(f"✏️ ページ編集: {page_data['title']}")
        
        # 編集フォーム
        new_title = st.text_input("ページタイトル:", value=page_data['title'])
        new_content = st.text_area("ページ内容:", value=page_data['content'], height=300)
        
        # URL追加機能
        st.markdown("**🔗 URLリンクの追加**")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            link_title = st.text_input("リンクタイトル:", key=f"edit_link_title_{page_id}")
        with col2:
            link_url = st.text_input("URL:", key=f"edit_link_url_{page_id}", 
                                   placeholder="https://example.com")
        with col3:
            if st.button("➕ リンク追加", key=f"add_link_{page_id}"):
                if link_title and link_url:
                    link_markdown = f"[{link_title}]({link_url})"
                    new_content += f"\n\n{link_markdown}"
                    st.success(f"リンク「{link_title}」を追加しました！")
                    st.rerun()
        
        # 保存・キャンセルボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 変更を保存"):
                st.session_state.free_pages[page_id].update({
                    "title": new_title,
                    "content": new_content,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("変更を保存しました！")
                st.session_state.current_page = f"view_page_{page_id}"
                st.rerun()
        
        with col2:
            if st.button("❌ キャンセル"):
                st.session_state.current_page = f"view_page_{page_id}"
                st.rerun()

# メインの組織マップ機能（既存機能）
def show_main_page():
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
        else:
            st.info("まず部署を追加してください。")
            help_text = """### 使い方
1. 左のサイドバーから「部署の追加」で組織構造を作成
2. 「業務の追加」で各部署に業務を追加
3. ツリー表示の業務（📝ボタン）をクリックして詳細編集"""
            st.markdown(help_text)

# メイン処理
show_page_navigation()

# 現在のページに応じて表示を切り替え
current_page = st.session_state.current_page

if current_page == "main":
    show_main_page()
elif current_page == "drawing":
    show_drawing_tool()
elif current_page == "free_page":
    show_free_page_creator()
elif current_page.startswith("view_page_"):
    page_id = current_page.replace("view_page_", "")
    show_free_page(page_id)
elif current_page.startswith("edit_page_"):
    page_id = current_page.replace("edit_page_", "")
    show_free_page_editor(page_id)
else:
    show_main_page()

