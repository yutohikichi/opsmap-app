import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# ページ設定
st.set_page_config(
    page_title="BackOps Guide",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データファイルのパス
TASKS_FILE = "tasks_data.json"
FLOWS_FILE = "flows_data.json"
SKILLS_FILE = "skills_data.json"
ORG_FILE = "org_data.json"

# セッション状態の初期化
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = False

# データ保存・読み込み関数
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# データ初期化関数（一度だけ実行）
@st.cache_data
def init_data_once():
    # 業務データの初期化
    if not os.path.exists(TASKS_FILE):
        initial_tasks = [
            {
                "id": "task_001",
                "業務名": "請求書発行",
                "部門": "経理",
                "説明": "顧客への請求書を作成し送付する業務",
                "工数": "30分",
                "頻度": "月1回",
                "重要度": "★★★",
                "担当者": "田中"
            },
            {
                "id": "task_002",
                "業務名": "入社手続き",
                "部門": "人事",
                "説明": "新入社員の各種手続きを行う業務",
                "工数": "2時間",
                "頻度": "随時",
                "重要度": "★★★",
                "担当者": "佐藤"
            }
        ]
        save_data(TASKS_FILE, initial_tasks)
    
    # スキルデータの初期化
    if not os.path.exists(SKILLS_FILE):
        initial_skills = [
            {"id": "skill_001", "スキル分野": "経理業務", "現在レベル": 3, "目標レベル": 4, "経験業務数": 5},
            {"id": "skill_002", "スキル分野": "人事業務", "現在レベル": 2, "目標レベル": 3, "経験業務数": 2}
        ]
        save_data(SKILLS_FILE, initial_skills)
    
    # 組織データの初期化
    if not os.path.exists(ORG_FILE):
        initial_org = [
            {"id": "org_001", "部門": "管理部", "業務": "経理業務", "担当者": "田中", "重要度": "★★★"},
            {"id": "org_002", "部門": "管理部", "業務": "人事業務", "担当者": "佐藤", "重要度": "★★☆"}
        ]
        save_data(ORG_FILE, initial_org)
    
    return True

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# データ初期化
init_data_once()

# サイドバー
st.sidebar.title("🏢 BackOps Guide")
st.sidebar.markdown("---")

# ナビゲーション
page = st.sidebar.selectbox(
    "ページを選択",
    ["ホーム", "業務辞書", "スキルマップ", "設定"]
)

# メイン画面
if page == "ホーム":
    st.markdown('<h1 class="main-header">🏠 ホーム</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-header">📅 今週の業務予定</div>', unsafe_allow_html=True)
        st.info("• 請求書発行（月末）\n• 月次決算準備\n• 新入社員研修")
    
    with col2:
        st.markdown('<div class="section-header">📊 スキル進捗</div>', unsafe_allow_html=True)
        skills_data = load_data(SKILLS_FILE)
        if skills_data:
            for skill in skills_data[:3]:
                level_stars = "★" * skill["現在レベル"] + "☆" * (5 - skill["現在レベル"])
                st.success(f"• {skill['スキル分野']}: {level_stars}")
    
    with col3:
        st.markdown('<div class="section-header">🔔 通知</div>', unsafe_allow_html=True)
        st.warning("• 属人化業務が3件検出されました\n• 新しい業務テンプレートが追加されました")

elif page == "業務辞書":
    st.markdown('<h1 class="main-header">📚 業務辞書</h1>', unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 業務一覧", "✏️ 業務編集"])
    
    with tab1:
        # 業務検索
        search_term = st.text_input("🔍 業務を検索", placeholder="例: 請求書、経理、人事")
        
        tasks_data = load_data(TASKS_FILE)
        
        # 業務一覧表示
        for task in tasks_data:
            if not search_term or search_term.lower() in task["業務名"].lower():
                with st.expander(f"📋 {task['業務名']} ({task['部門']})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**説明**: {task['説明']}")
                        st.write(f"**工数**: {task['工数']}")
                        st.write(f"**担当者**: {task['担当者']}")
                    with col2:
                        st.write(f"**頻度**: {task['頻度']}")
                        st.write(f"**重要度**: {task['重要度']}")
    
    with tab2:
        st.markdown('<div class="section-header">業務の追加・編集</div>', unsafe_allow_html=True)
        
        # 新規業務追加
        with st.expander("➕ 新しい業務を追加", expanded=False):
            with st.form("add_task_form"):
                new_task_name = st.text_input("業務名")
                new_dept = st.text_input("部門")
                new_desc = st.text_area("説明")
                new_time = st.text_input("工数")
                new_freq = st.text_input("頻度")
                new_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"])
                new_person = st.text_input("担当者")
                
                if st.form_submit_button("追加"):
                    if new_task_name and new_dept:
                        tasks_data = load_data(TASKS_FILE)
                        new_id = f"task_{len(tasks_data) + 1:03d}"
                        new_task = {
                            "id": new_id,
                            "業務名": new_task_name,
                            "部門": new_dept,
                            "説明": new_desc,
                            "工数": new_time,
                            "頻度": new_freq,
                            "重要度": new_importance,
                            "担当者": new_person
                        }
                        tasks_data.append(new_task)
                        save_data(TASKS_FILE, tasks_data)
                        st.success("業務が追加されました！")
                        st.rerun()
        
        # 既存業務の編集
        tasks_data = load_data(TASKS_FILE)
        if tasks_data:
            st.subheader("既存業務の編集・削除")
            for i, task in enumerate(tasks_data):
                with st.expander(f"📝 {task['業務名']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        with st.form(f"edit_task_form_{i}"):
                            edit_name = st.text_input("業務名", value=task["業務名"], key=f"name_{i}")
                            edit_dept = st.text_input("部門", value=task["部門"], key=f"dept_{i}")
                            edit_desc = st.text_area("説明", value=task["説明"], key=f"desc_{i}")
                            edit_time = st.text_input("工数", value=task["工数"], key=f"time_{i}")
                            edit_freq = st.text_input("頻度", value=task["頻度"], key=f"freq_{i}")
                            edit_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"], 
                                                         index=["★☆☆", "★★☆", "★★★"].index(task["重要度"]), key=f"imp_{i}")
                            edit_person = st.text_input("担当者", value=task["担当者"], key=f"person_{i}")
                            
                            if st.form_submit_button("更新"):
                                tasks_data[i] = {
                                    "id": task["id"],
                                    "業務名": edit_name,
                                    "部門": edit_dept,
                                    "説明": edit_desc,
                                    "工数": edit_time,
                                    "頻度": edit_freq,
                                    "重要度": edit_importance,
                                    "担当者": edit_person
                                }
                                save_data(TASKS_FILE, tasks_data)
                                st.success("業務が更新されました！")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️ 削除", key=f"delete_task_{i}"):
                            tasks_data.pop(i)
                            save_data(TASKS_FILE, tasks_data)
                            st.success("業務が削除されました！")
                            st.rerun()

elif page == "スキルマップ":
    st.markdown('<h1 class="main-header">🎯 スキルマップ</h1>', unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 スキル表示", "✏️ スキル編集"])
    
    with tab1:
        skills_data = load_data(SKILLS_FILE)
        
        if skills_data:
            df_skills = pd.DataFrame(skills_data)
            
            # スキルチャート
            st.subheader("📊 スキルレベル")
            chart_data = df_skills.set_index("スキル分野")[["現在レベル", "目標レベル"]]
            st.bar_chart(chart_data)
            
            # 詳細テーブル
            st.subheader("📋 詳細データ")
            st.dataframe(df_skills.drop('id', axis=1), use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">スキルの追加・編集</div>', unsafe_allow_html=True)
        
        # 新規スキル追加
        with st.expander("➕ 新しいスキルを追加", expanded=False):
            with st.form("add_skill_form"):
                new_skill_name = st.text_input("スキル分野")
                new_current_level = st.slider("現在レベル", 1, 5, 1)
                new_target_level = st.slider("目標レベル", 1, 5, 3)
                new_experience = st.number_input("経験業務数", min_value=0, value=0)
                
                if st.form_submit_button("追加"):
                    if new_skill_name:
                        skills_data = load_data(SKILLS_FILE)
                        new_id = f"skill_{len(skills_data) + 1:03d}"
                        new_skill = {
                            "id": new_id,
                            "スキル分野": new_skill_name,
                            "現在レベル": new_current_level,
                            "目標レベル": new_target_level,
                            "経験業務数": new_experience
                        }
                        skills_data.append(new_skill)
                        save_data(SKILLS_FILE, skills_data)
                        st.success("スキルが追加されました！")
                        st.rerun()
        
        # 既存スキルの編集
        skills_data = load_data(SKILLS_FILE)
        if skills_data:
            st.subheader("既存スキルの編集・削除")
            for i, skill in enumerate(skills_data):
                with st.expander(f"📝 {skill['スキル分野']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        with st.form(f"edit_skill_form_{i}"):
                            edit_name = st.text_input("スキル分野", value=skill["スキル分野"], key=f"skill_name_{i}")
                            edit_current = st.slider("現在レベル", 1, 5, skill["現在レベル"], key=f"current_{i}")
                            edit_target = st.slider("目標レベル", 1, 5, skill["目標レベル"], key=f"target_{i}")
                            edit_exp = st.number_input("経験業務数", min_value=0, value=skill["経験業務数"], key=f"exp_{i}")
                            
                            if st.form_submit_button("更新"):
                                skills_data[i] = {
                                    "id": skill["id"],
                                    "スキル分野": edit_name,
                                    "現在レベル": edit_current,
                                    "目標レベル": edit_target,
                                    "経験業務数": edit_exp
                                }
                                save_data(SKILLS_FILE, skills_data)
                                st.success("スキルが更新されました！")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️ 削除", key=f"delete_skill_{i}"):
                            skills_data.pop(i)
                            save_data(SKILLS_FILE, skills_data)
                            st.success("スキルが削除されました！")
                            st.rerun()

elif page == "設定":
    st.markdown('<h1 class="main-header">⚙️ 設定</h1>', unsafe_allow_html=True)
    
    st.subheader("🎨 表示設定")
    theme = st.selectbox("テーマ", ["ライト", "ダーク"])
    language = st.selectbox("言語", ["日本語", "English"])
    
    st.subheader("💾 データ設定")
    auto_save = st.checkbox("自動保存を有効にする", value=True)
    backup_frequency = st.selectbox("バックアップ頻度", ["毎日", "毎週", "毎月"])
    
    if st.button("設定を保存"):
        st.success("設定が保存されました！")

# フッター
st.sidebar.markdown("---")
st.sidebar.markdown("**BackOps Guide v2.0**")
st.sidebar.markdown("© 2025 Manus Team")
st.sidebar.markdown("✨ 入力・編集機能付き")

