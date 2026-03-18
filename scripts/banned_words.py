#!/usr/bin/env python3
"""
小红书违禁词检测模块
包含多个类别的违禁词，支持严重等级分类
"""

import re
from typing import List, Dict, Tuple


# ==================== 违禁词库 ====================

# 高危违禁词（直接拒绝）
HIGH_RISK_WORDS = [
    # 引导私信/站外交易
    "互粉", "互关", "私信", "加微信", "加V", "加vx", "加wx", "➕V", "➕微",
    "找我", "联系我", "扫码", "二维码", "QQ", "企鹅号",
    
    # 承诺类
    "包下款", "100%", "百分百", "保证下款", "必过", "秒批", "秒下",
    "无条件", "零门槛", "不看征信", "黑户", "白户必过",
    
    # 违规金融
    "套现", "TX", "提额", "养卡", "代还", "代办", "包装资料",
    "假流水", "假征信", "洗白征信",
    
    # 色情低俗
    "约炮", "一夜情", "援交", "包养", "小姐", "嫖娼",
    
    # 政治敏感
    "习近平", "共产党", "民主", "自由", "人权", "六四", "法轮功",
    
    # 赌博诈骗
    "赌博", "博彩", "六合彩", "时时彩", "网赚", "刷单", "兼职打字",
]

# 中危违禁词（警告，建议修改）
MEDIUM_RISK_WORDS = [
    # 营销引导
    "点赞", "关注", "收藏", "转发", "评论", "留言", "置顶",
    "第一条", "看我主页", "看我简介", "戳我头像",
    
    # 金融敏感
    "贷款中介", "中介", "贷款公司", "金融公司", "担保公司",
    "利息", "利率", "年化", "月息", "日息", "手续费", "服务费",
    "征信", "逾期", "黑名单", "网贷", "小贷", "现金贷",
    
    # 夸大宣传
    "最好", "第一", "唯一", "顶级", "极品", "史上最强",
    "全网最低", "全城最低", "独家", "限时", "仅此一次",
    
    # 医疗健康
    "治疗", "治愈", "根治", "疗效", "药品", "保健品",
    
    # 其他敏感
    "翻墙", "VPN", "代理", "科学上网",
]

# 低危违禁词（提示，可酌情使用）
LOW_RISK_WORDS = [
    # 轻度营销
    "推荐", "分享", "安利", "种草", "拔草",
    
    # 金融相关（需要包装）
    "贷款", "借钱", "借款", "融资", "资金周转",
    "信用卡", "信贷", "抵押", "担保",
    
    # 可能引起误解
    "免费", "赠送", "福利", "优惠", "折扣",
]

# 行业特定违禁词（贷款中介）
LOAN_INDUSTRY_WORDS = [
    # 直接暴露身份
    "贷款中介", "金融中介", "贷款经理", "信贷经理",
    "帮你贷款", "帮你办理", "代办贷款",
    
    # 违规操作
    "包装", "做流水", "做资料", "美化征信",
    "过桥", "垫资", "倒贷", "转贷",
    
    # 过度承诺
    "当天下款", "立即放款", "快速到账", "急速审批",
    "不成功不收费", "先下款后收费",
]

# 武汉本地敏感词（根据地域特点）
WUHAN_LOCAL_WORDS = [
    # 可能引起争议的表述
    # （暂时为空，根据实际情况添加）
]


# ==================== 检测函数 ====================

def check_banned_words(text: str) -> Dict:
    """
    检测文本中的违禁词
    
    Returns:
        {
            'safe': bool,           # 是否安全
            'risk_level': str,      # 风险等级: safe/low/medium/high
            'violations': List[Dict],  # 违规详情
            'suggestions': List[str]   # 修改建议
        }
    """
    violations = []
    
    # 检测高危词
    for word in HIGH_RISK_WORDS:
        if word in text:
            violations.append({
                'word': word,
                'level': 'high',
                'category': '高危违禁词',
                'action': '必须删除'
            })
    
    # 检测中危词
    for word in MEDIUM_RISK_WORDS:
        if word in text:
            violations.append({
                'word': word,
                'level': 'medium',
                'category': '中危敏感词',
                'action': '建议修改'
            })
    
    # 检测低危词
    for word in LOW_RISK_WORDS:
        if word in text:
            violations.append({
                'word': word,
                'level': 'low',
                'category': '低危提示词',
                'action': '可酌情使用'
            })
    
    # 检测行业特定词
    for word in LOAN_INDUSTRY_WORDS:
        if word in text:
            violations.append({
                'word': word,
                'level': 'high',
                'category': '行业违禁词',
                'action': '必须删除或包装'
            })
    
    # 判断风险等级
    if any(v['level'] == 'high' for v in violations):
        risk_level = 'high'
        safe = False
    elif any(v['level'] == 'medium' for v in violations):
        risk_level = 'medium'
        safe = False
    elif any(v['level'] == 'low' for v in violations):
        risk_level = 'low'
        safe = True  # 低危可以发布，但需注意
    else:
        risk_level = 'safe'
        safe = True
    
    # 生成修改建议
    suggestions = generate_suggestions(violations)
    
    return {
        'safe': safe,
        'risk_level': risk_level,
        'violations': violations,
        'suggestions': suggestions
    }


def generate_suggestions(violations: List[Dict]) -> List[str]:
    """根据违规情况生成修改建议"""
    suggestions = []
    
    # 高危词建议
    high_risk = [v for v in violations if v['level'] == 'high']
    if high_risk:
        suggestions.append("⚠️ 发现高危违禁词，必须删除或替换：")
        for v in high_risk:
            suggestions.append(f"  - '{v['word']}' → {get_replacement(v['word'])}")
    
    # 中危词建议
    medium_risk = [v for v in violations if v['level'] == 'medium']
    if medium_risk:
        suggestions.append("\n💡 发现敏感词，建议优化：")
        for v in medium_risk:
            suggestions.append(f"  - '{v['word']}' → {get_replacement(v['word'])}")
    
    # 低危词提示
    low_risk = [v for v in violations if v['level'] == 'low']
    if low_risk:
        suggestions.append("\nℹ️ 以下词汇需谨慎使用：")
        for v in low_risk:
            suggestions.append(f"  - '{v['word']}'")
    
    return suggestions


def get_replacement(word: str) -> str:
    """获取违禁词的替换建议"""
    replacements = {
        # 引导类
        "互粉": "一起成长",
        "私信": "评论区交流",
        "加微信": "留言讨论",
        "找我": "有需要可以了解",
        
        # 承诺类
        "包下款": "帮助申请",
        "100%": "大概率",
        "必过": "通过率高",
        "秒批": "审批快",
        
        # 金融类
        "贷款中介": "金融咨询师",
        "贷款": "资金周转方案",
        "利息": "成本",
        "征信": "信用记录",
        
        # 营销类
        "点赞": "喜欢的话可以支持一下",
        "关注": "感兴趣可以看看",
        "最好": "很不错",
        "第一": "领先",
    }
    
    return replacements.get(word, "请删除或用其他表述替换")


def highlight_violations(text: str, violations: List[Dict]) -> str:
    """在文本中高亮显示违规词汇"""
    highlighted = text
    
    for v in violations:
        word = v['word']
        level = v['level']
        
        # 根据等级使用不同标记
        if level == 'high':
            marker = f"【❌{word}❌】"
        elif level == 'medium':
            marker = f"【⚠️{word}⚠️】"
        else:
            marker = f"【ℹ️{word}ℹ️】"
        
        highlighted = highlighted.replace(word, marker)
    
    return highlighted


# ==================== 批量检测 ====================

def batch_check(texts: List[str]) -> List[Dict]:
    """批量检测多段文本"""
    results = []
    
    for i, text in enumerate(texts, 1):
        result = check_banned_words(text)
        result['index'] = i
        result['text_preview'] = text[:50] + '...' if len(text) > 50 else text
        results.append(result)
    
    return results


# ==================== 命令行工具 ====================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python banned_words.py <文本内容>")
        print("或者: python banned_words.py --test")
        sys.exit(1)
    
    if sys.argv[1] == '--test':
        # 测试用例
        test_cases = [
            "武汉过早推荐，热干面才8块钱！",
            "需要贷款的私信我，包下款！",
            "公积金贷款攻略分享，点赞收藏！",
            "贷款中介帮你办理，100%通过！",
        ]
        
        print("=" * 50)
        print("违禁词检测测试")
        print("=" * 50)
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n测试 {i}: {text}")
            result = check_banned_words(text)
            
            print(f"  风险等级: {result['risk_level']}")
            print(f"  是否安全: {'✅' if result['safe'] else '❌'}")
            
            if result['violations']:
                print(f"  违规词汇: {len(result['violations'])} 个")
                for v in result['violations']:
                    print(f"    - {v['word']} ({v['category']})")
            
            if result['suggestions']:
                print("  修改建议:")
                for s in result['suggestions']:
                    print(f"    {s}")
    
    else:
        # 检测用户输入的文本
        text = ' '.join(sys.argv[1:])
        result = check_banned_words(text)
        
        print("\n" + "=" * 50)
        print("违禁词检测结果")
        print("=" * 50)
        print(f"\n原文: {text}")
        print(f"\n风险等级: {result['risk_level']}")
        print(f"是否安全: {'✅ 可以发布' if result['safe'] else '❌ 需要修改'}")
        
        if result['violations']:
            print(f"\n发现 {len(result['violations'])} 个问题:")
            for v in result['violations']:
                print(f"  [{v['level'].upper()}] {v['word']} - {v['category']}")
        
        if result['suggestions']:
            print("\n修改建议:")
            for s in result['suggestions']:
                print(s)
        
        print("\n高亮显示:")
        print(highlight_violations(text, result['violations']))
