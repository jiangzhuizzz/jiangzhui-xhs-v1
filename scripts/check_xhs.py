#!/usr/bin/env python3
"""
小红书文案检测脚本
功能：违禁词检测 + 敏感词替换 + 去AI味检测
规则来源：word_rules.json（统一规则）
"""

import re
import json
from pathlib import Path

# 规则文件路径
SCRIPT_DIR = Path(__file__).parent
RULES_FILE = SCRIPT_DIR / "word_rules.json"

# 加载规则
def load_rules():
    """从JSON文件加载规则"""
    if RULES_FILE.exists():
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

RULES = load_rules()

# 白名单（允许使用的词）
EXTREME_WHITELIST = ["最", "第一"]  # 口语化表达，如"最扎实"、"第一年"允许使用

# 词库
EXTREME_WORDS = RULES.get("extreme_words", {}).get("words", [])
SENSITIVE_WORDS = RULES.get("sensitive_words", {})
INDUCE_WORDS = RULES.get("induce_words", {}).get("words", [])
PROMISE_WORDS = RULES.get("promise_words", {}).get("words", [])
MEDICAL_WORDS = RULES.get("medical_words", {}).get("words", [])
FALSE_WORDS = RULES.get("false_words", {}).get("words", [])
AI_PATTERN_WORDS = RULES.get("ai_pattern_words", {}).get("words", [])
FORMAL_WORDS = RULES.get("formal_words", {}).get("words", [])
REPEAT_WORDS = RULES.get("repeat_words", {}).get("words", [])

# ============ 检测函数 ============

def check_extreme_words(text):
    """检测极限词"""
    found = []
    for word in EXTREME_WORDS:
        if word in text:
            found.append(word)
    return [w for w in found if w not in EXTREME_WHITELIST]

def check_sensitive_words(text):
    """检测敏感词"""
    found = []
    for word in SENSITIVE_WORDS:
        if word in text:
            found.append(word)
    return found

def replace_sensitive_words(text):
    """替换敏感词"""
    result = text
    sorted_words = sorted(SENSITIVE_WORDS.items(), key=lambda x: len(x[0]), reverse=True)
    for old, new in sorted_words:
        if old in result:
            temp = result.replace(old, new)
            while re.search(r'(\w)\1{2,}', temp):
                temp = re.sub(r'(\w)\1{2,}', r'\1\1', temp)
            result = temp
    return result

def check_induce_words(text):
    """检测诱导词"""
    found = []
    for word in INDUCE_WORDS:
        if word in text:
            found.append(word)
    return found

def check_promise_words(text):
    """检测承诺词"""
    found = []
    for word in PROMISE_WORDS:
        if word in text:
            found.append(word)
    return found

def check_medical_words(text):
    """检测医疗健康词"""
    found = []
    for word in MEDICAL_WORDS:
        if word in text:
            found.append(word)
    return found

def check_false_words(text):
    """检测虚假宣传词"""
    found = []
    for word in FALSE_WORDS:
        if word in text:
            found.append(word)
    return found

def check_ai_pattern(text):
    """检测AI惯用词（去AI化）"""
    found = []
    for word in AI_PATTERN_WORDS:
        if word in text:
            found.append(word)
    return found

def check_formal_words(text):
    """检测书面用语（去AI化）"""
    found = []
    for word in FORMAL_WORDS:
        if word in text:
            found.append(word)
    return found

def check_repeat_words(text):
    """检测重复词（去AI化）"""
    found = []
    for word in REPEAT_WORDS:
        if word in text:
            found.append(word)
    return found

def check_emoji(text):
    """检测是否有emoji"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))

def check_sentence_length(text):
    """检测句子长度"""
    sentences = text.replace('\n', '.').split('.')
    long_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return long_sentences

def check_interaction(text):
    """检测是否有互动引导"""
    interaction_patterns = [
        r"你们.*\?",
        r"大家.*\?",
        r"有没有.*\?",
        r"评论.*",
        r"点赞.*",
        r"收藏.*",
        r"扣\d+",
    ]
    for pattern in interaction_patterns:
        if re.search(pattern, text):
            return True
    return False

def check_spelling_errors(text):
    """检测可能的错别字（简单检测）"""
    # 常见错别字
    common_errors = {
        "的地得": "的/地/得",
        "在那": "在哪",
    }
    found = []
    for error in common_errors.keys():
        if error in text:
            found.append(error)
    return found

# ============ 主检测函数 ============

def check_content(text, auto_fix=False):
    """检测文案内容"""
    issues = []

    # 1. 极限词检测
    extreme = check_extreme_words(text)
    if extreme:
        issues.append({
            "type": "极限词",
            "found": extreme,
            "action": "替换",
            "category": "违禁词"
        })

    # 2. 敏感词检测
    sensitive = check_sensitive_words(text)
    if sensitive:
        issues.append({
            "type": "敏感词",
            "found": sensitive,
            "action": "替换",
            "category": "违禁词"
        })

    # 3. 诱导词检测
    induce = check_induce_words(text)
    if induce:
        issues.append({
            "type": "诱导词",
            "found": induce,
            "action": "删除",
            "category": "违禁词"
        })

    # 4. 承诺词检测
    promise = check_promise_words(text)
    if promise:
        issues.append({
            "type": "承诺词",
            "found": promise,
            "action": "删除",
            "category": "违禁词"
        })

    # 5. 医疗词检测
    medical = check_medical_words(text)
    if medical:
        issues.append({
            "type": "医疗词",
            "found": medical,
            "action": "注意",
            "category": "违禁词"
        })

    # 6. 虚假宣传词检测
    false = check_false_words(text)
    if false:
        issues.append({
            "type": "虚假宣传词",
            "found": false,
            "action": "注意",
            "category": "违禁词"
        })

    # 7. AI惯用词检测（去AI化）
    ai_pattern = check_ai_pattern(text)
    if ai_pattern:
        issues.append({
            "type": "AI惯用词",
            "found": ai_pattern,
            "action": "重写",
            "category": "去AI化"
        })

    # 8. 书面用语检测（去AI化）
    formal = check_formal_words(text)
    if formal:
        issues.append({
            "type": "书面用语",
            "found": formal,
            "action": "改为口语",
            "category": "去AI化"
        })

    # 9. 重复词检测（去AI化）
    repeat = check_repeat_words(text)
    if repeat:
        issues.append({
            "type": "重复词",
            "found": repeat,
            "action": "减少使用",
            "category": "去AI化"
        })

    # 10. Emoji检测
    has_emoji = check_emoji(text)
    if not has_emoji:
        issues.append({
            "type": "缺少Emoji",
            "found": [],
            "action": "补充",
            "category": "格式"
        })

    # 11. 句子长度检测
    long_sentences = check_sentence_length(text)
    if long_sentences:
        issues.append({
            "type": "长句",
            "found": long_sentences[:3],
            "action": "断句",
            "category": "格式"
        })

    # 12. 互动引导检测
    has_interaction = check_interaction(text)
    if not has_interaction:
        issues.append({
            "type": "缺少互动",
            "found": [],
            "action": "补充",
            "category": "格式"
        })

    # 自动修复
    if auto_fix and issues:
        text = auto_fix_content(text)

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "fixed_text": text if auto_fix else None
    }

def auto_fix_content(text):
    """自动修复文案"""
    # 1. 替换敏感词
    text = replace_sensitive_words(text)

    # 2. 替换AI惯用词
    for word in AI_PATTERN_WORDS:
        if word in text:
            text = text.replace(word, "")

    # 3. 替换书面用语
    for word in FORMAL_WORDS:
        if word in text:
            text = text.replace(word, "其实")

    # 4. 删除诱导词
    for word in INDUCE_WORDS:
        text = text.replace(word, "")

    # 5. 删除承诺词
    for word in PROMISE_WORDS:
        text = text.replace(word, "")

    # 6. 添加Emoji（如果没有）
    if not check_emoji(text):
        text = "💡 " + text

    # 7. 断句（长句分段）
    sentences = text.split('。')
    new_sentences = []
    for s in sentences:
        if len(s) > 20 and '，' not in s:
            mid = len(s) // 2
            s = s[:mid] + '，' + s[mid:]
        new_sentences.append(s)
    text = '。'.join(new_sentences)

    # 8. 添加互动引导（如果没有）
    if not check_interaction(text):
        text = text.strip() + "\n\n你们有遇到过这种情况吗？评论区聊聊~"

    return text

# ============ 命令行接口 ============

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="小红书文案检测")
    parser.add_argument("-t", "--text", help="待检测文案")
    parser.add_argument("-f", "--file", help="待检测文件")
    parser.add_argument("--auto-fix", action="store_true", help="自动修复")
    parser.add_argument("--show-rules", action="store_true", help="显示当前规则")
    parser.add_argument("--category", choices=["违禁词", "去AI化", "格式", "all"], default="all", help="按类别检测")

    args = parser.parse_args()

    if args.show_rules:
        print("=== 当前规则 ===")
        print(f"极限词: {len(EXTREME_WORDS)}个")
        print(f"敏感词: {len(SENSITIVE_WORDS)}个")
        print(f"诱导词: {len(INDUCE_WORDS)}个")
        print(f"承诺词: {len(PROMISE_WORDS)}个")
        print(f"医疗词: {len(MEDICAL_WORDS)}个")
        print(f"虚假词: {len(FALSE_WORDS)}个")
        print(f"AI惯用词: {len(AI_PATTERN_WORDS)}个")
        print(f"书面用语: {len(FORMAL_WORDS)}个")
        print(f"重复词: {len(REPEAT_WORDS)}个")
        print(f"\n规则文件: {RULES_FILE}")
        exit(0)

    # 获取待检测文本
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        file_path = Path(args.file)
        if file_path.exists():
            text = file_path.read_text(encoding='utf-8')
        else:
            print(f"文件不存在: {args.file}")
            exit(1)
    else:
        print("请输入待检测文案 -t '文案内容' 或 -f 文件路径")
        exit(1)

    # 检测
    result = check_content(text, auto_fix=args.auto_fix)

    # 按类别筛选输出
    if args.category != "all":
        result["issues"] = [i for i in result["issues"] if i["category"] == args.category]

    # 输出结果
    if result["passed"] or not result["issues"]:
        print("✅ 检测通过")
    else:
        print("❌ 检测未通过\n")

        # 按类别分组输出
        categories = {}
        for issue in result["issues"]:
            cat = issue.get("category", "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)

        for cat, items in categories.items():
            print(f"--- {cat} ---")
            for issue in items:
                print(f"【{issue['type']}】")
                found = ', '.join(map(str, issue['found'][:5]))
                if found:
                    print(f"  发现: {found}")
                print(f"  处理: {issue['action']}")
            print()

    if args.auto_fix and result["fixed_text"]:
        print("=== 修复后文案 ===")
        print(result["fixed_text"])
