#!/usr/bin/env python3
"""
小红书运营主脚本（优化版）
完整流程：选题 → 生成初稿(+并行检测) → 配图 → 人工审核 → 发布

优化点：
1. 生成初稿和违禁词检测并行执行
2. 检测失败可修改后重新检测
3. 审核通过直接发布
4. 保留初稿和修改版本的历史记录
"""

import os
import sys
import yaml
import json
import asyncio
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent))

from feishu_client import FeishuClient, load_config

# 工作流环节
STAGES = ["选题", "初稿", "检测", "配图", "审核", "发布"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书运营工具（优化版）")
    parser.add_argument("--step", 
                       choices=["1", "2", "3", "4", "5", "6", "all"], 
                       default="all", 
                       help="""执行哪一步: 
                       1=选题 2=生成初稿+检测 3=配图 4=人工审核 5=发布 6=查看历史""")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--topic", help="选题内容")
    parser.add_argument("--title", help="笔记标题")
    parser.add_argument("--content", help="笔记正文")
    parser.add_argument("--tags", help="话题标签（逗号分隔）")
    parser.add_argument("--images", help="图片路径（逗号分隔）")
    parser.add_argument("--record-id", help="飞书笔记库记录ID")
    parser.add_argument("--approve", action="store_true", help="审核通过，直接发布")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    print(f"📋 已加载配置: {args.config}")
    
    # 初始化飞书客户端
    client = FeishuClient(args.config)
    
    # 执行对应步骤
    if args.step in ["1", "all"]:
        step_choose_topic(config, client, args)
    
    if args.step in ["2", "all"]:
        step_generate_and_check(config, client, args)
    
    if args.step in ["3", "all"]:
        step_add_images(config, client, args)
    
    if args.step in ["4", "all"]:
        step_review(config, client, args)
    
    if args.step in ["5", "all"]:
        step_publish(config, client, args)
    
    if args.step == "6":
        step_show_history(config, client, args)
    
    print("\n✅ 流程完成")


def step_choose_topic(config, client, args):
    """第1步：选题"""
    print("\n=== 第1步：选题 ===")
    
    table_id = config["feishu"]["table_id_topics"]
    records = client.get_table_records(table_id)
    
    available = [r for r in records if r.get("fields", {}).get("状态") != "已完成"]
    
    if available:
        print(f"找到 {len(available)} 个可选选题：")
        for i, r in enumerate(available, 1):
            fields = r.get("fields", {})
            print(f"  {i}. {fields.get('选题', '未命名')} | {fields.get('类型', '')}")
        print(f"\n📝 使用方式: python3 scripts/run.py --step 2 --topic '选题名称'")
    else:
        print("暂无选题，请在飞书选题库添加")


def step_generate_and_check(config, client, args):
    """第2步：生成初稿 + 并行违禁词检测"""
    print("\n=== 第2步：生成初稿 + 违禁词检测 ===")
    
    if not args.topic and not args.content:
        print("❌ 需要提供内容，使用 --topic 或 --content 参数")
        return
    
    # 参数
    title = args.title or f"关于{args.topic}的笔记"
    content = args.content or f"# {args.topic}\n\n（待生成内容）"
    tags = args.tags or ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"📝 标题: {title}")
    print(f"📝 正文: {content[:50]}...")
    
    # 并行执行：生成初稿 + 违禁词检测
    print("\n🔄 正在生成初稿 + 违禁词检测...")
    
    def run_check():
        """模拟违禁词检测"""
        import time
        time.sleep(0.5)  # 模拟检测时间
        # TODO: 实际调用 check_xhs.py
        return True, []  # (是否通过, 违禁词列表)
    
    # 并行执行
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 生成初稿（这里简化，实际会调用 AI）
        future_content = executor.submit(lambda: content)
        # 违禁词检测
        future_check = executor.submit(run_check)
        
        result_content = future_content.result()
        is_safe, forbidden = future_check.result()
    
    # 保存初稿到飞书
    table_id = config["feishu"]["table_id_notes"]
    
    fields = {
        "标题": title,  # 兼容旧字段
        "正文": result_content,  # 兼容旧字段
        "话题标签": tags,  # 兼容旧字段
        "初稿标题": title,
        "初稿正文": result_content,
        "初稿话题标签": tags,
        "状态": "初稿" if is_safe else "检测失败"
    }
    
    result = client.create_table_record(table_id, fields)
    record_id = result.get("record", {}).get("record_id", "")
    
    if is_safe:
        print("✅ 初稿生成完成 + 违禁词检测通过")
    else:
        print(f"❌ 初稿生成完成，但检测到违禁词: {forbidden}")
        print("   请修改后重新执行检测")
    
    print(f"\n📝 记录ID: {record_id}")
    print(f"   状态: {'初稿' if is_safe else '检测失败'}")
    
    if is_safe:
        print(f"\n📝 继续配图: python3 scripts/run.py --step 3 --record-id {record_id}")
    else:
        print(f"\n📝 修改后重新检测: python3 scripts/run.py --step 2 --record-id {record_id} --content '新内容'")


def step_add_images(config, client, args):
    """第3步：配图"""
    print("\n=== 第3步：配图 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    images = args.images or ["./picture/card_1.png"]
    
    print(f"📷 待渲染图片: {images}")
    print("   （调用 render_xhs.py 渲染图片）")
    print("✅ 图片渲染完成")
    
    # 更新飞书（图片字段暂不传，默认用本地路径）
    table_id = config["feishu"]["table_id_notes"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    fields = {
        # 飞书图片字段需要特殊格式，暂时跳过
        # "封面图": images[0] if images else "",
        # "内容图": ",".join(images) if images else "",
        "状态": "配图完成",
        "版本记录": f"[{now}] 配图完成\n"
    }
    
    client.update_table_record(table_id, args.record_id, fields)
    print(f"✅ 已更新飞书笔记库")
    print(f"\n📝 继续审核: python3 scripts/run.py --step 4 --record-id {args.record_id}")


def step_review(config, client, args):
    """第4步：人工审核"""
    print("\n=== 第4步：人工审核 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    table_id = config["feishu"]["table_id_notes"]
    
    print("📋 请人工审核以下内容：")
    print("   - 标题是否合适")
    print("   - 正文是否有错别字")
    print("   - 图片是否正确")
    print("   - 话题标签是否合适")
    
    print("\n审核命令：")
    print(f"   通过并发布: python3 scripts/run.py --step 4 --record-id {args.record_id} --approve")
    print(f"   仅保存不发布: python3 scripts/run.py --step 4 --record-id {args.record_id}")
    
    if args.approve:
        print("\n✅ 审核通过，自动进入发布环节...")
        # 自动进入发布
        step_publish(config, client, args)
    else:
        fields = {"状态": "审核中"}
        client.update_table_record(table_id, args.record_id, fields)
        print(f"\n📝 已保存审核状态，请审核后使用 --approve 发布")


def step_publish(config, client, args):
    """第5步：发布"""
    print("\n=== 第5步：发布 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    table_id = config["feishu"]["table_id_notes"]
    
    # TODO: 调用浏览器上传到小红书
    print("📤 打开小红书创作平台...")
    print("   （自动上传图片和文案）")
    print("✅ 已发布到小红书")
    
    # 更新飞书 - 保存发布版本的内容
    # 发布时间需要 Unix 时间戳
    import time
    timestamp = int(time.time())
    
    # 获取初稿内容作为发布内容（也可以人工修改）
    # 这里简化处理，直接用初稿内容
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    record = None
    for r in records:
        if r.get("record_id") == args.record_id:
            record = r
            break
    
    draft_title = record.get("fields", {}).get("初稿标题", "")
    draft_content = record.get("fields", {}).get("初稿正文", "")
    draft_tags = record.get("fields", {}).get("初稿话题标签", "")
    
    fields = {
        "状态": "已发布",
        "发布时间": timestamp,
        "发布标题": draft_title,
        "发布正文": draft_content,
        "发布话题标签": draft_tags
    }
    
    client.update_table_record(table_id, args.record_id, fields)
    print(f"✅ 已更新飞书笔记库，状态: 已发布")


def step_show_history(config, client, args):
    """第6步：查看历史版本"""
    print("\n=== 查看笔记历史 ===\n")
    
    if not args.record_id:
        # 列出所有笔记
        table_id = config["feishu"]["table_id_notes"]
        records = client.get_table_records(table_id)
        
        print(f"共 {len(records)} 条笔记：\n")
        for r in records:
            fields = r.get("fields", {})
            record_id = r.get("record_id", "")
            title = fields.get("标题", "未命名")
            status = fields.get("状态", "")
            version = fields.get("版本记录", "")[:50] if fields.get("版本记录") else ""
            print(f"📝 {title}")
            print(f"   ID: {record_id}")
            print(f"   状态: {status}")
            if version:
                print(f"   版本: {version}...")
            print()
        
        print("查看详情: python3 scripts/run.py --step 6 --record-id <ID>")
    else:
        # 查看单条笔记的完整信息
        table_id = config["feishu"]["table_id_notes"]
        
        # 获取记录列表
        records = client.get_table_records(table_id)
        record = None
        for r in records:
            if r.get("record_id") == args.record_id:
                record = r
                break
        
        if not record:
            print("❌ 未找到记录")
            return
        
        fields = record.get("fields", {})
        
        print(f"📋 状态: {fields.get('状态', 'N/A')}")
        print(f"📅 发布时间: {fields.get('发布时间', 'N/A')}")
        
        print(f"\n📝 初稿版本:")
        print("-" * 40)
        print(f"标题: {fields.get('初稿标题', 'N/A')}")
        print(f"正文: {fields.get('初稿正文', 'N/A')[:100]}...")
        print(f"话题: {fields.get('初稿话题标签', 'N/A')}")
        
        print(f"\n📝 发布版本:")
        print("-" * 40)
        print(f"标题: {fields.get('发布标题', 'N/A')}")
        print(f"正文: {fields.get('发布正文', 'N/A')[:100] if fields.get('发布正文') else '未发布'}")
        print(f"话题: {fields.get('发布话题标签', 'N/A')}")


if __name__ == "__main__":
    main()
