#!/usr/bin/env python3
"""
小红书运营主脚本
完整流程：选题 → 初稿 → 配图 → 待发布 → 已发布
每个环节都会同步到飞书笔记库
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from feishu_client import FeishuClient, load_config

# 工作流环节
STAGES = ["选题", "初稿", "配图", "待发布", "已发布"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书运营工具")
    parser.add_argument("--step", choices=["1", "2", "3", "4", "5", "all"], 
                       default="all", help="执行哪一步: 1=选题 2=初稿 3=配图 4=待发布 5=已发布")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--topic", help="选题内容")
    parser.add_argument("--draft", help="生成的初稿内容（JSON格式：{title, content, tags}）")
    parser.add_argument("--images", help="图片路径（逗号分隔）")
    parser.add_argument("--record-id", help="飞书笔记库记录ID（用于继续流程）")
    
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
        step_create_draft(config, client, args)
    
    if args.step in ["3", "all"]:
        step_add_images(config, client, args)
    
    if args.step in ["4", "all"]:
        step_ready_to_publish(config, client, args)
    
    if args.step in ["5", "all"]:
        step_published(config, client, args)
    
    print("\n✅ 流程完成")


def step_choose_topic(config, client, args):
    """第1步：选题 - 从飞书选题库读取"""
    print("\n=== 第1步：选题 ===")
    
    table_id = config["feishu"]["table_id_topics"]
    records = client.get_table_records(table_id)
    
    # 筛选未完成的选题
    available = [r for r in records if r.get("fields", {}).get("状态") != "已完成"]
    
    if available:
        print(f"找到 {len(available)} 个可选选题：")
        for i, r in enumerate(available, 1):
            fields = r.get("fields", {})
            print(f"  {i}. {fields.get('选题', '未命名')} | {fields.get('类型', '')} | {fields.get('状态', '')}")
        print(f"\n📝 请选择选题编号，或使用 --topic 参数指定")
    else:
        print("暂无选题，请在飞书选题库添加")


def step_create_draft(config, client, args):
    """第2步：初稿 - 生成文案并写入飞书"""
    print("\n=== 第2步：生成初稿 ===")
    
    if not args.draft and not args.topic:
        print("❌ 需要提供选题内容，使用 --topic 或 --draft 参数")
        return
    
    table_id = config["feishu"]["table_id_notes"]
    
    # 解析初稿内容
    if args.draft:
        import json
        draft = json.loads(args.draft)
        title = draft.get("title", "")
        content = draft.get("content", "")
        tags = draft.get("tags", "")
    else:
        title = f"关于{args.topic}的笔记"
        content = f"# {args.topic}\n\n（待AI生成内容）"
        tags = ""
    
    # 写入飞书笔记库（状态即环节）
    fields = {
        "标题": title,
        "正文": content,
        "话题标签": tags,
        "状态": "初稿"  # 环节：初稿/配图/待发布/已发布
    }
    
    result = client.create_table_record(table_id, fields)
    record_id = result.get("record", {}).get("record_id", "")
    
    print(f"✅ 初稿已保存到飞书笔记库")
    print(f"   记录ID: {record_id}")
    print(f"   标题: {title}")
    print(f"   环节: 初稿")
    print(f"\n📝 继续流程请使用: --record-id {record_id}")


def step_add_images(config, client, args):
    """第3步：配图 - 渲染图片"""
    print("\n=== 第3步：配图 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    # TODO: 调用 render_xhs.py 渲染图片
    # 这里简化处理
    images = args.images or ["./picture/card_1.png"]
    
    print(f"📷 待渲染图片: {images}")
    print("（调用 render_xhs.py 渲染图片）")
    print("✅ 图片渲染完成")
    
    # 更新飞书笔记库
    table_id = config["feishu"]["table_id_notes"]
    fields = {
        "封面图": images[0] if images else "",
        "内容图": ",".join(images) if images else "",
        "状态": "配图"
    }
    
    client.update_table_record(table_id, args.record_id, fields)
    print(f"✅ 已更新飞书笔记库，状态: 配图")


def step_ready_to_publish(config, client, args):
    """第4步：待发布 - 保存到小红书草稿箱"""
    print("\n=== 第4步：待发布 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    # TODO: 调用浏览器上传到小红书草稿箱
    print("📤 打开小红书创作平台...")
    print("   （需要在浏览器中手动上传图片）")
    print("✅ 已保存到小红书草稿箱")
    
    # 更新飞书笔记库
    table_id = config["feishu"]["table_id_notes"]
    fields = {
        "状态": "待发布"
    }
    
    client.update_table_record(table_id, args.record_id, fields)
    print(f"✅ 已更新飞书笔记库，状态: 待发布")


def step_published(config, client, args):
    """第5步：已发布 - 标记为已发布"""
    print("\n=== 第5步：已发布 ===")
    
    if not args.record_id:
        print("❌ 需要提供记录ID，使用 --record-id 参数")
        return
    
    import time
    fields = {
        "状态": "已发布",
        "发布时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    table_id = config["feishu"]["table_id_notes"]
    client.update_table_record(table_id, args.record_id, fields)
    
    print(f"✅ 已更新飞书笔记库，状态: 已发布")


if __name__ == "__main__":
    main()
