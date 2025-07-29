if isinstance(node, dict):
    with st.sidebar:
        st.markdown(f"### 📝 編集対象：「{clicked}」")

        task = node.get("業務", "")
        freq = node.get("頻度", "毎週")
        imp = node.get("重要度", 3)
        effort = node.get("工数", 0.0)
        estimate = node.get("時間目安", 0.0)

        new_task = st.text_area("業務内容", value=task, height=150)
        new_freq = st.selectbox("頻度", ["毎日", "毎週", "毎月", "その他"],
                                index=["毎日", "毎週", "毎月", "その他"].index(freq))
        new_imp = st.slider("重要度 (1〜5)", 1, 5, value=imp)
        new_effort = st.number_input("工数 (時間/週)", min_value=0.0, value=effort, step=0.5)
        new_estimate = st.number_input("作業時間目安 (分/タスク)", min_value=0.0, value=estimate, step=5.0)

        if st.button("保存（サイドバー）", key=f"save_sidebar_{clicked}"):
            node["業務"] = new_task
            node["頻度"] = new_freq
            node["重要度"] = new_imp
            node["工数"] = new_effort
            node["時間目安"] = new_estimate
            st.success("✅ サイドバーから保存しました。")

