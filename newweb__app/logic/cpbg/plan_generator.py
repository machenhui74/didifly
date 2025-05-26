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
def generate_plan(child_name, child_age, child_ratings, source_folder, destination_folder, weeks=1):
    # 过滤输入，只保留视觉相关的能力评估
    visual_ratings = {k: v for k, v in child_ratings.items() if k in categories}
    
    # 计算总课程数量（12节课 × weeks)
    total_courses = 12 * weeks
    # 计算每节课7题，总共需要的题目数
    total_needed = total_courses * 7
    
    # 当没有视觉能力评估时提醒用户
    if not visual_ratings:
        print("警告：没有可用的视觉能力评估结果。请确保至少提供一项视觉相关的能力评估。")
        return
    
    # 计算目标难度：公式 "L" + str(child_age + offset - 3)
    # 对于4-5周岁且能力"极差"或"不合格"的小朋友，固定使用L1难度
    target_difficulties = {}
    for cat, rating in visual_ratings.items():
        if (child_age in [4, 5]) and (rating in ["极差", "不合格"]):
            target_difficulties[cat] = "L1"
        else:
            # 计算难度值，确保至少为1（不小于L1）
            difficulty_value = max(1, child_age + rating_to_offset[rating] - 3)
            target_difficulties[cat] = f"L{difficulty_value}"
    
    # 计算权重
    weights = calculate_weights(visual_ratings)
    # 构建文件索引
    files_index = build_file_index(source_folder)
    # 按比例分配题目数量
    required = {cat: int(round(total_needed * weights[cat])) for cat in visual_ratings}
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
    for cat in visual_ratings:
        need = required[cat]
        diff_label = target_difficulties[cat]
        pool = files_index.get(cat, {}).get(diff_label, [])
        if not pool:
            print(f"警告：项目[{cat}]难度[{diff_label}] 没有可用文件。")
            continue
        picks = random.choices(pool, k=need) if len(pool) < need else random.sample(pool, k=need)
        selected_files.extend(picks)
    # 如果抽取的文件不足，则从所有候选文件中补足
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
    # 分组：打乱后按每组7题分为total_courses组，不足时随机补齐
    random.shuffle(selected_files)
    group_size = 7
    course_names = [f"第{i}次课" for i in range(1, total_courses + 1)]
    groups = [selected_files[i*group_size:(i+1)*group_size] for i in range(total_courses)]
    for group in groups:
        while len(group) < group_size:
            group.append(random.choice(selected_files))
    # 在目标文件夹下自动生成以小朋友名字命名的子文件夹，然后生成课程的子文件夹
    folder_name = f"{child_name}—{total_courses}节课视觉训练"
    destination_base = os.path.join(destination_folder, folder_name)
    os.makedirs(destination_base, exist_ok=True)
    for course_name, group in zip(course_names, groups):
        course_folder = os.path.join(destination_base, course_name)
        os.makedirs(course_folder, exist_ok=True)
        for fname in group:
            src = os.path.join(source_folder, fname)
            dst = os.path.join(course_folder, fname)
            shutil.copy(src, dst)
            print(f"复制 {fname} 到 {course_folder}")
    print(f"方案生成完成！共{total_courses}节课。")
    return folder_name

# 直接使用用户选择的难度级别生成训练方案（无测评版本）
def generate_direct_plan(child_name, child_age, child_ratings, target_difficulties, source_folder, destination_folder, weeks=1):
    """
    根据用户直接选择的难度级别生成训练方案
    
    参数:
    - child_name: 小朋友姓名
    - child_age: 小朋友年龄
    - child_ratings: 小朋友视觉能力评级（这里只是为了兼容性）
    - target_difficulties: 用户选择的难度级别，格式为 {"visual_breadth": "L1", ...}
    - source_folder: 训练文件源目录
    - destination_folder: 输出目录
    - weeks: 训练周数（每周12节课）
    
    返回:
    - 生成的文件夹名称
    """
    # 过滤输入，只保留视觉相关的能力评估
    visual_ratings = {k: v for k, v in child_ratings.items() if k in categories}
    
    # 计算总课程数量（12节课 × weeks)
    total_courses = 12 * weeks
    # 计算每节课7题，总共需要的题目数
    total_needed = total_courses * 7
    
    # 当没有视觉能力评估时提醒用户
    if not visual_ratings:
        print("警告：没有可用的视觉能力评估结果。请确保至少提供一项视觉相关的能力评估。")
        return
    
    # 使用用户直接选择的难度级别
    # 计算权重 - 这里简化为平均分配
    weights = {cat: 1.0 / len(visual_ratings) for cat in visual_ratings}
    
    # 构建文件索引
    files_index = build_file_index(source_folder)
    
    # 按比例分配题目数量
    required = {cat: int(round(total_needed * weights[cat])) for cat in visual_ratings}
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
    for cat in visual_ratings:
        need = required[cat]
        diff_label = target_difficulties[cat]
        pool = files_index.get(cat, {}).get(diff_label, [])
        if not pool:
            print(f"警告：项目[{cat}]难度[{diff_label}] 没有可用文件。")
            continue
        picks = random.choices(pool, k=need) if len(pool) < need else random.sample(pool, k=need)
        selected_files.extend(picks)
    
    # 如果抽取的文件不足，则从所有候选文件中补足
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
    
    # 分组：打乱后按每组7题分为total_courses组，不足时随机补齐
    random.shuffle(selected_files)
    group_size = 7
    course_names = [f"第{i}次课" for i in range(1, total_courses + 1)]
    groups = [selected_files[i*group_size:(i+1)*group_size] for i in range(total_courses)]
    for group in groups:
        while len(group) < group_size:
            group.append(random.choice(selected_files))
    
    # 在目标文件夹下自动生成以小朋友名字命名的子文件夹，然后生成课程的子文件夹
    folder_name = f"{child_name}—{total_courses}节课视觉训练"
    destination_base = os.path.join(destination_folder, folder_name)
    os.makedirs(destination_base, exist_ok=True)
    for course_name, group in zip(course_names, groups):
        course_folder = os.path.join(destination_base, course_name)
        os.makedirs(course_folder, exist_ok=True)
        for fname in group:
            src = os.path.join(source_folder, fname)
            dst = os.path.join(course_folder, fname)
            shutil.copy(src, dst)
            print(f"复制 {fname} 到 {course_folder}")
    
    print(f"方案生成完成！共{total_courses}节课。")
    return folder_name 