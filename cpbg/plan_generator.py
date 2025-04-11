# plan_generator.py
# 这是根据输入能力水平选取合适文件打包成12节课内容的程序
import os
import re
import random
import shutil

# 定义训练项目关键词（内部键 → 文件中显示的中文关键词）
categories = {
    "visual_breadth": "视觉广度",
    "visual_memory": "视觉记忆",
    "visual_discrimination": "视觉分辨",
    "visuo_motor": "视动统合"
}

# 解析文件名：提取难度标签（L1～L9）以及所属训练项目
def parse_file(filename):
    base = os.path.splitext(filename)[0]
    m = re.search(r"[lL]\s*([1-9])", base)
    if not m:
        return []
    difficulty = "L" + m.group(1)
    found = []
    for cat_key, cat_kw in categories.items():
        if cat_kw in base:
            found.append((cat_key, difficulty))
    return found

# 构建文件索引：按"类别+难度"组织所有文件
def build_file_index(source_folder):
    index = {cat: {} for cat in categories}
    for f in os.listdir(source_folder):
        for (cat, diff) in parse_file(f):
            index[cat].setdefault(diff, []).append(f)
    return index

# 能力评价映射（目标难度与权重计算）
rating_to_offset = {
    "极差": -2,
    "不合格": -1,
    "合格": 0,
    "优秀": 1
}
rating_to_rank = {
    "极差": 1,
    "不合格": 2,
    "合格": 3,
    "优秀": 4
}

# 根据评价计算归一化权重（薄弱项权重较高）
def calculate_weights(child_ratings):
    raw = {ability: 5 - rating_to_rank[rating] for ability, rating in child_ratings.items()}
    total = sum(raw.values())
    return {ability: raw[ability] / total for ability in raw}

# 生成训练方案的核心函数
def generate_plan(child_name, child_age, child_ratings, source_folder, destination_folder):
    # 计算目标难度：公式 "L" + str(child_age + offset - 3)
    target_difficulties = {cat: f"L{child_age + rating_to_offset[rating] - 3}"
                           for cat, rating in child_ratings.items()}
    # 计算权重
    weights = calculate_weights(child_ratings)
    # 构建文件索引
    files_index = build_file_index(source_folder)
    # 按比例分配题目数量（总共12节课×7题=84题）
    total_needed = 12 * 7
    required = {cat: int(round(total_needed * weights[cat])) for cat in child_ratings}
    diff = total_needed - sum(required.values())
    while diff:
        if diff > 0:
            cat_max = max(weights, key=weights.get)
            required[cat_max] += 1
            diff -= 1
        else:
            cat_max = max(required, key=required.get)
            if required[cat_max] > 0:
                required[cat_max] -= 1
                diff += 1
            else:
                break
    # 从目标难度中抽取文件（不足时允许重复抽取）
    selected_files = []
    for cat in child_ratings:
        need = required[cat]
        diff_label = target_difficulties[cat]
        pool = files_index.get(cat, {}).get(diff_label, [])
        if not pool:
            print(f"警告：项目[{cat}]难度[{diff_label}] 没有可用文件。")
            continue
        picks = random.choices(pool, k=need) if len(pool) < need else random.sample(pool, k=need)
        selected_files.extend(picks)
    # 如果抽取的文件不足，则从所有候选文件中补足到84个
    if len(selected_files) < total_needed:
        remain = total_needed - len(selected_files)
        all_candidates = []
        for cat in files_index:
            for diff_label in files_index[cat]:
                all_candidates.extend(files_index[cat][diff_label])
        if not all_candidates:
            raise Exception("错误：没有任何可用文件，请检查文件命名格式！")
        selected_files.extend(random.choices(all_candidates, k=remain))
    selected_files = selected_files[:total_needed]
    # 分组：打乱后按每组7题分为12组，不足时随机补齐
    random.shuffle(selected_files)
    group_size = 7
    course_names = [f"第{i}次课" for i in range(1, 13)]
    groups = [selected_files[i*group_size:(i+1)*group_size] for i in range(12)]
    for group in groups:
        while len(group) < group_size:
            group.append(random.choice(selected_files))
    # 在目标文件夹下自动生成以小朋友名字命名的子文件夹，然后生成12节课的子文件夹
    destination_base = os.path.join(destination_folder, f"{child_name}—12节课视觉训练")
    os.makedirs(destination_base, exist_ok=True)
    for course_name, group in zip(course_names, groups):
        course_folder = os.path.join(destination_base, course_name)
        os.makedirs(course_folder, exist_ok=True)
        for fname in group:
            src = os.path.join(source_folder, fname)
            dst = os.path.join(course_folder, fname)
            shutil.copy(src, dst)
            print(f"复制 {fname} 到 {course_folder}")
    print("方案生成完成！")
