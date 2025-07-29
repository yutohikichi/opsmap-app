import streamlit as st
import json
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="BackOps Guide",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .node-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .flow-container {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# サイドバー
st.sidebar.title("🏢 BackOps Guide")
st.sidebar.markdown("---")

# ナビゲーション
page = st.sidebar.selectbox(
    "ページを選択",
    ["ホーム", "OpsMap", "FlowBuilder", "業務辞書", "スキルマップ", "設定"]
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
        st.success("• 経理業務: ★★★☆☆\n• 人事業務: ★★☆☆☆\n• 情シス業務: ★☆☆☆☆")
    
    with col3:
        st.markdown('<div class="section-header">🔔 通知</div>', unsafe_allow_html=True)
        st.warning("• 属人化業務が3件検出されました\n• 新しい業務テンプレートが追加されました")

elif page == "OpsMap":
    st.markdown('<h1 class="main-header">🗺️ OpsMap（組織構造）</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">部門別業務マップ</div>', unsafe_allow_html=True)
    
    # 組織構造の表示（簡易版）
    org_data = {
        "部門": ["管理部", "管理部", "管理部", "営業部", "営業部", "情報システム部"],
        "業務": ["経理業務", "人事業務", "総務業務", "営業活動", "顧客対応", "システム管理"],
        "担当者": ["田中", "佐藤", "鈴木", "山田", "高橋", "伊藤"],
        "重要度": ["★★★", "★★☆", "★★☆", "★★★", "★★☆", "★★★"]
    }
    
    df = pd.DataFrame(org_data)
    st.dataframe(df, use_container_width=True)
    
    st.info("💡 各業務をクリックすると、FlowBuilderで詳細なプロセスを確認できます。")

elif page == "FlowBuilder":
    st.markdown('<h1 class="main-header">🔄 FlowBuilder</h1>', unsafe_allow_html=True)
    
    # JSONファイルの読み込み
    try:
        with open('invoice_flow.json', 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
    except FileNotFoundError:
        st.error("フローデータが見つかりません。")
        flow_data = None
    
    if flow_data:
        st.markdown(f'<div class="section-header">{flow_data["flow_name"]}</div>', unsafe_allow_html=True)
        st.write(f"**説明**: {flow_data['description']}")
        
        # フロー表示エリア
        st.markdown('<div class="flow-container">', unsafe_allow_html=True)
        
        # ノード一覧表示
        st.subheader("📋 業務ステップ一覧")
        
        for i, node in enumerate(flow_data['nodes']):
            if node['type'] != 'start' and node['type'] != 'end':
                with st.expander(f"ステップ {i}: {node['label']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**説明**: {node.get('description', 'なし')}")
                        st.write(f"**担当者**: {node.get('assigned_to', 'なし')}")
                    with col2:
                        st.write(f"**予想時間**: {node.get('estimated_time', 'なし')}分")
                        st.write(f"**タイプ**: {node['type']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 接続関係の表示
        st.subheader("🔗 フロー接続")
        connections_df = pd.DataFrame(flow_data['connections'])
        st.dataframe(connections_df, use_container_width=True)
        
        # JSON表示
        with st.expander("📄 JSON構造を表示", expanded=False):
            st.json(flow_data)
        
        # JSON保存機能
        st.subheader("💾 データ保存")
        if st.button("JSONをダウンロード"):
            st.download_button(
                label="📥 JSONファイルをダウンロード",
                data=json.dumps(flow_data, ensure_ascii=False, indent=2),
                file_name=f"{flow_data['flow_name']}.json",
                mime="application/json"
            )

elif page == "業務辞書":
    st.markdown('<h1 class="main-header">📚 業務辞書</h1>', unsafe_allow_html=True)
    
    # 業務検索
    search_term = st.text_input("🔍 業務を検索", placeholder="例: 請求書、経理、人事")
    
    # サンプル業務データ
    tasks = [
        {
            "業務名": "請求書発行",
            "部門": "経理",
            "説明": "顧客への請求書を作成し送付する業務",
            "工数": "30分",
            "頻度": "月1回",
            "重要度": "★★★"
        },
        {
            "業務名": "入社手続き",
            "部門": "人事",
            "説明": "新入社員の各種手続きを行う業務",
            "工数": "2時間",
            "頻度": "随時",
            "重要度": "★★★"
        },
        {
            "業務名": "PCセットアップ",
            "部門": "情報システム",
            "説明": "新入社員用PCの初期設定を行う業務",
            "工数": "1時間",
            "頻度": "随時",
            "重要度": "★★☆"
        }
    ]
    
    # 業務一覧表示
    for task in tasks:
        if not search_term or search_term.lower() in task["業務名"].lower():
            with st.expander(f"📋 {task['業務名']} ({task['部門']})", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**説明**: {task['説明']}")
                    st.write(f"**工数**: {task['工数']}")
                with col2:
                    st.write(f"**頻度**: {task['頻度']}")
                    st.write(f"**重要度**: {task['重要度']}")

elif page == "スキルマップ":
    st.markdown('<h1 class="main-header">🎯 スキルマップ</h1>', unsafe_allow_html=True)
    
    # スキル評価データ
    skills_data = {
        "スキル分野": ["経理業務", "人事業務", "総務業務", "営業業務", "情報システム"],
        "現在レベル": [3, 2, 1, 1, 1],
        "目標レベル": [4, 3, 2, 2, 3],
        "経験業務数": [5, 2, 1, 0, 1]
    }
    
    df_skills = pd.DataFrame(skills_data)
    
    # スキルチャート
    st.subheader("📊 スキルレベル")
    st.bar_chart(df_skills.set_index("スキル分野")[["現在レベル", "目標レベル"]])
    
    # 詳細テーブル
    st.subheader("📋 詳細データ")
    st.dataframe(df_skills, use_container_width=True)
    
    # 成長提案
    st.subheader("💡 成長提案")
    st.info("• 人事業務のスキルアップのため、入社手続きフローを学習することをお勧めします\n• 情報システム分野の経験を積むため、PCセットアップ業務に参加してみましょう")

elif page == "設定":
    st.markdown('<h1 class="main-header">⚙️ 設定</h1>', unsafe_allow_html=True)
    
    st.subheader("🎨 表示設定")
    theme = st.selectbox("テーマ", ["ライト", "ダーク"])
    language = st.selectbox("言語", ["日本語", "English"])
    
    st.subheader("💾 データ設定")
    auto_save = st.checkbox("自動保存を有効にする", value=True)
    backup_frequency = st.selectbox("バックアップ頻度", ["毎日", "毎週", "毎月"])
    
    st.subheader("🔔 通知設定")
    email_notifications = st.checkbox("メール通知", value=True)
    task_reminders = st.checkbox("タスクリマインダー", value=True)
    
    if st.button("設定を保存"):
        st.success("設定が保存されました！")

# フッター
st.sidebar.markdown("---")
st.sidebar.markdown("**BackOps Guide v1.0**")
st.sidebar.markdown("© 2025 Manus Team")

