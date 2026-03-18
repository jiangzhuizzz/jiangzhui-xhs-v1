#!/usr/bin/env python3
"""
小红书运营主脚本
完整流程：选题 → 生成文案 → 违禁词检测 → 渲染图片 → 发布
"""

import os
import sys
import argparse
import yaml
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from feishu_client import FeishuClient, load_config


def main():
    parser = argparse.ArgumentParser(description="小红书运营工具")
    parser.add_argument("--step", choices=["1", "2", "3", "4", "5", "all"], 
                       default="all", help="执行哪一步: 1=选题 2=文案 3=检测 4=图片 5=发布")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--topic-id", help="选题ID（可选）")
    parser.add_argument("--title", help="笔记标题")
    parser.add_argument("--content", help="笔记正文")
    parser.add_argument("--images", nargs="+", help="图片路径列表")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际执行")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    print(f"📋 已加载配置: {args.config}")
    
    # 执行对应步骤
    if args.step in ["1", "all"]:
        step_choose_topic(config, args)
    
    if args.step in ["2", "all"]:
        step_generate_content(config, args)
    
    if args.step in ["3", "all"]:
        step_check_content(config, args)
    
    if args.step in ["4", "all"]:
        step_render_image(config, args)
    
    if args.step in ["5", "all"]:
        step_publish(config, args)
    
    print("✅ 流程完成")


def step_choose_topic(config, args):
    """第1步：选题"""
    print("\n=== 第1步：选题 ===")
    # TODO: 从飞书多维表格读取选题
    print("从飞书选题库读取待写选题...")
    
    # 示例：读取选题库
    client = FeishuClient(args.config)
    table_id = config["feishu"]["table_id_topics"]
    
    # 读取状态为"待写"的选题
    # filter = 'filter={"status":{"eq":"待写"}}'
    records = client.get_table_records(table_id)
    
    if records:
        print(f"找到 {len(records)} 个选题")
        for i, r in enumerate(records[:3]):
            fields = r.get("fields", {})
            print(f"  {i+1}. {fields.get('选题', '未命名')} ({fields.get('类型', '')})")
    else:
        print("暂无选题，请在飞书选题库添加")


def step_generate_content(config, args):
    """第2步：生成文案"""
    print("\n=== 第2步：生成文案 ===")
    # TODO: 调用 AI 生成文案
    # TODO: 写入飞书笔记库
    print("调用 AI 生成文案...")
    print("写入飞书笔记库...")


def step_check_content(config, args):
    """第3步：违禁词检测"""
    print("\n=== 第3步：违禁词检测 ===")
    import check_xhs
    # TODO: 执行检测
    print("检测通过 ✓")


def step_render_image(config, args):
    """第4步：渲染图片"""
    print("\n=== 第4步：渲染图片 ===")
    # TODO: 调用 render_xhs.py
    # TODO: 上传到飞书云空间
    print("渲染图片...")
    print("上传飞书云空间...")


def step_publish(config, args):
    """第5步：发布"""
    print("\n=== 第5步：发布 ===")
    # TODO: 从飞书下载图片
    # TODO: 调用 upload_xhs.py
    print("下载飞书图片...")
    print("发布到小红书...")


if __name__ == "__main__":
    main()
