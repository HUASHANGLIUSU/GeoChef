import re

# 本地 README.md 文件路径（和 main.py 同目录）
README_LOCAL_PATH = "README.md"

# 存储：数据集名称(小写) → 论文链接
name_to_paper = {}


def load_github_paper_links():
    global name_to_paper
    name_to_paper.clear()  # 清空旧数据

    try:
        # 读取本地 README.md 文件
        with open(README_LOCAL_PATH, "r", encoding="utf-8") as f:
            md_text = f.read()

        # ========== 你指定的核心正则 ==========
        pattern = r'\[(.*?)\]\((https?://.*?)\)'
        matches = re.findall(pattern, md_text, re.DOTALL | re.IGNORECASE)
        # =====================================

        # 过滤有效链接（仅保留学术相关）
        valid_count = 0
        for name, link in matches:
            clean_name = name.strip().lower()
            clean_link = link.strip()
            # 过滤条件：名称长度≥2 + 链接是学术相关
            if len(clean_name) >= 2 and any(
                    key in clean_link for key in ["arxiv", "sciencedirect", "ieee", "mdpi", "github", "cvf"]):
                name_to_paper[clean_name] = clean_link
                valid_count += 1

        print(f"✅ 离线解析完成 | 核心正则匹配到 {len(matches)} 条结果 | 有效学术链接 {valid_count} 个")

    except FileNotFoundError:
        print(f"❌ 未找到本地文件：{README_LOCAL_PATH} | 请确认文件路径正确")
        name_to_paper = {}
    except Exception as e:
        print(f"❌ 解析失败：{str(e)}")
        name_to_paper = {}


def get_paper_link_by_name(name):
    """模糊匹配：支持大小写/部分匹配"""
    if not name:
        return None
    target_name = name.strip().lower()
    # 宽松匹配：输入包含关键词 或 关键词包含输入
    for key in name_to_paper:
        if target_name in key or key in target_name:
            return name_to_paper[key]
    return None


# 测试验证（运行该文件时执行）
if __name__ == "__main__":
    load_github_paper_links()
    # 测试关键数据集
    test_list = ["osvqa", "geochat", "geoplan-bench", "SkyEyeGPT"]
    print("\n🔍 匹配测试：")
    for test_name in test_list:
        link = get_paper_link_by_name(test_name)
        print(f"   {test_name} → {link if link else '未匹配到'}")