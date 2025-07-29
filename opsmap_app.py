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

# 階層組織表示用のヘルパー関数
def render_hierarchical_organization(org_data):
    """階層構造で組織を表示"""
    # 階層構造を構築
    hierarchy = {}
    
    for org in org_data:
        group = org.get("グループ", "その他")
        dept = org.get("部門", "未分類")
        subdept = org.get("課・係", "")
        
        if group not in hierarchy:
            hierarchy[group] = {}
        
        if dept not in hierarchy[group]:
            hierarchy[group][dept] = {}
        
        if subdept:
            if subdept not in hierarchy[group][dept]:
                hierarchy[group][dept][subdept] = []
            hierarchy[group][dept][subdept].append(org)
        else:
            if "直属" not in hierarchy[group][dept]:
                hierarchy[group][dept]["直属"] = []
            hierarchy[group][dept]["直属"].append(org)
    
    # 階層表示
    for group_name, departments in hierarchy.items():
        with st.expander(f"🏢 **{group_name}**", expanded=True):
            for dept_name, subdivisions in departments.items():
                st.markdown(f"### 📋 {dept_name}")
                
                for subdiv_name, tasks in subdivisions.items():
                    if subdiv_name == "直属":
                        # 部門直属の業務
                        cols = st.columns(min(len(tasks), 3))
                        for i, task in enumerate(tasks):
                            with cols[i % 3]:
                                if st.button(
                                    f"📋 {task['業務']}\n👤 {task['担当者']}\n{task['重要度']}", 
                                    key=f"org_task_{task['id']}"
                                ):
                                    st.session_state.selected_task = task['業務']
                                    st.info(f"選択された業務: {task['業務']}")
                    else:
                        # 課・係レベルの業務
                        with st.expander(f"📁 {subdiv_name}", expanded=False):
                            cols = st.columns(min(len(tasks), 3))
                            for i, task in enumerate(tasks):
                                with cols[i % 3]:
                                    if st.button(
                                        f"📋 {task['業務']}\n👤 {task['担当者']}\n{task['重要度']}", 
                                        key=f"org_task_sub_{task['id']}"
                                    ):
                                        st.session_state.selected_task = task['業務']
                                        st.info(f"選択された業務: {task['業務']}")

# 階層フロー表示用のヘルパー関数
def render_hierarchical_flow(flow_data):
    """階層構造でフローを表示"""
    nodes = flow_data['nodes']
    connections = flow_data['connections']
    
    # ノードをIDでマッピング
    node_map = {node['node_id']: node for node in nodes}
    
    # 接続関係を解析
    connection_map = {}
    for conn in connections:
        from_id = conn['from']
        to_id = conn['to']
        condition = conn.get('condition', '')
        
        if from_id not in connection_map:
            connection_map[from_id] = []
        connection_map[from_id].append({'to': to_id, 'condition': condition})
    
    # 開始ノードを見つける
    start_nodes = [node for node in nodes if node['type'] == 'start']
    if not start_nodes:
        st.error("開始ノードが見つかりません")
        return
    
    # フロー概要を表示
    st.markdown(f"### 📋 {flow_data['flow_name']}")
    st.markdown(f"**説明**: {flow_data['description']}")
    
    # 階層表示の開始
    st.markdown("---")
    
    def render_step_hierarchy(node_id, level=0, visited=None):
        if visited is None:
            visited = set()
        
        if node_id in visited or level > 15:  # 無限ループ防止
            return
        
        visited.add(node_id)
        
        if node_id not in node_map:
            return
        
        node = node_map[node_id]
        
        # インデントレベルに応じたスタイル
        indent = "　" * level
        
        # ノードタイプに応じたアイコンとスタイル
        if node['type'] == 'start':
            icon = "🚀"
            style_class = "start-node"
        elif node['type'] == 'end':
            icon = "🏁"
            style_class = "end-node"
        elif node['type'] == 'decision':
            icon = "❓"
            style_class = "decision-node"
        else:
            icon = "📋"
            style_class = "task-node"
        
        # ノード情報を階層表示
        if node['type'] not in ['start', 'end']:
            with st.expander(f"{indent}{icon} **{node['label']}**", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**説明**: {node.get('description', 'なし')}")
                    st.write(f"**担当者**: {node.get('assigned_to', 'なし')}")
                    st.write(f"**予想時間**: {node.get('estimated_time', 'なし')}分")
                
                with col2:
                    st.write(f"**タイプ**: {node['type']}")
                    if node['type'] == 'decision':
                        st.write("**分岐条件**:")
                        if node_id in connection_map:
                            for conn in connection_map[node_id]:
                                condition = conn['condition'] if conn['condition'] else "デフォルト"
                                next_node = node_map.get(conn['to'], {})
                                next_label = next_node.get('label', 'Unknown')
                                st.write(f"• {condition} → {next_label}")
                
                # 分岐がある場合の処理
                if node_id in connection_map and len(connection_map[node_id]) > 1:
                    st.markdown("**🔀 分岐パス:**")
                    
                    # 分岐ごとにタブを作成
                    branch_tabs = []
                    branch_connections = connection_map[node_id]
                    
                    for i, conn in enumerate(branch_connections):
                        condition = conn['condition'] if conn['condition'] else f"パス{i+1}"
                        branch_tabs.append(condition)
                    
                    if len(branch_tabs) > 1:
                        tabs = st.tabs(branch_tabs)
                        
                        for i, (tab, conn) in enumerate(zip(tabs, branch_connections)):
                            with tab:
                                st.markdown(f"**条件**: {conn['condition'] if conn['condition'] else 'デフォルト'}")
                                render_step_hierarchy(conn['to'], level + 1, visited.copy())
                    else:
                        # 単一接続の場合
                        render_step_hierarchy(branch_connections[0]['to'], level + 1, visited.copy())
                else:
                    # 単一接続または接続なしの場合
                    if node_id in connection_map:
                        render_step_hierarchy(connection_map[node_id][0]['to'], level + 1, visited.copy())
        else:
            # start/endノードは簡潔に表示
            st.markdown(f"{indent}{icon} **{node['label']}**")
            if node_id in connection_map:
                render_step_hierarchy(connection_map[node_id][0]['to'], level, visited.copy())
    
    # 階層表示を開始
    start_node = start_nodes[0]
    render_step_hierarchy(start_node['node_id'])

# データ初期化関数
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
            },
            {
                "id": "task_003",
                "業務名": "PCセットアップ",
                "部門": "情報システム",
                "説明": "新入社員用PCの初期設定を行う業務",
                "工数": "1時間",
                "頻度": "随時",
                "重要度": "★★☆",
                "担当者": "伊藤"
            }
        ]
        save_data(TASKS_FILE, initial_tasks)
    
    # フローデータの初期化（階層分岐を含む例）
    if not os.path.exists(FLOWS_FILE):
        initial_flows = [
            {
                "flow_id": "flow_001",
                "flow_name": "請求書発行フロー",
                "description": "請求内容確認から請求書送付までの流れ（承認分岐あり）",
                "nodes": [
                    {
                        "node_id": "start_1",
                        "type": "start",
                        "label": "開始",
                        "position": {"x": 100, "y": 50}
                    },
                    {
                        "node_id": "step_1",
                        "type": "task",
                        "label": "請求内容確認",
                        "description": "見積書・契約書と照合し、請求金額と内容を確認する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 30,
                        "position": {"x": 300, "y": 50}
                    },
                    {
                        "node_id": "step_2",
                        "type": "task",
                        "label": "請求書作成",
                        "description": "freeeシステムを使用して請求書を作成する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 20,
                        "position": {"x": 500, "y": 50}
                    },
                    {
                        "node_id": "decision_1",
                        "type": "decision",
                        "label": "承認判定",
                        "description": "上長による請求書内容の承認判定を行う",
                        "assigned_to": "経理部長・山田",
                        "estimated_time": 10,
                        "position": {"x": 700, "y": 50}
                    },
                    {
                        "node_id": "step_3",
                        "type": "task",
                        "label": "請求書送付",
                        "description": "承認された請求書をPDFでメール送付する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 10,
                        "position": {"x": 900, "y": 50}
                    },
                    {
                        "node_id": "step_4",
                        "type": "task",
                        "label": "請求書修正",
                        "description": "指摘事項に基づいて請求書を修正する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 15,
                        "position": {"x": 700, "y": 150}
                    },
                    {
                        "node_id": "decision_2",
                        "type": "decision",
                        "label": "修正内容確認",
                        "description": "修正内容が適切かどうかを確認する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 5,
                        "position": {"x": 500, "y": 150}
                    },
                    {
                        "node_id": "step_5",
                        "type": "task",
                        "label": "送付記録",
                        "description": "送付日時と送付先を記録する",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 5,
                        "position": {"x": 1100, "y": 50}
                    },
                    {
                        "node_id": "end_1",
                        "type": "end",
                        "label": "完了",
                        "position": {"x": 1300, "y": 50}
                    }
                ],
                "connections": [
                    {"from": "start_1", "to": "step_1"},
                    {"from": "step_1", "to": "step_2"},
                    {"from": "step_2", "to": "decision_1"},
                    {"from": "decision_1", "to": "step_3", "condition": "承認"},
                    {"from": "decision_1", "to": "step_4", "condition": "差し戻し"},
                    {"from": "step_4", "to": "decision_2"},
                    {"from": "decision_2", "to": "decision_1", "condition": "再提出"},
                    {"from": "decision_2", "to": "step_2", "condition": "大幅修正"},
                    {"from": "step_3", "to": "step_5"},
                    {"from": "step_5", "to": "end_1"}
                ],
                "metadata": {
                    "created_by": "user_001",
                    "created_at": "2025-07-29T12:00:00",
                    "updated_at": "2025-07-29T13:45:00"
                }
            }
        ]
        save_data(FLOWS_FILE, initial_flows)
    
    # スキルデータの初期化
    if not os.path.exists(SKILLS_FILE):
        initial_skills = []
        skill_areas = ["経理業務", "人事業務", "総務業務", "営業業務", "情報システム", "マーケティング", "法務", "広報", "開発", "デザイン"]
        for i in range(1, 21): # 最低20個のスキルを生成
            skill_area = skill_areas[(i-1) % len(skill_areas)] + f"_{i}"
            initial_skills.append({
                "id": f"skill_{i:03d}",
                "スキル分野": skill_area,
                "現在レベル": (i % 5) + 1, # 1-5のレベルをランダムに設定
                "目標レベル": ((i + 2) % 5) + 1, # 1-5のレベルをランダムに設定
                "経験業務数": (i % 10) + 1
            })
        save_data(SKILLS_FILE, initial_skills)
    
    # 組織データの初期化（階層構造対応）
    if not os.path.exists(ORG_FILE):
        initial_org = [
            # 経営管理グループ
            {"id": "org_001", "グループ": "経営管理グループ", "部門": "法務部", "課・係": "地方法律", "業務": "地方法令対応", "担当者": "田中", "重要度": "★★★"},
            {"id": "org_002", "グループ": "経営管理グループ", "部門": "法務部", "課・係": "国法律", "業務": "国法令対応", "担当者": "佐藤", "重要度": "★★★"},
            {"id": "org_003", "グループ": "経営管理グループ", "部門": "法務部", "課・係": "", "業務": "契約書審査", "担当者": "鈴木", "重要度": "★★☆"},
            {"id": "org_004", "グループ": "経営管理グループ", "部門": "労務部", "課・係": "人事課", "業務": "採用業務", "担当者": "山田", "重要度": "★★★"},
            {"id": "org_005", "グループ": "経営管理グループ", "部門": "労務部", "課・係": "給与課", "業務": "給与計算", "担当者": "高橋", "重要度": "★★★"},
            {"id": "org_006", "グループ": "経営管理グループ", "部門": "経理部", "課・係": "会計課", "業務": "月次決算", "担当者": "伊藤", "重要度": "★★★"},
            {"id": "org_007", "グループ": "経営管理グループ", "部門": "経理部", "課・係": "税務課", "業務": "税務申告", "担当者": "渡辺", "重要度": "★★★"},
            {"id": "org_008", "グループ": "経営管理グループ", "部門": "経理部", "課・係": "", "業務": "請求書発行", "担当者": "加藤", "重要度": "★★☆"},
            
            # 営業グループ
            {"id": "org_009", "グループ": "営業グループ", "部門": "営業部", "課・係": "第一営業課", "業務": "新規開拓", "担当者": "中村", "重要度": "★★★"},
            {"id": "org_010", "グループ": "営業グループ", "部門": "営業部", "課・係": "第二営業課", "業務": "既存顧客対応", "担当者": "小林", "重要度": "★★☆"},
            {"id": "org_011", "グループ": "営業グループ", "部門": "営業部", "課・係": "", "業務": "営業企画", "担当者": "松本", "重要度": "★★☆"},
            {"id": "org_012", "グループ": "営業グループ", "部門": "マーケティング部", "課・係": "", "業務": "市場調査", "担当者": "井上", "重要度": "★★☆"},
            
            # 技術グループ
            {"id": "org_013", "グループ": "技術グループ", "部門": "情報システム部", "課・係": "開発課", "業務": "システム開発", "担当者": "木村", "重要度": "★★★"},
            {"id": "org_014", "グループ": "技術グループ", "部門": "情報システム部", "課・係": "運用課", "業務": "システム運用", "担当者": "林", "重要度": "★★★"},
            {"id": "org_015", "グループ": "技術グループ", "部門": "情報システム部", "課・係": "", "業務": "IT戦略", "担当者": "清水", "重要度": "★★☆"}
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
    .start-node {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .end-node {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .decision-node {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .task-node {
        background-color: #e7f3ff;
        border-left: 4px solid #007bff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .org-group {
        background-color: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .org-department {
        background-color: #e9ecef;
        border: 1px solid #6c757d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .org-subdivision {
        background-color: #fff;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 10px;
        margin: 8px 0;
        border-left: 3px solid #ffc107;
    }
    .org-task {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 8px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .org-task:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .step-container {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .branch-container {
        border: 2px dashed #6c757d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fff;
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
    ["ホーム", "OpsMap", "FlowBuilder", "業務辞書", "スキルマップ", "設定"]
)

# メイン画面
if page == "ホーム":
    st.markdown("<h1 class=\"main-header\">🏠 ホーム</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class=\"section-header\">📅 今週の業務予定</div>", unsafe_allow_html=True)
        st.info("• 請求書発行（月末）\n• 月次決算準備\n• 新入社員研修")
    
    with col2:
        st.markdown("<div class=\"section-header\">📊 スキル進捗</div>", unsafe_allow_html=True)
        skills_data = load_data(SKILLS_FILE)
        if skills_data:
            for skill in skills_data[:3]: # ここはホーム画面の簡易表示なので3つに制限
                level_stars = "★" * skill["現在レベル"] + "☆" * (5 - skill["現在レベル"])
                st.success(f"• {skill['スキル分野']}: {level_stars}")
    
    with col3:
        st.markdown("<div class=\"section-header\">🔔 通知</div>", unsafe_allow_html=True)
        st.warning("• 属人化業務が3件検出されました\n• 新しい業務テンプレートが追加されました")

elif page == "OpsMap":
    st.markdown("<h1 class=\"main-header\">🗺️ OpsMap（組織構造）</h1>", unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 組織マップ表示", "✏️ 組織データ編集"])
    
    with tab1:
        st.markdown("<div class=\"section-header\">階層組織マップ</div>", unsafe_allow_html=True)
        
        org_data = load_data(ORG_FILE)
        if org_data:
            # 階層表示を実行
            render_hierarchical_organization(org_data)
        
        st.info("💡 各業務をクリックすると、FlowBuilderで詳細なプロセスを確認できます。")
    
    with tab2:
        st.markdown("<div class=\"section-header\">組織データの追加・編集</div>", unsafe_allow_html=True)
        
        # 新規追加フォーム
        with st.expander("➕ 新しい組織データを追加", expanded=False):
            with st.form("add_org_form"):
                new_group = st.text_input("グループ名（例：経営管理グループ）")
                new_dept = st.text_input("部門名（例：法務部）")
                new_subdept = st.text_input("課・係名（例：地方法律）※任意")
                new_task = st.text_input("業務名")
                new_person = st.text_input("担当者")
                new_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"])
                
                if st.form_submit_button("追加"):
                    if new_group and new_dept and new_task and new_person:
                        org_data = load_data(ORG_FILE)
                        new_id = f"org_{len(org_data) + 1:03d}"
                        new_org = {
                            "id": new_id,
                            "グループ": new_group,
                            "部門": new_dept,
                            "課・係": new_subdept,
                            "業務": new_task,
                            "担当者": new_person,
                            "重要度": new_importance
                        }
                        org_data.append(new_org)
                        save_data(ORG_FILE, org_data)
                        st.success("組織データが追加されました！")
                        st.rerun()
        
        # 既存データの編集・削除
        org_data = load_data(ORG_FILE)
        if org_data:
            st.subheader("既存データの編集・削除")
            for i, org in enumerate(org_data):
                with st.expander(f"📝 {org['グループ']} > {org['部門']} > {org.get('課・係', '')} - {org['業務']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        with st.form(f"edit_org_form_{i}"):
                            edit_group = st.text_input("グループ名", value=org["グループ"], key=f"group_{i}")
                            edit_dept = st.text_input("部門名", value=org["部門"], key=f"dept_{i}")
                            edit_subdept = st.text_input("課・係名", value=org.get("課・係", ""), key=f"subdept_{i}")
                            edit_task = st.text_input("業務名", value=org["業務"], key=f"task_{i}")
                            edit_person = st.text_input("担当者", value=org["担当者"], key=f"person_{i}")
                            edit_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"], 
                                                         index=["★☆☆", "★★☆", "★★★"].index(org["重要度"]), key=f"imp_{i}")
                            
                            if st.form_submit_button("更新"):
                                org_data[i] = {
                                    "id": org["id"],
                                    "グループ": edit_group,
                                    "部門": edit_dept,
                                    "課・係": edit_subdept,
                                    "業務": edit_task,
                                    "担当者": edit_person,
                                    "重要度": edit_importance
                                }
                                save_data(ORG_FILE, org_data)
                                st.success("データが更新されました！")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️ 削除", key=f"delete_org_{i}"):
                            org_data.pop(i)
                            save_data(ORG_FILE, org_data)
                            st.success("データが削除されました！")
                            st.rerun()

elif page == "FlowBuilder":
    st.markdown("<h1 class=\"main-header\">🔄 FlowBuilder</h1>", unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 フロー表示", "✏️ フロー編集"])
    
    with tab1:
        flows_data = load_data(FLOWS_FILE)
        
        if flows_data:
            # フロー選択
            flow_names = [flow["flow_name"] for flow in flows_data]
            selected_flow_name = st.selectbox("表示するフローを選択", flow_names)
            
            # 選択されたフローを表示
            selected_flow = next(flow for flow in flows_data if flow["flow_name"] == selected_flow_name)
            
            # 階層表示でフローを描画
            render_hierarchical_flow(selected_flow)
            
            # 接続関係の表示
            st.markdown("---")
            st.subheader("🔗 フロー接続詳細")
            if selected_flow['connections']:
                connections_df = pd.DataFrame(selected_flow['connections'])
                st.dataframe(connections_df, use_container_width=True)
            else:
                st.info("接続が定義されていません")
            
            # JSON表示
            with st.expander("📄 JSON構造を表示", expanded=False):
                st.json(selected_flow)
    
    with tab2:
        st.markdown("<div class=\"section-header\">フローの追加・編集</div>", unsafe_allow_html=True)
        
        # 新規フロー作成
        with st.expander("➕ 新しいフローを作成", expanded=False):
            with st.form("add_flow_form"):
                new_flow_name = st.text_input("フロー名")
                new_flow_desc = st.text_area("フローの説明")
                
                if st.form_submit_button("フローを作成"):
                    if new_flow_name and new_flow_desc:
                        flows_data = load_data(FLOWS_FILE)
                        new_flow_id = f"flow_{len(flows_data) + 1:03d}"
                        new_flow = {
                            "flow_id": new_flow_id,
                            "flow_name": new_flow_name,
                            "description": new_flow_desc,
                            "nodes": [
                                {
                                    "node_id": "start_1",
                                    "type": "start",
                                    "label": "開始",
                                    "position": {"x": 100, "y": 50}
                                },
                                {
                                    "node_id": "end_1",
                                    "type": "end",
                                    "label": "完了",
                                    "position": {"x": 300, "y": 50}
                                }
                            ],
                            "connections": [],
                            "metadata": {
                                "created_by": "user",
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }
                        }
                        flows_data.append(new_flow)
                        save_data(FLOWS_FILE, flows_data)
                        st.success("新しいフローが作成されました！")
                        st.rerun()
        
        # 既存フローの編集
        flows_data = load_data(FLOWS_FILE)
        if flows_data:
            st.subheader("既存フローの編集")
            
            for flow_idx, flow in enumerate(flows_data):
                with st.expander(f"📝 {flow['flow_name']}", expanded=False):
                    # フロー基本情報の編集
                    with st.form(f"edit_flow_basic_{flow_idx}"):
                        edit_flow_name = st.text_input("フロー名", value=flow["flow_name"], key=f"flow_name_{flow_idx}")
                        edit_flow_desc = st.text_area("説明", value=flow["description"], key=f"flow_desc_{flow_idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("基本情報を更新"):
                                flows_data[flow_idx]["flow_name"] = edit_flow_name
                                flows_data[flow_idx]["description"] = edit_flow_desc
                                flows_data[flow_idx]["metadata"]["updated_at"] = datetime.now().isoformat()
                                save_data(FLOWS_FILE, flows_data)
                                st.success("フロー情報が更新されました！")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ フローを削除"):
                                flows_data.pop(flow_idx)
                                save_data(FLOWS_FILE, flows_data)
                                st.success("フローが削除されました！")
                                st.rerun()
                    
                    # ノードの追加
                    st.subheader("ノードの追加")
                    with st.form(f"add_node_{flow_idx}"):
                        node_label = st.text_input("ノード名", key=f"node_label_{flow_idx}")
                        node_desc = st.text_area("説明", key=f"node_desc_{flow_idx}")
                        node_type = st.selectbox("タイプ", ["task", "decision", "input", "output"], key=f"node_type_{flow_idx}")
                        node_assigned = st.text_input("担当者", key=f"node_assigned_{flow_idx}")
                        node_time = st.number_input("予想時間（分）", min_value=0, key=f"node_time_{flow_idx}")
                        
                        if st.form_submit_button("ノードを追加"):
                            if node_label:
                                new_node_id = f"step_{len([n for n in flow['nodes'] if n['type'] not in ['start', 'end']]) + 1}"
                                new_node = {
                                    "node_id": new_node_id,
                                    "type": node_type,
                                    "label": node_label,
                                    "description": node_desc,
                                    "assigned_to": node_assigned,
                                    "estimated_time": node_time,
                                    "position": {"x": 200, "y": 50}
                                }
                                flows_data[flow_idx]["nodes"].insert(-1, new_node)  # 最後のendノードの前に挿入
                                flows_data[flow_idx]["metadata"]["updated_at"] = datetime.now().isoformat()
                                save_data(FLOWS_FILE, flows_data)
                                st.success("ノードが追加されました！")
                                st.rerun()
                    
                    # 接続の追加（分岐対応）
                    st.subheader("接続の追加（分岐対応）")
                    with st.form(f"add_connection_{flow_idx}"):
                        # ノード選択肢を作成
                        node_options = [f"{node['node_id']} ({node['label']})" for node in flow['nodes']]
                        
                        from_node = st.selectbox("接続元ノード", node_options, key=f"from_node_{flow_idx}")
                        to_node = st.selectbox("接続先ノード", node_options, key=f"to_node_{flow_idx}")
                        condition = st.text_input("分岐条件（例：承認、差し戻し、再提出）", key=f"condition_{flow_idx}")
                        
                        st.info("💡 分岐を作成するには、同じ接続元ノードから複数の接続を異なる条件で作成してください。")
                        
                        if st.form_submit_button("接続を追加"):
                            if from_node and to_node:
                                from_id = from_node.split(' ')[0]
                                to_id = to_node.split(' ')[0]
                                
                                new_connection = {
                                    "from": from_id,
                                    "to": to_id
                                }
                                if condition:
                                    new_connection["condition"] = condition
                                
                                flows_data[flow_idx]["connections"].append(new_connection)
                                flows_data[flow_idx]["metadata"]["updated_at"] = datetime.now().isoformat()
                                save_data(FLOWS_FILE, flows_data)
                                st.success("接続が追加されました！")
                                st.rerun()
                    
                    # 既存接続の管理
                    if flow['connections']:
                        st.subheader("既存接続の管理")
                        for conn_idx, conn in enumerate(flow['connections']):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                condition_text = f" (条件: {conn['condition']})" if conn.get('condition') else ""
                                st.write(f"**{conn['from']}** → **{conn['to']}**{condition_text}")
                            with col2:
                                if st.button("🗑️", key=f"delete_conn_{flow_idx}_{conn_idx}"):
                                    flows_data[flow_idx]["connections"].pop(conn_idx)
                                    save_data(FLOWS_FILE, flows_data)
                                    st.success("接続が削除されました！")
                                    st.rerun()

elif page == "業務辞書":
    st.markdown("<h1 class=\"main-header\">📚 業務辞書</h1>", unsafe_allow_html=True)
    
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
        st.markdown("<div class=\"section-header\">業務の追加・編集</div>", unsafe_allow_html=True)
        
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
    st.markdown("<h1 class=\"main-header\">🎯 スキルマップ</h1>", unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 スキル表示", "✏️ スキル編集"])
    
    with tab1:
        skills_data = load_data(SKILLS_FILE)
        
        if skills_data:
            df_skills = pd.DataFrame(skills_data)
            
            # スキルチャート
            st.subheader("📊 スキルレベル")
            chart_data = df_skills.set_index("スキル分野")[["現在レベル", "目標レベル"]]
            st.bar_chart(chart_data) # ここで全スキルが表示されるはず
            
            # 詳細テーブル
            st.subheader("📋 詳細データ")
            st.dataframe(df_skills.drop('id', axis=1), use_container_width=True)
            
            # 成長提案
            st.subheader("💡 成長提案")
            suggestions = []
            for skill in skills_data:
                if skill["現在レベル"] < skill["目標レベル"]:
                    suggestions.append(f"• {skill['スキル分野']}のスキルアップが必要です（現在: {skill['現在レベル']}, 目標: {skill['目標レベル']}）")
            
            if suggestions:
                st.info("\n".join(suggestions))
            else:
                st.success("すべてのスキルが目標レベルに達しています！")
    
    with tab2:
        st.markdown("<div class=\"section-header\">スキルの追加・編集</div>", unsafe_allow_html=True)
        
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
    st.markdown("<h1 class=\"main-header\">⚙️ 設定</h1>", unsafe_allow_html=True)
    
    st.subheader("🎨 表示設定")
    theme = st.selectbox("テーマ", ["ライト", "ダーク"])
    language = st.selectbox("言語", ["日本語", "English"])
    
    st.subheader("💾 データ設定")
    auto_save = st.checkbox("自動保存を有効にする", value=True)
    backup_frequency = st.selectbox("バックアップ頻度", ["毎日", "毎週", "毎月"])
    
    if st.button("設定を保存"):
        st.success("設定が保存されました！")
    
    # データ管理
    st.subheader("📊 データ管理")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 データをエクスポート"):
            # 全データをJSONで出力
            all_data = {
                "tasks": load_data(TASKS_FILE),
                "flows": load_data(FLOWS_FILE),
                "skills": load_data(SKILLS_FILE),
                "organization": load_data(ORG_FILE)
            }
            st.download_button(
                label="📥 全データをダウンロード",
                data=json.dumps(all_data, ensure_ascii=False, indent=2),
                file_name=f"backops_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 データをインポート", type=['json'])
        if uploaded_file is not None:
            try:
                import_data = json.load(uploaded_file)
                if st.button("インポート実行"):
                    if "tasks" in import_data:
                        save_data(TASKS_FILE, import_data["tasks"])
                    if "flows" in import_data:
                        save_data(FLOWS_FILE, import_data["flows"])
                    if "skills" in import_data:
                        save_data(SKILLS_FILE, import_data["skills"])
                    if "organization" in import_data:
                        save_data(ORG_FILE, import_data["organization"])
                    st.success("データがインポートされました！")
                    st.rerun()
            except Exception as e:
                st.error(f"インポートエラー: {e}")
    
    with col3:
        if st.button("🗑️ 全データをリセット"):
            if st.checkbox("本当にリセットしますか？"):
                # データファイルを削除して初期化
                for file in [TASKS_FILE, FLOWS_FILE, SKILLS_FILE, ORG_FILE]:
                    if os.path.exists(file):
                        os.remove(file)
                init_data_once.clear()  # キャッシュをクリア
                st.success("データがリセットされました！")
                st.rerun()

# フッター
st.sidebar.markdown("---")
st.sidebar.markdown("**BackOps Guide v5.0**")
st.sidebar.markdown("© 2025 Manus Team")
st.sidebar.markdown("✨ 階層組織・フロー表示対応版")

