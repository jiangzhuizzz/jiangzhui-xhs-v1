#!/usr/bin/env python3
"""
批量处理脚本 - 一次生成多篇小红书笔记
支持从选题库批量读取、批量生成文案、批量渲染图片、批量上传飞书

使用方法:
    python batch_process.py --count 5                    # 从选题库随机选5个
    python batch_process.py --topics "话题1,话题2,话题3"   # 指定话题
    python batch_process.py --file topics.txt            # 从文件读取选题列表
    python batch_process.py --dry-run                    # 预览模式，不实际生成
"""

import argparse
import asyncio
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.feishu_client import FeishuClient
from scripts.run import generate_draft, render_images, upload_to_feishu


def load_config():
    """加载配置文件"""
    config_file = PROJECT_ROOT / "config" / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_topics_from_file(file_path: str) -> List[str]:
    """从文件加载选题列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def fetch_topics_from_feishu(count: int = 5) -> List[Dict]:
    """从飞书选题库获取待处理的选题"""
    config = load_config()
    client = FeishuClient(
        config['feishu']['app_id'],
        config['feishu']['app_secret']
    )
    
    # 获取选题库记录
    records = client.list_records(
        config['feishu']['app_token'],
        config['feishu']['table_id_topics']
    )
    
    # 筛选状态为"待生成"的选题
    pending_topics = [
        r for r in records 
        if r.get('fields', {}).get('状态') == '待生成'
    ]
    
    # 按优先级排序（如果有优先级字段）
    pending_topics.sort(
        key=lambda x: x.get('fields', {}).get('优先级', 999)
    )
    
    return pending_topics[:count]


async def process_single_topic(topic: Dict, config: dict, dry_run: bool = False) -> Dict:
    """处理单个选题"""
    fields = topic.get('fields', {})
    title = fields.get('标题', '未命名')
    content_type = fields.get('内容类型', '武汉生活')
    keywords = fields.get('关键词', '')
    
    print(f"\n{'[预览]' if dry_run else ''}📝 处理选题: {title}")
    print(f"  类型: {content_type}")
    print(f"  关键词: {keywords}")
    
    if dry_run:
        return {
            'success': True,
            'title': title,
            'status': 'preview'
        }
    
    try:
        # 1. 生成文案
        print("  ⏳ 生成文案...")
        draft_result = await generate_draft(
            title=title,
            content_type=content_type,
            keywords=keywords
        )
        
        if not draft_result['success']:
            return {
                'success': False,
                'title': title,
                'error': draft_result.get('error', '生成失败')
            }
        
        # 2. 渲染图片
        print("  ⏳ 渲染图片...")
        render_result = await render_images(
            content=draft_result['content'],
            title=title,
            theme=config['image']['theme']
        )
        
        if not render_result['success']:
            return {
                'success': False,
                'title': title,
                'error': render_result.get('error', '渲染失败')
            }
        
        # 3. 上传到飞书
        print("  ⏳ 上传到飞书...")
        upload_result = upload_to_feishu(
            title=title,
            content=draft_result['content'],
            images=render_result['images'],
            record_id=topic.get('record_id')
        )
        
        if not upload_result['success']:
            return {
                'success': False,
                'title': title,
                'error': upload_result.get('error', '上传失败')
            }
        
        print(f"  ✅ 完成: {title}")
        return {
            'success': True,
            'title': title,
            'record_id': upload_result.get('record_id'),
            'images_count': len(render_result['images'])
        }
        
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return {
            'success': False,
            'title': title,
            'error': str(e)
        }


async def batch_process(topics: List[Dict], config: dict, 
                       dry_run: bool = False, 
                       parallel: int = 1) -> Dict:
    """批量处理选题"""
    print(f"\n🚀 开始批量处理 {len(topics)} 个选题")
    print(f"  并发数: {parallel}")
    print(f"  模式: {'预览' if dry_run else '生产'}")
    
    results = {
        'total': len(topics),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    # 分批处理（避免并发过高）
    for i in range(0, len(topics), parallel):
        batch = topics[i:i+parallel]
        
        # 并发处理当前批次
        tasks = [
            process_single_topic(topic, config, dry_run)
            for topic in batch
        ]
        batch_results = await asyncio.gather(*tasks)
        
        # 统计结果
        for result in batch_results:
            results['details'].append(result)
            if result['success']:
                results['success'] += 1
            else:
                results['failed'] += 1
        
        # 批次间延迟（避免API限流）
        if i + parallel < len(topics):
            await asyncio.sleep(2)
    
    return results


def print_summary(results: Dict):
    """打印处理结果摘要"""
    print("\n" + "="*50)
    print("📊 批量处理完成")
    print("="*50)
    print(f"  总数: {results['total']}")
    print(f"  成功: {results['success']} ✅")
    print(f"  失败: {results['failed']} ❌")
    
    if results['failed'] > 0:
        print("\n失败列表:")
        for detail in results['details']:
            if not detail['success']:
                print(f"  ❌ {detail['title']}: {detail.get('error', '未知错误')}")
    
    print("\n成功列表:")
    for detail in results['details']:
        if detail['success']:
            images_count = detail.get('images_count', 0)
            print(f"  ✅ {detail['title']} ({images_count} 张图片)")


async def main():
    parser = argparse.ArgumentParser(
        description='批量生成小红书笔记',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 选题来源
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--count', '-c',
        type=int,
        help='从飞书选题库获取指定数量的待处理选题'
    )
    source_group.add_argument(
        '--topics', '-t',
        help='逗号分隔的选题列表'
    )
    source_group.add_argument(
        '--file', '-f',
        help='从文件读取选题列表（每行一个）'
    )
    
    # 处理选项
    parser.add_argument(
        '--parallel', '-p',
        type=int,
        default=1,
        help='并发处理数量（默认: 1，建议不超过 3）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际生成'
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 获取选题列表
    topics = []
    
    if args.count:
        print(f"📥 从飞书选题库获取 {args.count} 个待处理选题...")
        topics = fetch_topics_from_feishu(args.count)
        if not topics:
            print("❌ 没有找到待处理的选题")
            sys.exit(1)
    
    elif args.topics:
        topic_list = [t.strip() for t in args.topics.split(',')]
        topics = [{'fields': {'标题': t}} for t in topic_list]
    
    elif args.file:
        topic_list = load_topics_from_file(args.file)
        topics = [{'fields': {'标题': t}} for t in topic_list]
    
    # 批量处理
    results = await batch_process(
        topics,
        config,
        dry_run=args.dry_run,
        parallel=args.parallel
    )
    
    # 打印摘要
    print_summary(results)
    
    # 发送 Telegram 通知
    if not args.dry_run:
        try:
            from scripts.notify import send_telegram_message
            message = f"""📦 **批量处理完成**

总数: {results['total']}
成功: {results['success']} ✅
失败: {results['failed']} ❌
"""
            send_telegram_message(message)
        except:
            pass


if __name__ == '__main__':
    asyncio.run(main())
