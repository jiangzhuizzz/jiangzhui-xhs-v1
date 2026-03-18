#!/usr/bin/env python3
"""
Telegram 通知模块
用于发送各类运营通知到 Telegram
"""

import os
import sys
import yaml
import requests
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        return None
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def send_telegram_message(message: str, parse_mode: str = "Markdown"):
    """
    发送 Telegram 消息
    
    Args:
        message: 消息内容
        parse_mode: 解析模式 (Markdown/HTML)
    
    Returns:
        bool: 是否发送成功
    """
    config = load_config()
    
    if not config or not config.get('telegram', {}).get('enabled'):
        return False
    
    chat_id = config['telegram'].get('chat_id')
    if not chat_id:
        return False
    
    # 使用 OpenClaw 的 message 工具发送
    # 这里通过调用 openclaw CLI 来发送消息
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--target', chat_id, '--message', message],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"发送 Telegram 消息失败: {e}", file=sys.stderr)
        return False


def notify_sync_success(commit_hash: str = "", files_changed: int = 0):
    """通知 Git 同步成功"""
    config = load_config()
    if not config or 'sync_success' not in config.get('telegram', {}).get('notify_on', []):
        return
    
    message = f"""✅ **Git 同步成功**

📦 提交: `{commit_hash[:7] if commit_hash else 'unknown'}`
📝 修改文件: {files_changed} 个
🕐 时间: {_get_current_time()}
"""
    send_telegram_message(message)


def notify_sync_failure(error: str = ""):
    """通知 Git 同步失败"""
    config = load_config()
    if not config or 'sync_failure' not in config.get('telegram', {}).get('notify_on', []):
        return
    
    message = f"""❌ **Git 同步失败**

⚠️ 错误: {error[:200]}
🕐 时间: {_get_current_time()}

请检查网络或权限设置。
"""
    send_telegram_message(message)


def notify_publish_success(title: str = "", note_url: str = ""):
    """通知发布成功"""
    config = load_config()
    if not config or 'publish_success' not in config.get('telegram', {}).get('notify_on', []):
        return
    
    message = f"""🎉 **小红书发布成功**

📝 标题: {title}
🔗 链接: {note_url if note_url else '草稿箱'}
🕐 时间: {_get_current_time()}
"""
    send_telegram_message(message)


def notify_publish_failure(title: str = "", error: str = ""):
    """通知发布失败"""
    config = load_config()
    if not config or 'publish_failure' not in config.get('telegram', {}).get('notify_on', []):
        return
    
    message = f"""❌ **小红书发布失败**

📝 标题: {title}
⚠️ 错误: {error[:200]}
🕐 时间: {_get_current_time()}

请检查账号登录状态或内容是否违规。
"""
    send_telegram_message(message)


def notify_render_complete(title: str = "", card_count: int = 0, output_dir: str = ""):
    """通知图片渲染完成"""
    config = load_config()
    if not config or 'render_complete' not in config.get('telegram', {}).get('notify_on', []):
        return
    
    message = f"""🎨 **图片渲染完成**

📝 标题: {title}
🖼️ 卡片数: {card_count} 张
📁 目录: `{output_dir}`
🕐 时间: {_get_current_time()}
"""
    send_telegram_message(message)


def _get_current_time():
    """获取当前时间字符串"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    # 测试通知
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'sync_success':
            notify_sync_success('abc1234', 3)
        elif test_type == 'sync_failure':
            notify_sync_failure('网络连接超时')
        elif test_type == 'publish_success':
            notify_publish_success('武汉过早plog｜这一碗热干面才8块钱', 'https://xiaohongshu.com/xxx')
        elif test_type == 'publish_failure':
            notify_publish_failure('测试标题', '账号未登录')
        elif test_type == 'render_complete':
            notify_render_complete('测试标题', 5, './picture/2026-03-18-测试')
        else:
            print("用法: python notify.py [sync_success|sync_failure|publish_success|publish_failure|render_complete]")
    else:
        print("Telegram 通知模块已加载")
        print("用法: python notify.py [test_type]")
