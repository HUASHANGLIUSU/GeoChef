import pandas as pd
import random
import json
import re

MODAL_KEYWORDS = {
    "SAR": {"sar", "sentinel-1", "sentinel1", "雷达"},
    "Optical (RGB)": {"rgb", "optical", "光学", "可见光"},
    "Multispectral": {"msi", "sentinel-2", "sentinel2", "landsat", "多光谱"},
    "Hyperspectral": {"hsi", "高光谱"},
    "LiDAR": {"lidar", "激光雷达"},
}

TASK_LIST = ["VQA", "Caption", "VG", "Classification", "Detection", "Segmentation"]


class GeoChef:
    def __init__(self):
        self.data = []
        self.years = []
        self.publishers = []
        self.methods = []
        self.modalities = list(MODAL_KEYWORDS.keys())
        self.tasks = TASK_LIST

    def load(self, path="rs_vlm_datasets.xlsx"):
        sheets = ["VQA", "Cap", "Caption", "VG", "Comprehensive Data", "Comprehensive benchmark",
                  "统计期刊数量、国家数量、年份"]
        items = []
        publishers = set()
        methods = set()
        years = set()

        for sheet in sheets:
            try:
                df = pd.read_excel(path, sheet_name=sheet)
                for _, row in df.iterrows():
                    item = row.dropna().to_dict()
                    item["_sheet"] = sheet
                    item["_text"] = json.dumps(item, ensure_ascii=False).lower()
                    item["_years"] = set(re.findall(r'\b(199\d|20[0-2]\d)\b', item["_text"]))
                    items.append(item)

                    p = str(item.get("Publisher", item.get("publisher", ""))).strip()
                    if p and len(p) > 1:
                        publishers.add(p)

                    m = str(item.get("Method", item.get("method", ""))).strip()
                    if m and len(m) > 1:
                        methods.add(m)

                    years.update(item["_years"])
            except:
                continue

        self.data = items
        self.years = sorted(list(years))
        self.publishers = sorted(list(publishers))
        self.methods = sorted(list(methods))

    def check_modal(self, item_words, modals):
        if not modals: return True
        for m in modals:
            if MODAL_KEYWORDS[m] & item_words: return True
        return False

    def check_task(self, text, tasks):
        if not tasks: return True
        return any(t.lower() in text for t in tasks)

    def check_year(self, item_years, years):
        if not years: return True
        return bool(set(years) & item_years)

    def check_publisher(self, item, selected):
        if not selected: return True
        val = str(item.get("Publisher", item.get("publisher", ""))).strip()
        return val in selected

    def check_method(self, item, selected):
        if not selected: return True
        val = str(item.get("Method", item.get("method", ""))).strip()
        return val in selected

    def check_keywords(self, text, kws):
        if not kws: return True
        return all(kw.lower() in text for kw in kws)

    def filter(self, modals, tasks, years, publishers, methods, kws):
        res = []
        for item in self.data:
            item_words = set(re.findall(r"\w+", item["_text"]))
            if (self.check_modal(item_words, modals) and
                    self.check_task(item["_text"], tasks) and
                    self.check_year(item["_years"], years) and
                    self.check_publisher(item, publishers) and
                    self.check_method(item, methods) and
                    self.check_keywords(item["_text"], kws)):
                res.append(item)
        return res

    def random_one(self):
        return random.choice(self.data) if self.data else None

    def extract_original_datasets(self, item):
        """解析单个数据项中的原始数据集（支持多格式分隔）"""
        # 可能的字段名（中英文/大小写）
        original_fields = ["原始数据集", "Original Dataset", "Source Dataset", "数据源", "source", "原始数据"]
        original_text = ""
        for field in original_fields:
            val = item.get(field, item.get(field.lower(), ""))
            if val and str(val).strip():
                original_text = str(val).strip()
                break

        # 解析分隔符（逗号/分号/空格/换行）
        if not original_text:
            return set()

        # 正则分割各种分隔符
        original_list = re.split(r'[,;，；\n\s]+', original_text)
        # 清洗空值和短字符串
        original_set = set([x.strip().lower() for x in original_list if x.strip() and len(x.strip()) >= 2])
        return original_set

    def detect_leakage_risk(self, train_dataset_name):
        """
        检测数据泄露风险：
        - train_dataset_name: 训练集数据集名称（模糊匹配）
        - 返回：(训练集原始数据集, 有泄露风险的测试集列表)
        """
        # 1. 查找训练集数据项（模糊匹配）
        train_item = None
        train_originals = set()
        target_name = train_dataset_name.strip().lower()

        for item in self.data:
            # 匹配数据集名称字段
            item_name = str(item.get("Name", item.get("name", item.get("_sheet", "")))).strip().lower()
            if target_name in item_name or item_name in target_name:
                train_item = item
                train_originals = self.extract_original_datasets(item)
                break

        if not train_item or not train_originals:
            return train_originals, []

        # 2. 筛选有泄露风险的测试集（共享原始数据集）
        risk_items = []
        for item in self.data:
            # 跳过自身
            if item == train_item:
                continue

            # 提取当前项的原始数据集
            item_originals = self.extract_original_datasets(item)
            # 有交集则判定为有泄露风险
            if train_originals & item_originals:
                # 补充泄露的原始数据集信息
                leak_originals = train_originals & item_originals
                item["_leak_originals"] = leak_originals
                risk_items.append(item)

        return train_originals, risk_items