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
    
    # フローデータの初期化
    if not os.path.exists(FLOWS_FILE):
        initial_flows = [
            {
                "flow_id": "flow_001",
                "flow_name": "請求書発行フロー",
                "description": "請求内容確認から請求書送付までの流れ",
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
                        "description": "見積書・契約書と照合",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 30,
                        "position": {"x": 300, "y": 50}
                    },
                    {
                        "node_id": "step_2",
                        "type": "task",
                        "label": "請求書作成",
                        "description": "freeeで作成",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 20,
                        "position": {"x": 500, "y": 50}
                    },
                    {
                        "node_id": "step_3",
                        "type": "decision",
                        "label": "承認",
                        "description": "上長による承認",
                        "assigned_to": "上長",
                        "estimated_time": 10,
                        "position": {"x": 700, "y": 50}
                    },
                    {
                        "node_id": "step_4",
                        "type": "task",
                        "label": "送付",
                        "description": "PDFメールで送付",
                        "assigned_to": "経理部・田中",
                        "estimated_time": 10,
                        "position": {"x": 900, "y": 50}
                    },
                    {
                        "node_id": "end_1",
                        "type": "end",
                        "label": "完了",
                        "position": {"x": 1100, "y": 50}
                    }
                ],
                "connections": [
                    {"from": "start_1", "to": "step_1"},
                    {"from": "step_1", "to": "step_2"},
                    {"from": "step_2", "to": "step_3"},
                    {"from": "step_3", "to": "step_4", "condition": "承認"},
                    {"from": "step_4", "to": "end_1"}
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
        initial_skills = [
            {"id": "skill_001", "スキル分野": "経理業務", "現在レベル": 3, "目標レベル": 4, "経験業務数": 5},
            {"id": "skill_002", "スキル分野": "人事業務", "現在レベル": 2, "目標レベル": 3, "経験業務数": 2},
            {"id": "skill_003", "スキル分野": "総務業務", "現在レベル": 1, "目標レベル": 2, "経験業務数": 1},
            {"id": "skill_004", "スキル分野": "営業業務", "現在レベル": 1, "目標レベル": 2, "経験業務数": 0},
            {"id": "skill_005", "スキル分野": "情報システム", "現在レベル": 1, "目標レベル": 3, "経験業務数": 1}
        ]
        save_data(SKILLS_FILE, initial_skills)
    
    # 組織データの初期化
    if not os.path.exists(ORG_FILE):
        initial_org = [
            {"id": "org_001", "部門": "管理部", "業務": "経理業務", "担当者": "田中", "重要度": "★★★"},
            {"id": "org_002", "部門": "管理部", "業務": "人事業務", "担当者": "佐藤", "重要度": "★★☆"},
            {"id": "org_003", "部門": "管理部", "業務": "総務業務", "担当者": "鈴木", "重要度": "★★☆"},
            {"id": "org_004", "部門": "営業部", "業務": "営業活動", "担当者": "山田", "重要度": "★★★"},
            {"id": "org_005", "部門": "営業部", "業務": "顧客対応", "担当者": "高橋", "重要度": "★★☆"},
            {"id": "org_006", "部門": "情報システム部", "業務": "システム管理", "担当者": "伊藤", "重要度": "★★★"}
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
    .flow-node {
        background-color: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        min-width: 120px;
        display: inline-block;
    }
    .flow-arrow {
        color: #007bff;
        font-size: 1.5rem;
        margin: 0 10px;
    }
    .org-node {
        background-color: #e9ecef;
        border: 1px solid #6c757d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .org-node:hover {
        background-color: #dee2e6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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

elif page == "OpsMap":
    st.markdown('<h1 class="main-header">🗺️ OpsMap（組織構造）</h1>', unsafe_allow_html=True)
    
    # タブで表示と編集を分ける
    tab1, tab2 = st.tabs(["📊 組織マップ表示", "✏️ 組織データ編集"])
    
    with tab1:
        st.markdown('<div class="section-header">部門別業務マップ</div>', unsafe_allow_html=True)
        
        org_data = load_data(ORG_FILE)
        if org_data:
            # 部門別にグループ化
            departments = {}
            for org in org_data:
                dept = org["部門"]
                if dept not in departments:
                    departments[dept] = []
                departments[dept].append(org)
            
            # 部門ごとに表示
            for dept_name, dept_tasks in departments.items():
                st.subheader(f"🏢 {dept_name}")
                
                cols = st.columns(min(len(dept_tasks), 3))
                for i, task in enumerate(dept_tasks):
                    with cols[i % 3]:
                        if st.button(f"📋 {task['業務']}\n👤 {task['担当者']}\n{task['重要度']}", 
                                   key=f"org_task_{task['id']}"):
                            st.session_state.selected_task = task['業務']
                            st.info(f"選択された業務: {task['業務']}")
        
        st.info("💡 各業務をクリックすると、FlowBuilderで詳細なプロセスを確認できます。")
    
    with tab2:
        st.markdown('<div class="section-header">組織データの追加・編集</div>', unsafe_allow_html=True)
        
        # 新規追加フォーム
        with st.expander("➕ 新しい組織データを追加", expanded=False):
            with st.form("add_org_form"):
                new_dept = st.text_input("部門名")
                new_task = st.text_input("業務名")
                new_person = st.text_input("担当者")
                new_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"])
                
                if st.form_submit_button("追加"):
                    if new_dept and new_task and new_person:
                        org_data = load_data(ORG_FILE)
                        new_id = f"org_{len(org_data) + 1:03d}"
                        new_org = {
                            "id": new_id,
                            "部門": new_dept,
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
                with st.expander(f"📝 {org['部門']} - {org['業務']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        with st.form(f"edit_org_form_{i}"):
                            edit_dept = st.text_input("部門名", value=org["部門"], key=f"dept_{i}")
                            edit_task = st.text_input("業務名", value=org["業務"], key=f"task_{i}")
                            edit_person = st.text_input("担当者", value=org["担当者"], key=f"person_{i}")
                            edit_importance = st.selectbox("重要度", ["★☆☆", "★★☆", "★★★"], 
                                                         index=["★☆☆", "★★☆", "★★★"].index(org["重要度"]), key=f"imp_{i}")
                            
                            if st.form_submit_button("更新"):
                                org_data[i] = {
                                    "id": org["id"],
                                    "部門": edit_dept,
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
    st.markdown('<h1 class="main-header">🔄 FlowBuilder</h1>', unsafe_allow_html=True)
    
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
            
            st.markdown(f'<div class="section-header">{selected_flow["flow_name"]}</div>', unsafe_allow_html=True)
            st.write(f"**説明**: {selected_flow['description']}")
            
            # フローチャートの視覚的表示
            st.subheader("🔄 フローチャート")
            
            # ノードを横に並べて表示
            flow_html = '<div style="display: flex; align-items: center; overflow-x: auto; padding: 20px;">'
            
            for i, node in enumerate(selected_flow['nodes']):
                if node['type'] == 'start':
                    flow_html += f'<div class="flow-node" style="background-color: #d4edda; border-color: #28a745;">🚀 {node["label"]}</div>'
                elif node['type'] == 'end':
                    flow_html += f'<div class="flow-node" style="background-color: #f8d7da; border-color: #dc3545;">🏁 {node["label"]}</div>'
                elif node['type'] == 'decision':
                    flow_html += f'<div class="flow-node" style="background-color: #fff3cd; border-color: #ffc107;">❓ {node["label"]}</div>'
                else:
                    flow_html += f'<div class="flow-node">📋 {node["label"]}</div>'
                
                # 矢印を追加（最後のノード以外）
                if i < len(selected_flow['nodes']) - 1:
                    flow_html += '<span class="flow-arrow">→</span>'
            
            flow_html += '</div>'
            st.markdown(flow_html, unsafe_allow_html=True)
            
            # ノード詳細一覧
            st.subheader("📋 業務ステップ詳細")
            
            for i, node in enumerate(selected_flow['nodes']):
                if node['type'] not in ['start', 'end']:
                    with st.expander(f"ステップ {i}: {node['label']}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**説明**: {node.get('description', 'なし')}")
                            st.write(f"**担当者**: {node.get('assigned_to', 'なし')}")
                        with col2:
                            st.write(f"**予想時間**: {node.get('estimated_time', 'なし')}分")
                            st.write(f"**タイプ**: {node['type']}")
            
            # 接続関係の表示
            st.subheader("🔗 フロー接続")
            connections_df = pd.DataFrame(selected_flow['connections'])
            st.dataframe(connections_df, use_container_width=True)
            
            # JSON表示
            with st.expander("📄 JSON構造を表示", expanded=False):
                st.json(selected_flow)
    
    with tab2:
        st.markdown('<div class="section-header">フローの追加・編集</div>', unsafe_allow_html=True)
        
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
st.sidebar.markdown("**BackOps Guide v3.0**")
st.sidebar.markdown("© 2025 Manus Team")
st.sidebar.markdown("✨ FlowBuilder & OpsMap 完全版")

