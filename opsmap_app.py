if return_value and return_value.clicked_node_id:
    clicked = return_value.clicked_node_id
    st.markdown(f"### ✏️ 「{clicked}」の業務詳細を編集")
    node = get_node_by_path(clicked.split("/"), tree)

    if isinstance(node, dict):
        # 各項目の初期値取得
        task = node.get("業務", "")
        freq = node.get("頻度", "毎週")
        imp = node.get("重要度", 3)
        effort = node.get("工数", 0.0)
        estimate = node.get("時間目安", 0.0)

        # ✅ メイン画面：元の入力フォーム（そのまま残す）
        new_task_main = st.text_area("業務内容（メイン画面）", value=task, height=150, key="main_task")
        new_freq_main = st.selectbox("頻度（メイン画面）", ["毎日", "毎週", "毎月", "その他"],
                                     index=["毎日", "毎週", "毎月", "その他"].index(freq), key="main_freq")
        new_imp_main = st.slider("重要度 (1〜5)（メイン画面）", 1, 5, value=imp, key="main_imp")
        new_effort_main = st.number_input("工数 (時間/週)（メイン画面）", min_value=0.0, value=effort, step=0.5, key="main_effort")
        new_estimate_main = st.number_input("作業時間目安 (分/タスク)（メイン画面）", min_value=0.0, value=estimate, step=5.0, key="main_estimate")

        if st.button("保存（メイン画面）", key=f"save_main_{clicked}"):
            node["業務"] = new_task_main
            node["頻度"] = new_freq_main
            node["重要度"] = new_imp_main
            node["工数"] = new_effort_main
            node["時間目安"] = new_estimate_main
            st.success("✅ メイン画面から保存しました。")

        # ✅ サイドバー：同じ入力項目を表示
        with st.sidebar:
            st.markdown(f"### 📝 サイドバー編集：「{clicked}」")

            new_task_sb = st.text_area("業務内容", value=task, height=150, key="sb_task")
            new_freq_sb = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"],
                                       index=["毎日", "毎週", "毎月", "その他"].index(freq), key="sb_freq")
            new_imp_sb = st.slider("重要度 (1〜5)", 1, 5, value=imp, key="sb_imp")
            new_effort_sb = st.number_input("工数 (時間/週)", min_value=0.0, value=effort, step=0.5, key="sb_effort")
            new_estimate_sb = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, value=estimate, step=5.0, key="sb_estimate")

            if st.button("保存（サイドバー）", key=f"save_sb_{clicked}"):
                node["業務"] = new_task_sb
                node["頻度"] = new_freq_sb
                node["重要度"] = new_imp_sb
                node["工数"] = new_effort_sb
                node["時間目安"] = new_estimate_sb
                st.success("✅ サイドバーから保存しました。")
