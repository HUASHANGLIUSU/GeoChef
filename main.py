import streamlit as st
from core import GeoChef
from model import ECNUModel
from github_parser import load_github_paper_links, get_paper_link_by_name
from paper_explainer import explain_paper_by_link

# ====================== 初始化主题状态 ======================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# ====================== 动态CSS样式（适配深浅色） ======================
def get_theme_css():
    if st.session_state.theme_mode == "dark":
        primary_color = "#2563eb"
        bg_color = "#111827"
        card_bg = "#1f2937"
        input_bg = "#374151"
        text_color = "#f9fafb"
        border_color = "#374151"
        hover_color = "#4b5563"
        user_msg_bg = "#3b82f6"
        assistant_msg_bg = "#374151"
        no_result_bg = "#1f2937"
        explain_area_bg = "#374151"
    else:
        primary_color = "#2563eb"
        bg_color = "#ffffff"
        card_bg = "#ffffff"
        input_bg = "#ffffff"
        text_color = "#111827"
        border_color = "#e2e8f0"
        hover_color = "#f3f4f6"
        user_msg_bg = "#e1f5fe"
        assistant_msg_bg = "#f5f5f5"
        no_result_bg = "#f8fafc"
        explain_area_bg = "#f1f5f9"

    return f"""
<style>
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}
.stApp {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem;
    background-color: {bg_color} !important;
    color: {text_color} !important;
}}
h1, h2, h3, h4, h5, h6 {{
    color: {text_color} !important;
}}
.stButton > button {{
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
    height: 40px !important;
    font-weight: 500 !important;
    color: white !important;
    background-color: {primary_color} !important;
}}
.stButton > button[type="secondary"] {{
    background-color: {hover_color} !important;
    color: {text_color} !important;
}}
.stButton > button:hover {{
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    transform: translateY(-1px) !important;
    opacity: 0.95;
}}
.stMultiSelect > div {{
    border-radius: 8px !important;
    border: 1px solid {border_color} !important;
    background-color: {input_bg} !important;
    color: {text_color} !important;
}}
.stTextInput > div > div > input {{
    border-radius: 8px !important;
    border: 1px solid {border_color} !important;
    background-color: {input_bg} !important;
    padding: 0.6rem 1rem !important;
    color: {text_color} !important;
}}
.result-card {{
    background-color: {card_bg} !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    border: 1px solid {border_color} !important;
    color: {text_color} !important;
}}
.loading-text {{
    color: {primary_color} !important;
    font-weight: 500 !important;
}}
.no-result {{
    padding: 2rem !important;
    text-align: center !important;
    background-color: {no_result_bg} !important;
    border-radius: 12px !important;
    border: 1px dashed {border_color} !important;
    color: {text_color} !important;
    margin: 1rem 0 !important;
}}
.stDivider {{
    margin: 1.5rem 0 !important;
}}
.explain-area {{
    background-color: {explain_area_bg} !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin-top: 0.8rem !important;
    line-height: 1.6 !important;
    color: {text_color} !important;
}}
.github-link {{
    color: {primary_color} !important;
    text-decoration: none !important;
    font-weight: 500 !important;
    display: inline-block !important;
    margin-top: 8px !important;
}}
.github-link:hover {{
    text-decoration: underline !important;
}}
.chat-history {{
    max-height: 300px !important;
    overflow-y: auto !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    background-color: {card_bg} !important;
    margin-bottom: 1rem !important;
    border: 1px solid {border_color} !important;
}}
.user-message {{
    background-color: {user_msg_bg} !important;
    padding: 0.8rem 1rem !important;
    border-radius: 8px !important;
    margin-bottom: 0.8rem !important;
    text-align: right !important;
    color: {text_color} !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}}
.assistant-message {{
    background-color: {assistant_msg_bg} !important;
    padding: 0.8rem 1rem !important;
    border-radius: 8px !important;
    margin-bottom: 0.8rem !important;
    text-align: left !important;
    color: {text_color} !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}}
ul {{
    margin: 0.8rem 0 !important;
    padding-left: 1.8rem !important;
}}
li {{
    margin-bottom: 0.5rem;
    color: {text_color} !important;
    line-height: 1.5 !important;
}}
.link-button {{
    display: block !important;
    width: 100% !important;
    height: 40px !important;
    line-height: 40px !important;
    text-align: center !important;
    background-color: {primary_color} !important;
    color: white !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
}}
.leak-button-wrapper {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;
    margin-top: 24px !important;
}}
</style>
"""
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ====================== 多语言配置 ======================
I18N = {
    "cn": {
        "title": "🌍 GeoChef ",
        "modal": "数据模态 (可多选)",
        "task": "任务类型 (可多选)",
        "year": "年份 (可多选)",
        "publisher": "发布单位 (可多选)",
        "method": "方法类型 (可多选)",
        "search_btn": "🔍 开始检索",
        "random": "🎲 随机一条",
        "result": "检索结果",
        "no_result": "未找到符合条件的数据",
        "switch_lang": "🌐 切换语言 EN",
        "switch_theme": "🌓 切换深色/浅色",
        "loading": "加载中...",
        "paper_url": "📄 论文原文链接",
        "no_paper_link": "暂未找到该数据集的论文链接",
        "explain_btn": "🧠 AI论文讲解",
        "view_btn": "🔗 查看原文",
        "explain_loading": "AI 正在生成论文讲解...",
        "explain_success": "✅ 论文讲解生成完成！",
        "chat_input": "ChatECNU助手（输入问题）",
        "chat_send": "📤 发送",
        "chat_clear": "🗑️ 清空聊天",
        "chat_title": "📝 ChatECNU智能助手",
        "filter_title": "🔍 精准筛选",
        "leak_title": "⚠️ 数据泄露风险检测",
        "leak_select_train": "选择训练集使用的数据集",
        "leak_detect_btn": "🔍 检测泄露风险",
        "leak_detecting": "正在检测数据泄露风险...",
        "leak_result_title": "📋 检测结果",
        "leak_train_dataset": "训练集数据集：",
        "leak_original_datasets": "关联原始数据集：",
        "leak_risk_title": "⚠️ 存在数据泄露风险的测试集（共{count}个）",
        "leak_risk_originals": "泄露的原始数据集：",
        "leak_no_risk": "✅ 未检测到数据泄露风险",
        "leak_no_risk_desc": "未找到与该训练集共享原始数据集的测试集",
        "paper_chat_title": "📚 OpenAI论文助手",
        "paper_chat_input": "输入论文链接或粘贴URL，我来帮你讲解",
        "paper_chat_send": "📤 讲解论文",
        "paper_chat_clear": "🗑️ 清空对话"
    },
    "en": {
        "title": "🌍 GeoChef ",
        "modal": "Modality (Multi-Select)",
        "task": "Task (Multi-Select)",
        "year": "Year (Multi-Select)",
        "publisher": "Publisher (Multi-Select)",
        "method": "Method (Multi-Select)",
        "search_btn": "🔍 Search",
        "random": "🎲 Random One",
        "result": "Results",
        "no_result": "No Result Found",
        "switch_lang": "🌐 Switch Language 中文",
        "switch_theme": "🌓 Switch Dark/Light",
        "loading": "Loading...",
        "paper_url": "📄 Paper URL",
        "no_paper_link": "No paper link found for this dataset",
        "explain_btn": "🧠 AI Explain Paper",
        "view_btn": "🔗 View Paper",
        "explain_loading": "AI is generating paper explanation...",
        "explain_success": "✅ Paper explanation generated!",
        "chat_input": "ChatECNU Assistant (Input Question)",
        "chat_send": "📤 Send",
        "chat_clear": "🗑️ Clear Chat",
        "chat_title": "📝 ChatECNU AI Assistant",
        "filter_title": "🔍 Precise Filter",
        "leak_title": "⚠️ Data Leakage Risk Detection",
        "leak_select_train": "Select Training Dataset",
        "leak_detect_btn": "🔍 Detect Leakage Risk",
        "leak_detecting": "Detecting data leakage risk...",
        "leak_result_title": "📋 Detection Result",
        "leak_train_dataset": "Training Dataset：",
        "leak_original_datasets": "Associated Original Datasets：",
        "leak_risk_title": "⚠️ Risky Test Datasets ({count} total)",
        "leak_risk_originals": "Leaked Original Datasets：",
        "leak_no_risk": "✅ No Data Leakage Risk Detected",
        "leak_no_risk_desc": "No test datasets sharing original datasets with this training set were found",
        "paper_chat_title": "📚 Paper Explanation Assistant",
        "paper_chat_input": "Enter a paper link or paste URL, I'll explain it",
        "paper_chat_send": "📤 Explain Paper",
        "paper_chat_clear": "🗑️ Clear Chat"
    }
}

def main():
    st.set_page_config(
        page_title="GeoChef",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🌍"
    )

    if "lang" not in st.session_state:
        st.session_state.lang = "cn"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "paper_chat_history" not in st.session_state:
        st.session_state.paper_chat_history = []

    lang = st.session_state.lang
    i18n = I18N[lang]

    # 顶部导航
    top_col1, top_col2, top_col3, top_col4 = st.columns([5, 1.5, 1.5, 2])
    with top_col1:
        st.title(i18n["title"])
    with top_col2:
        if st.button(i18n["switch_lang"], use_container_width=True):
            st.session_state.lang = "en" if lang == "cn" else "cn"
            st.rerun()
    with top_col3:
        theme_text = "🌙 深色模式" if st.session_state.theme_mode == "light" else "☀️ 浅色模式"
        if st.button(theme_text, use_container_width=True, type="secondary"):
            st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"
            st.rerun()
    with top_col4:
        st.markdown(f'<div style="display: flex; align-items: center; height: 100%;"><a href="https://github.com/VisionXLab/Awesome-RS-VL-Data" target="_blank" class="github-link">Github主页持续更新中...</a></div>', unsafe_allow_html=True)

    # 加载数据
    if "github_loaded" not in st.session_state:
        with st.spinner(i18n["loading"]):
            load_github_paper_links()
            st.session_state.github_loaded = True

    if "chef" not in st.session_state:
        with st.spinner(i18n["loading"]):
            chef = GeoChef()
            chef.load()
            st.session_state.chef = chef
    chef = st.session_state.chef

    # ====================== ChatECNU智能助手 ======================
    st.subheader(i18n["chat_title"], divider="blue")
    if st.session_state.chat_history:
        st.markdown("<div class='chat-history'>", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    chat_col1, chat_col2, chat_col3 = st.columns([4, 1, 1], gap="medium")
    with chat_col1:
        chat_input = st.text_input(i18n["chat_input"], placeholder="问问我“如何构建一个SAR数据集”或“为什么要检测数据泄露风险”", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button(i18n["chat_send"], use_container_width=True, type="primary")
    with chat_col3:
        clear_btn = st.button(i18n["chat_clear"], use_container_width=True, type="secondary")

    if clear_btn:
        st.session_state.chat_history = []
        st.rerun()
    if send_btn and chat_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        with st.spinner(i18n["loading"]):
            assistant_response = ECNUModel.generate_response(chat_input, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.rerun()

    # ====================== 【论文讲解助手 → 已放到最上方】 ======================
    st.subheader(i18n["paper_chat_title"], divider="blue")

    if st.session_state.paper_chat_history:
        st.markdown("<div class='chat-history'>", unsafe_allow_html=True)
        for msg in st.session_state.paper_chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    paper_chat_col1, paper_chat_col2, paper_chat_col3 = st.columns([4, 1, 1], gap="medium")
    with paper_chat_col1:
        paper_chat_input = st.text_input(
            i18n["paper_chat_input"],
            placeholder="输入论文链接/URL，或直接粘贴地址，如 https://arxiv.org/abs/xxx",
            label_visibility="collapsed"
        )
    with paper_chat_col2:
        paper_send_btn = st.button(i18n["paper_chat_send"], use_container_width=True, type="primary")
    with paper_chat_col3:
        paper_clear_btn = st.button(i18n["paper_chat_clear"], use_container_width=True, type="secondary")

    if paper_clear_btn:
        st.session_state.paper_chat_history = []
        st.rerun()
    if paper_send_btn and paper_chat_input.strip():
        st.session_state.paper_chat_history.append({"role": "user", "content": paper_chat_input})
        with st.spinner(i18n["explain_loading"]):
            full_text = ""
            for chunk in explain_paper_by_link(paper_chat_input):
                full_text += chunk
            st.session_state.paper_chat_history.append({"role": "assistant", "content": full_text})
        st.rerun()

    # ====================== 精准筛选（在论文讲解下方） ======================
    st.subheader(i18n["filter_title"], divider="blue")
    filter_cols = st.columns(5, gap="medium")
    with filter_cols[0]:
        modals = st.multiselect(i18n["modal"], chef.modalities, placeholder="请选择..." if lang == "cn" else "Select...")
    with filter_cols[1]:
        tasks = st.multiselect(i18n["task"], chef.tasks, placeholder="请选择..." if lang == "cn" else "Select...")
    with filter_cols[2]:
        years = st.multiselect(i18n["year"], chef.years, placeholder="请选择..." if lang == "cn" else "Select...")
    with filter_cols[3]:
        publishers = st.multiselect(i18n["publisher"], chef.publishers, placeholder="请选择..." if lang == "cn" else "Select...")
    with filter_cols[4]:
        methods = st.multiselect(i18n["method"], chef.methods, placeholder="请选择..." if lang == "cn" else "Select...")

    btn_cols = st.columns([7, 3], gap="medium")
    with btn_cols[0]:
        go = st.button(i18n["search_btn"], use_container_width=True)
    with btn_cols[1]:
        rand = st.button(i18n["random"], use_container_width=True, type="secondary")

    res = None
    if rand:
        res = [chef.random_one()] if chef.random_one() else []
    elif go:
        res = chef.filter(modals, tasks, years, publishers, methods, [])

    if res is not None:
        st.subheader(f"📊 {i18n['result']} ({len(res)})", divider="blue")
        if not res:
            st.markdown(f"""<div class='no-result'><h4>😶 {i18n['no_result']}</h4><p>建议调整筛选条件后重试</p></div>""", unsafe_allow_html=True)
        else:
            for idx, item in enumerate(res):
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                info_col, btn_col = st.columns([9, 3], gap="large")
                with info_col:
                    sheet_name = item.get('_sheet', 'Unknown Dataset')
                    st.markdown(f"### 📁 {sheet_name}")
                    info_list = []
                    for k, v in item.items():
                        if k not in ["_sheet", "_text", "_years"] and v:
                            line = f"- **{k}**: {v}"
                            if lang == "en":
                                line = ECNUModel.translate_line(line)
                            info_list.append(line)
                    if info_list:
                        st.markdown("\n".join(info_list))
                    else:
                        st.markdown("- 暂无详细信息" if lang == "cn" else "- No detailed information available")
                with btn_col:
                    name = str(item.get("Name", item.get("name", ""))).strip()
                    paper_link = get_paper_link_by_name(name)
                    if paper_link:
                        st.markdown(f'<a href="{paper_link}" target="_blank" class="link-button">{i18n["view_btn"]}</a>', unsafe_allow_html=True)
                    else:
                        st.info(i18n["no_paper_link"], icon="ℹ️")
                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()

    # ====================== 数据泄露风险检测 ======================
    st.subheader(i18n["leak_title"], divider="red")
    dataset_names = []
    for item in chef.data:
        name = str(item.get("Name", item.get("name", item.get("_sheet", "Unknown")))).strip()
        if name and name not in dataset_names:
            dataset_names.append(name)
    dataset_names = sorted(list(set(dataset_names)))

    leak_col1, leak_col2 = st.columns([3, 1], gap="medium")
    with leak_col1:
        selected_train = st.selectbox(i18n["leak_select_train"], dataset_names, key="leak_train_select")
    with leak_col2:
        st.markdown('<div class="leak-button-wrapper">', unsafe_allow_html=True)
        detect_leak = st.button(i18n["leak_detect_btn"], use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    if detect_leak and selected_train:
        with st.spinner(i18n["leak_detecting"]):
            train_originals, risk_items = chef.detect_leakage_risk(selected_train)
        st.markdown(f"""
        <div class='result-card'>
            <h4>{i18n['leak_result_title']}</h4>
            <p><strong>{i18n['leak_train_dataset']}</strong>{selected_train}</p>
            <p><strong>{i18n['leak_original_datasets']}</strong>{', '.join(train_originals) if train_originals else ('未识别' if lang == 'cn' else 'Unidentified')}</p>
        </div>""", unsafe_allow_html=True)
        if risk_items:
            st.markdown(f"<h5>{i18n['leak_risk_title'].format(count=len(risk_items))}</h5>", unsafe_allow_html=True)
            for idx, risk_item in enumerate(risk_items):
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                risk_name = str(risk_item.get("Name", risk_item.get("name", risk_item.get("_sheet", "Unknown")))).strip()
                st.markdown(f"### 🚨 {idx+1}. {risk_name}")
                leak_originals = risk_item.get("_leak_originals", set())
                st.markdown(f"<p><strong>{i18n['leak_risk_originals']}</strong>{', '.join(leak_originals)}</p>", unsafe_allow_html=True)
                info_list = []
                for k, v in risk_item.items():
                    if k not in ["_sheet", "_text", "_years", "_leak_originals"] and v:
                        line = f"- **{k}**: {v}"
                        if lang == "en":
                            line = ECNUModel.translate_line(line)
                        info_list.append(line)
                if info_list:
                    st.markdown("\n".join(info_list))
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='no-result'>
                <h4>{i18n['leak_no_risk']}</h4>
                <p>{i18n['leak_no_risk_desc']}</p>
            </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()