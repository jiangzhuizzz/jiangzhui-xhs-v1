#!/usr/bin/env python3
"""
upload_xhs.py
连接 OpenClaw 的 Chrome（CDP 18800），完成小红书图文发布
用法：
  python3 upload_xhs.py --images cover.png card_1.png --title "标题" --content "正文" --tags "武汉,生活"
"""

import argparse
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


CDP_URL = "http://127.0.0.1:18800"
PUBLISH_URL = "https://creator.xiaohongshu.com/creator/post?type=image"


def log(msg: str):
    print(f"[xhs] {msg}", flush=True)


def wait(seconds: float, reason: str = ""):
    if reason:
        log(f"等待 {seconds}s：{reason}")
    time.sleep(seconds)


def publish(images: list[str], title: str, content: str, tags: list[str], dry_run: bool = False, cdp_url: str = CDP_URL, visibility: str = "公开"):
    # ── 验证图片文件存在 ──────────────────────────────────────
    for img in images:
        if not Path(img).exists():
            log(f"❌ 图片不存在：{img}")
            sys.exit(1)
    log(f"✅ 图片验证通过：{images}")

    # ── 连接 OpenClaw Chrome ──────────────────────────────────
    with sync_playwright() as p:
        log(f"连接 CDP：{cdp_url}")
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            log(f"❌ 连接失败，确认 OpenClaw 正在运行：{e}")
            sys.exit(1)

        # 找到创作者页面的 tab，或新开一个
        context = browser.contexts[0]
        page = None
        for p_tab in context.pages:
            if "creator.xiaohongshu.com" in p_tab.url:
                page = p_tab
                log(f"✅ 找到已有创作中心标签：{p_tab.url}")
                break

        if page is None:
            log("未找到创作中心标签，新开发布页...")
            page = context.new_page()
            page.goto(PUBLISH_URL)
            wait(3, "页面加载")

        # 强制导航到图文发布页
        if "type=image" not in page.url:
            log(f"当前不是图文页（{page.url}），导航到图文页...")
            page.goto(PUBLISH_URL)

        # 等待页面加载完成
        wait(2, "等待页面渲染")
        log(f"当前页面：{page.url}")

        log(f"当前页面：{page.url}")

        # ── Step 1：注入图片文件 ─────────────────────────────────────
        log(f"注入图片文件：{images}")
        try:
            # 直接使用 file_chooser 方式（方法1在新版页面已失效）
            log("尝试点击上传区域触发 file_chooser...")
            upload_trigger = page.locator(
                '.img-upload-area, '
                '.upload-img-area, '
                '[class*="img-upload"], '
                '.img-preview-area, '
                '[class*="upload"], '
                'button:has-text("上传")'
            ).first

            try:
                with page.expect_file_chooser(timeout=10000) as fc_info:
                    upload_trigger.click()
                file_chooser = fc_info.value
                file_chooser.set_files(images)
                log("✅ 通过 file_chooser 注入图片成功")
            except Exception as e2:
                log(f"❌ file_chooser 方式失败：{e2}")
                log("请手动上传图片后，按 Enter 继续...")
                input()

            wait(3, "等待图片上传处理")

        except Exception as e:
            log(f"❌ 图片注入失败：{e}")
            log("请手动上传图片后，按 Enter 继续...")
            input()

        # ── Step 2：填写标题 ──────────────────────────────────────
        log(f"填写标题：{title}")
        wait(3, "等待编辑区渲染")
        try:
            title_input = page.locator(
                '[placeholder*="填写标题会有更多赞"], '
                '[placeholder*="标题会有更多赞"], '
                'input[placeholder*="标题"]'
            ).first
            title_input.wait_for(state="attached", timeout=15000)
            title_input.click()
            title_input.fill("")
            title_input.type(title, delay=40)
            wait(0.5)

            # 校验字数
            title_len = page.evaluate(
                "() => document.querySelector('[placeholder*=\"填写标题\"], input[placeholder*=\"标题\"]')?.value?.length || 0"
            )
            log(f"标题长度：{title_len}/20")
            if title_len > 20:
                log("⚠️  标题超过20字，请手动修改后按 Enter 继续...")
                input()
            else:
                log("✅ 标题填写完成")
        except Exception as e:
            log(f"❌ 填写标题失败：{e}")
            log("请手动填写标题后，按 Enter 继续...")
            input()

        # ── Step 3：填写正文 ──────────────────────────────────────
        log("填写正文...")
        wait(0.5)
        try:
            content_area = page.locator(
                '[placeholder*="添加正文"], '
                '[placeholder*="正文"], '
                '[contenteditable="true"]:not([placeholder*="标题"]):not([placeholder*="填写标题"])'
            ).first
            content_area.wait_for(state="attached", timeout=10000)
            content_area.click()
            wait(0.3)
            content_area.type(content, delay=25)
            log("✅ 正文填写完成")
            wait(0.5)
        except Exception as e:
            log(f"❌ 填写正文失败：{e}")
            log("请手动填写正文后，按 Enter 继续...")
            input()

        # ── Step 4：添加话题标签 ──────────────────────────────────
        if tags:
            log(f"添加话题标签：{tags}")
            wait(0.5)
            try:
                for tag in tags[:10]:  # 最多10个
                    # 在正文末尾追加 #标签
                    content_area = page.locator(
                        '[placeholder*="添加正文"], '
                        '[placeholder*="正文"], '
                        '[contenteditable="true"]:not([placeholder*="标题"]):not([placeholder*="填写标题"])'
                    ).first
                    content_area.click()
                    # 移到末尾
                    content_area.press("End")
                    content_area.type(f" #{tag}", delay=50)
                    wait(1.5)
                    # 等待话题联想弹出后点击第一个
                    suggestion = page.locator(
                        '.topic-item, .suggest-item, '
                        '[class*="topic"], [class*="suggest"], '
                        '[class*="hash-tag"]'
                    ).first
                    if suggestion.is_visible(timeout=2500):
                        suggestion.click()
                        log(f"  ✅ 话题已选：{tag}")
                        wait(0.5)
                    else:
                        # 联想没出来就按空格收起，话题文字已经在正文里了
                        content_area.press("Space")
                        log(f"  ⚠️  话题无联想，文字已写入正文：#{tag}")
                    wait(0.3)
            except Exception as e:
                log(f"⚠️  话题标签添加失败：{e}，继续流程")

        # ── Step 5：设置可见范围 ──────────────────────────────────
        if visibility != "公开":
            log(f"设置可见范围：{visibility}")
            wait(0.5)
            try:
                option_map = {
                    "私密": "仅自己可见",
                    "好友": "仅互关好友可见",
                    "公开": "公开可见",
                }
                option_text = option_map.get(visibility, visibility)
                visibility_btn = page.locator(
                    '[class*="visibility"], [class*="permission"], '
                    'button:has-text("公开"), .set-visibility'
                ).first
                visibility_btn.click()
                wait(1, "等待下拉菜单")
                option = page.locator(
                    f'li:has-text("{option_text}"), '
                    f'[class*="option"]:has-text("{option_text}")'
                ).first
                option.click()
                log(f"✅ 可见范围已设置：{option_text}")
                wait(0.5)
            except Exception as e:
                log(f"⚠️  自动设置可见范围失败：{e}")
                log(f"请手动设置后按 Enter 继续...")
                input()

        # ── Step 6：截图确认三要素 ────────────────────────────────
        log("截图确认发布内容...")
        wait(1)
        screenshot_path = "/tmp/openclaw/uploads/xhs_preview.png"
        page.screenshot(path=screenshot_path, full_page=False)
        log(f"✅ 预览截图已保存：{screenshot_path}")

        # ── Step 6：停在发布按钮，等待人工确认 ─────────────────────
        if dry_run:
            log("🔍 dry-run 模式，停在发布按钮前，不实际发布")
            log("请检查页面内容是否正确，按 Enter 退出...")
            input()
            return

        log("=" * 50)
        log("⚠️  即将发布，请检查页面内容")
        log(f"  标题：{title}")
        log(f"  图片：{images}")
        log(f"  标签：{tags}")
        log(f"  可见：{visibility}")
        log("确认发布请输入 yes，取消请输入 no：")
        confirm = input().strip().lower()

        if confirm != "yes":
            log("已取消发布")
            return

        # ── Step 7：点击发布 ──────────────────────────────────────
        log("点击发布按钮...")
        try:
            publish_btn = page.locator(
                'button:has-text("发布"), '
                '.publish-btn, '
                '[class*="publish"]:has-text("发布")'
            ).last
            publish_btn.click()
            wait(3, "等待发布响应")

            # 校验是否发布成功（跳转或出现成功提示）
            current_url = page.url
            log(f"发布后页面：{current_url}")

            if "success" in current_url or "creator" in current_url:
                log("✅ 发布成功！")
                if visibility == "私密":
                    log("⏰ 注意：请在30分钟-2小时后手动改公开！")
                    log("   路径：笔记管理 → 编辑 → 可见性改为「公开」")
            else:
                # 尝试读取笔记 ID
                note_id = page.evaluate("""
                    () => {
                        const url = window.location.href;
                        const match = url.match(/noteId=([a-zA-Z0-9]+)/);
                        return match ? match[1] : null;
                    }
                """)
                if note_id:
                    log(f"✅ 发布成功！笔记ID：{note_id}")
                    if visibility == "私密":
                        log("⏰ 注意：请在30分钟-2小时后手动改公开！")
                        log("   路径：笔记管理 → 编辑 → 可见性改为「公开」")
                else:
                    log("⚠️  发布状态未知，请手动确认页面")

        except Exception as e:
            log(f"❌ 点击发布失败：{e}")
            log("请手动点击发布按钮")


def main():
    parser = argparse.ArgumentParser(description="小红书图文发布脚本（连接 OpenClaw Chrome）")
    parser.add_argument("--images", nargs="+", required=True, help="图片路径列表（cover.png card_1.png ...）")
    parser.add_argument("--title", required=True, help="笔记标题（≤20字）")
    parser.add_argument("--content", required=True, help="正文内容")
    parser.add_argument("--tags", default="", help="话题标签，逗号分隔（武汉,生活,打工人）")
    parser.add_argument("--cdp", default=CDP_URL, help=f"CDP 地址（默认 {CDP_URL}）")
    parser.add_argument("--dry-run", action="store_true", help="预演模式，不实际点击发布")
    parser.add_argument("--visibility", default="公开",
                        choices=["公开", "私密", "好友"],
                        help="可见范围：公开 / 私密（仅自己）/ 好友（互关）")
    parser.add_argument("--delay-min", type=int, default=0,
                        help="发布时间随机化：延迟多少分钟后发布（随机±30%，如设为60则实际延迟42-78分钟）")
    parser.add_argument("--schedule", 
                        help="定时发布：格式如 '18:30' 或 '2026-03-16 18:30'")

    args = parser.parse_args()
    
    # 处理定时发布
    if args.schedule:
        import schedule
        from datetime import datetime, timedelta
        import random
        
        # 解析时间
        try:
            if ' ' in args.schedule:
                target_time = datetime.strptime(args.schedule, '%Y-%m-%d %H:%M')
            else:
                today = datetime.now().strftime('%Y-%m-%d')
                target_time = datetime.strptime(f"{today} {args.schedule}", '%Y-%m-%d %H:%M')
        except ValueError:
            print(f"❌ 时间格式错误，请使用 '18:30' 或 '2026-03-16 18:30'")
            sys.exit(1)
        
        # 如果时间已过，推到明天
        if target_time < datetime.now():
            target_time += timedelta(days=1)
        
        delay_seconds = (target_time - datetime.now()).total_seconds()
        print(f"⏰ 定时发布已设置：{target_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   等待 {int(delay_seconds)} 秒后自动发布...")
        
        time.sleep(delay_seconds)
    
    # 处理随机延迟发布
    elif args.delay_min > 0:
        import random
        # 随机±30%
        actual_delay = args.delay_min * random.uniform(0.7, 1.3)
        print(f"🎲 随机延迟发布：{int(actual_delay)} 分钟后自动发布（原值 {args.delay_min} 分钟）")
        time.sleep(actual_delay * 60)
    
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    cdp_url = args.cdp

    publish(
        images=args.images,
        title=args.title,
        content=args.content,
        tags=tags,
        dry_run=args.dry_run,
        cdp_url=cdp_url,
        visibility=args.visibility,
    )


if __name__ == "__main__":
    main()
