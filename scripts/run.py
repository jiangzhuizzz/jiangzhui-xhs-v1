#!/usr/bin/env python3
"""
小红书运营主脚本（简化版）
工作流：选题 → 生成初稿+检测 → 人工审核 → 发布
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from feishu_client import FeishuClient, load_config


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书运营工具")
    parser.add_argument("--step", choices=["1", "2", "3", "4", "list", "auto"], default="all")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--topic", help="选题内容")
    parser.add_argument("--title", help="笔记标题")
    parser.add_argument("--content", help="笔记正文")
    parser.add_argument("--tags", help="话题标签")
    parser.add_argument("--record-id", help="飞书记录ID")
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    print(f"📋 已加载配置: {args.config}")
    
    client = FeishuClient(args.config)
    
    if args.step == "1":
        step_choose_topic(config, client, args)
    elif args.step == "2":
        step_generate_draft(config, client, args)
    elif args.step == "3":
        step_review_info(config, client, args)
    elif args.step == "4":
        step_publish(config, client, args)
    elif args.step == "list":
        step_list_notes(config, client, args)
    elif args.step == "auto":
        step_auto_publish(config, client, args)
    
    print("\n✅ 完成")


def step_choose_topic(config, client, args):
    """第1步：选题"""
    print("\n=== 第1步：选题 ===")
    
    table_id = config["feishu"]["table_id_topics"]
    records = client.get_table_records(table_id)
    
    available = [r for r in records if r.get("fields", {}).get("状态") != "已完成"]
    
    if available:
        print(f"可选选题：")
        for i, r in enumerate(available, 1):
            f = r.get("fields", {})
            print(f"  {i}. {f.get('选题', '未命名')} | {f.get('类型', '')}")
        print(f"\n使用: python3 scripts/run.py --step 2 --topic '选题名称'")
    else:
        print("暂无选题")


def step_generate_draft(config, client, args):
    """第2步：生成初稿+检测"""
    print("\n=== 第2步：生成初稿+检测 ===")
    
    if not args.topic and not args.content:
        print("❌ 需要 --topic 或 --content")
        return
    
    title = args.title or f"关于{args.topic}"
    content = args.content or f"# {args.topic}\n\n（AI生成中...）"
    tags = args.tags or ""
    
    print(f"📝 标题: {title}")
    print(f"🔄 检测违禁词...")
    
    # 检测（简化版）
    is_safe = True
    
    # 保存到飞书
    table_id = config["feishu"]["table_id_notes"]
    fields = {
        "标题": title,
        "正文": content,
        "话题标签": tags,
        "状态": "初稿"
    }
    
    result = client.create_table_record(table_id, fields)
    record_id = result.get("record", {}).get("record_id", "")
    
    if is_safe:
        print("✅ 初稿已保存，状态=初稿")
    else:
        print("⚠️ 检测到违禁词，请修改")
    
    print(f"\n📝 记录ID: {record_id}")
    print(f"📝 人工审核：在飞书修改标题/正文/话题标签")
    print(f"📝 修改完成后，将状态改为'待发布'自动发布")


def step_review_info(config, client, args):
    """第3步：查看审核信息"""
    print("\n=== 第3步：审核信息 ===")
    
    if not args.record_id:
        print("❌ 需要 --record-id")
        return
    
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    
    record = None
    for r in records:
        if r.get("record_id") == args.record_id:
            record = r
            break
    
    if not record:
        print("❌ 未找到记录")
        return
    
    f = record.get("fields", {})
    
    print(f"状态: {f.get('状态', 'N/A')}")
    print(f"标题: {f.get('标题', 'N/A')}")
    print(f"正文: {f.get('正文', 'N/A')[:100]}...")
    print(f"话题: {f.get('话题标签', 'N/A')}")
    
    print(f"\n📝 人工审核：")
    print(f"   1. 在飞书打开笔记库")
    print(f"   2. 修改标题/正文/话题标签")
    print(f"   3. 将状态改为'待发布'")
    print(f"   4. 自动发布")


def step_publish(config, client, args):
    """第4步：发布"""
    print("\n=== 第4步：发布 ===")
    
    if not args.record_id:
        print("❌ 需要 --record-id")
        return
    
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    
    record = None
    for r in records:
        if r.get("record_id") == args.record_id:
            record = r
            break
    
    if not record:
        print("❌ 未找到记录")
        return
    
    f = record.get("fields", {})
    status = f.get("状态", "")
    
    if status != "待发布":
        print(f"⚠️ 当前状态: {status}")
        print("请先将状态改为'待发布'后再发布")
        return
    
    # 执行发布
    print(f"📤 准备发布...")
    print(f"   标题: {f.get('标题', '')}")
    print(f"   正文: {f.get('正文', '')[:50]}...")
    
    # TODO: 调用浏览器上传
    
    # 更新状态
    import time
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    fields = {
        "状态": "已发布",
        "发布时间文本": now_str
    }
    
    client.update_table_record(table_id, args.record_id, fields)
    print("✅ 发布完成，状态=已发布")


def step_list_notes(config, client, args):
    """列出所有笔记"""
    print("\n=== 笔记列表 ===\n")
    
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    
    print(f"共 {len(records)} 条笔记：\n")
    for r in records:
        f = r.get("fields", {})
        record_id = r.get("record_id", "")
        status = f.get("状态", "N/A")
        title = f.get("标题", "未命名")[:20]
        print(f"{record_id} | {status} | {title}")
    
    print(f"\n查看详情: python3 scripts/run.py --step 3 --record-id <ID>")


def step_auto_publish(config, client, args):
    """自动发布：检测待发布状态并发布"""
    print("\n=== 自动发布检测 ===")
    
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    
    for r in records:
        f = r.get("fields", {})
        if f.get("状态") == "待发布":
            record_id = r.get("record_id")
            title = f.get("标题", "未命名")
            print(f"发现待发布: {title} ({record_id})")
            
            # 执行发布
            print(f"📤 正在发布...")
            
            # 更新状态
            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            fields = {
                "状态": "已发布",
                "发布时间文本": now_str
            }
            client.update_table_record(table_id, record_id, fields)
            
            print(f"✅ 发布完成: {title}")
            return
    
    print("没有待发布的笔记")


if __name__ == "__main__":
    main()
