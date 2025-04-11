def calculate_rating_and_target(ability_type, age, current_score):
    # 根据能力类型和年龄设置标准
    if ability_type == "visual_breadth":
        if age < 7:
            standards = [("优秀", 0, 179),
                         ("合格", 180, 240),
                         ("不合格", 241, 360),
                         ("极差", 361, float("inf"))]
        else:
            standards = [("优秀", 0, 119),
                         ("合格", 120, 180),
                         ("不合格", 181, 300),
                         ("极差", 301, float("inf"))]
    elif ability_type == "visual_discrimination":
        standards = [("优秀", 0, 2),
                     ("合格", 3, 4),
                     ("不合格", 5, 8),
                     ("极差", 9, float("inf"))]
    elif ability_type == "visuo_motor":
        age_standards = {
            4: [("极差", 0, 5), ("不合格", 6, 7), ("合格", 8, 10), ("优秀", 11, float("inf"))],
            5: [("极差", 0, 8), ("不合格", 9, 10), ("合格", 11, 13), ("优秀", 14, float("inf"))],
            6: [("极差", 0, 11), ("不合格", 12, 13), ("合格", 14, 15), ("优秀", 16, float("inf"))],
            7: [("极差", 0, 13), ("不合格", 14, 15), ("合格", 16, 17), ("优秀", 18, float("inf"))],
            8: [("极差", 0, 15), ("不合格", 16, 17), ("合格", 18, 19), ("优秀", 20, float("inf"))],
        }
        standards = age_standards.get(age, age_standards[8])  # 默认用8岁的标准
    elif ability_type == "visual_memory":
        standards = [("优秀", 4, 4),
                     ("合格", 3, 3),
                     ("不合格", 2, 2),
                     ("极差", 0, 1)]
    else:
        return "未知", current_score, "未知"

    # 查找当前得分的评级
    current_rating = "未知"
    for label, min_val, max_val in standards:
        if min_val <= current_score <= max_val:
            current_rating = label
            break

    # 设定目标评级：若当前评级为"极差"或"不合格"，目标为"合格"；若为"合格"，目标为"优秀"；若已优秀，则保持优秀
    if current_rating in ["极差", "不合格"]:
        target_rating = "合格"
    elif current_rating == "合格":
        target_rating = "优秀"
    else:
        target_rating = "优秀"  # 已经优秀则目标评级保持优秀

    # 设定目标评分
    # 先按默认逻辑取目标评级的下界
    target_score = next((min_val for label, min_val, max_val in standards if label == target_rating), current_score)

    # 对视觉广度做特殊处理：如果目标评级为优秀，则目标评分取该评级的上界（即最大允许时间）
    if ability_type == "visual_breadth" and target_rating == "优秀":
        for label, min_val, max_val in standards:
            if label == "优秀":
                # 如果上界为无限大则不做修改，否则取上界
                if max_val != float("inf"):
                    target_score = max_val
                break

    # 对视动统合做特殊处理：如果当前评级已经是优秀，则目标评分固定为27分
    if ability_type == "visuo_motor" and current_rating == "优秀":
        target_score = 27

    return current_rating, target_score, target_rating


if __name__ == "__main__":
    # 测试用例
    print("7岁, 视觉广度, 300秒:", calculate_rating_and_target("visual_breadth", 7, 300))  # ('不合格', 120, '合格')
    print("7岁, 视觉广度, 179秒:", calculate_rating_and_target("visual_breadth", 7, 179))  # ('优秀', 119, '优秀')
    print("6岁, 视觉广度, 188秒:", calculate_rating_and_target("visual_breadth", 6, 188))  # ('合格', 179, '优秀')
    print("7岁, 视动统合, 16分:", calculate_rating_and_target("visuo_motor", 7, 16))  # ('合格', 18, '优秀')
    print("6岁, 视动统合, 15分:", calculate_rating_and_target("visuo_motor", 6, 15))  # ('不合格', 16, '合格')
    print("7岁, 视动统合, 20分:", calculate_rating_and_target("visuo_motor", 7, 20))  # ('优秀', 27, '优秀')
    print("6岁, 视觉记忆, 2分:", calculate_rating_and_target("visual_memory", 6, 2))  # ('不合格', 3, '合格')


