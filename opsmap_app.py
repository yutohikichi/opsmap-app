import streamlit as st
import urllib.parse
import json
from datetime import datetime

st.set_page_config(page_title="OpsMap Enhanced", layout="wide")
st.title("OpsMap™：組織構造 × 業務マッピング + リンク機能")

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

if "node_links" not in st.session_state:
    st.session_state.node_links = {}

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
    
    if st.sidebar.button("🔗 ノードリンク管理"):
        st.session_state.current_page = "link_management"
        st.rerun()
    
    if st.sidebar.button("🎨 自由描画メモ"):
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

# ノードリンク管理機能
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
    
    # リンク追加・編集
    with st.expander("➕ ノードにリンクを追加/編集", expanded=True):
        selected_node = st.selectbox("ノードを選択:", all_nodes)
        
        # 既存リンク情報の取得
        existing_links = st.session_state.node_links.get(selected_node, [])
        
        st.markdown(f"**選択ノード:** `{selected_node}`")
        
        # 新しいリンクの追加
        st.markdown("**🔗 新しいリンクを追加**")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            link_title = st.text_input("リンクタイトル:", key="new_link_title")
        with col2:
            link_url = st.text_input("URL:", key="new_link_url", 
                                   placeholder="https://example.com")
        with col3:
            if st.button("➕ 追加"):
                if link_title and link_url:
                    if selected_node not in st.session_state.node_links:
                        st.session_state.node_links[selected_node] = []
                    
                    st.session_state.node_links[selected_node].append({
                        "title": link_title,
                        "url": link_url,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(f"リンク「{link_title}」を追加しました！")
                    st.rerun()
                else:
                    st.warning("リンクタイトルとURLを入力してください。")
        
        # 既存リンクの表示・管理
        if existing_links:
            st.markdown("**📋 既存のリンク**")
            for i, link in enumerate(existing_links):
                col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
                
                with col1:
                    st.write(f"**{link['title']}**")
                with col2:
                    st.write(f"[{link['url']}]({link['url']})")
                with col3:
                    if st.button("🌐 開く", key=f"open_{selected_node}_{i}"):
                        st.markdown(f"[🔗 {link['title']}を新しいタブで開く]({link['url']})")
                with col4:
                    if st.button("🗑️", key=f"delete_{selected_node}_{i}"):
                        st.session_state.node_links[selected_node].pop(i)
                        if not st.session_state.node_links[selected_node]:
                            del st.session_state.node_links[selected_node]
                        st.rerun()
    
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

# 自由描画メモツール（ライブラリ不要版）
def show_drawing_tool():
    st.subheader("🎨 自由描画メモツール")
    
    st.info("💡 このツールでは、描画のアイデアやスケッチの説明をテキストで記録できます。")
    
    # 描画メモ作成
    with st.expander("➕ 新しい描画メモを作成", expanded=True):
        memo_name = st.text_input("描画メモ名:", "新しい描画アイデア")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📝 描画内容・アイデア**")
            drawing_description = st.text_area(
                "描画の内容や構想を記述:", 
                height=200,
                placeholder="例：\n- 組織図の改善案\n- プロセスフローの設計\n- UI/UXのワイヤーフレーム\n- システム構成図のアイデア"
            )
        
        with col2:
            st.markdown("**🎯 目的・用途**")
            purpose = st.text_area(
                "この描画の目的や用途:",
                height=100,
                placeholder="例：会議での説明用、提案書への添付、チーム共有など"
            )
            
            st.markdown("**🏷️ タグ・カテゴリ**")
            tags = st.text_input(
                "タグ（カンマ区切り）:",
                placeholder="例：組織図,プロセス,UI設計"
            )
        
        if st.button("💾 描画メモを保存"):
            if memo_name and drawing_description:
                st.session_state.canvas_data[memo_name] = {
                    "description": drawing_description,
                    "purpose": purpose,
                    "tags": tags,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "memo"
                }
                st.success(f"描画メモ「{memo_name}」を保存しました！")
                st.rerun()
            else:
                st.warning("メモ名と描画内容を入力してください。")
    
    # 保存済み描画メモ一覧
    if st.session_state.canvas_data:
        st.subheader("💾 保存済み描画メモ")
        
        for name, data in st.session_state.canvas_data.items():
            with st.expander(f"📊 {name} ({data['created_at']})"):
                st.markdown(f"**描画内容:**")
                st.write(data["description"])
                
                if data.get("purpose"):
                    st.markdown(f"**目的:** {data['purpose']}")
                
                if data.get("tags"):
                    st.markdown(f"**タグ:** {data['tags']}")
                
                if st.button(f"🗑️ 削除", key=f"del_memo_{name}"):
                    del st.session_state.canvas_data[name]
                    st.rerun()

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

# メインの組織マップ機能（リンク機能付き）
def show_main_page():
    selected_node = st.session_state.get("selected_node")

    if selected_node:
        clicked = selected_node
        node = get_node_by_path(clicked.split("/"), tree)

        if isinstance(node, dict) and "業務" in node:
            st.subheader(f"📝 業務詳細ページ：「{clicked}」")

            # ノードのリンク表示
            node_links = st.session_state.node_links.get(clicked, [])
            if node_links:
                st.markdown("**🔗 関連リンク:**")
                cols = st.columns(min(len(node_links), 3))
                for i, link in enumerate(node_links):
                    with cols[i % 3]:
                        st.markdown(f"[🌐 {link['title']}]({link['url']})")

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
    
(Content truncated due to size limit. Use line ranges to read in chunks)