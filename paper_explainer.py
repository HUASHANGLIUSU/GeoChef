from openai import OpenAI
import streamlit as st

# ===================== 配置你的 autodl 大模型 =====================
CLIENT = OpenAI(
    base_url="https://www.autodl.art/api/v1",
    api_key="LkmOfOQEacf5udaCcKsg7kSR3UIUrqqymOWRSdgvAyRnAQKx",  # 替换成你的真实 API Key
)


# ==================================================================

def get_paper_explain_prompt(link, dataset_name):
    """生成专业的遥感论文讲解提示词"""
    prompt = f"""
    请你作为遥感领域的资深研究员，基于论文链接和关联数据集，讲解这篇论文的核心内容。
    论文链接：{link}
    关联数据集：{dataset_name}

    输出格式必须严格按照以下结构（中文、专业、简洁）：
    ### 📑 论文基础信息
    - 论文链接：{link}
    - 关联数据集：{dataset_name}

    ### 📝 论文核心讲解
    #### 🔹 核心贡献
    （总结论文解决的核心问题、主要创新点，100-150字）

    #### 🔹 方法创新
    （简述论文提出的模型/方法，对比现有方法的优势，150-200字）

    #### 🔹 数据特点
    （说明数据集的规模、覆盖场景、标注类型，80-100字）

    #### 🔹 实验效果
    （总结实验数据集、评价指标、关键结果，100-150字）

    #### 🔹 学术与应用价值
    （评价论文的学术意义和实际应用场景，80-100字）

    要求：
    1. 语言符合遥感领域学术表述，专业但易懂；
    2. 内容贴合遥感视觉语言（VQA/图像描述/场景规划）方向；
    3. 无冗余内容，严格控制字数；
    4. 即使信息有限，也要基于领域常识生成合理、专业的讲解。
    """
    return prompt.strip()


def explain_paper_by_link(link, dataset_name=""):
    """
    调用 autodl 大模型讲解论文（流式输出）
    :param link: 论文链接
    :param dataset_name: 数据集名称
    :return: 生成器（流式返回讲解内容）
    """
    # 生成提示词
    prompt = get_paper_explain_prompt(link, dataset_name)

    try:
        # 调用大模型（流式响应）
        stream = CLIENT.chat.completions.create(
            model="qwen3.6-plus",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=0.3,  # 低温度保证输出准确
            max_tokens=1500
        )

        # 流式返回内容
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield content  # 流式输出

        # 兜底：如果流式为空，返回基础讲解
        if not full_content:
            yield f"### 📑 论文基础信息\n- 论文链接：{link}\n- 关联数据集：{dataset_name}\n\n### 📝 论文核心讲解\n暂未获取到讲解内容，请检查API配置。"

    except Exception as e:
        # 异常处理：返回基础讲解 + 错误提示
        error_msg = f"""
        ### 📑 论文基础信息
        - 论文链接：{link}
        - 关联数据集：{dataset_name}

        ### 📝 论文核心讲解
        ❌ 调用大模型失败：{str(e)}
        请检查：
        1. API Key 是否正确；
        2. autodl 服务是否正常；
        3. 网络是否能访问 https://www.autodl.art/api/v1。
        """
        yield error_msg


# 测试：本地运行验证
if __name__ == "__main__":
    test_link = "https://www.sciencedirect.com/science/article/pii/S0924271625003405"
    print("正在生成论文讲解...\n")
    for content in explain_paper_by_link(test_link, "OSVQA"):
        print(content, end="")