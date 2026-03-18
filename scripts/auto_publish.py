# 自动发布脚本（供Telegram命令调用）

#!/usr/bin/env python3
"""
Telegram 命令：/publish
检测待发布状态并立即发布
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.feishu_client import FeishuClient, load_config
from datetime import datetime

def auto_publish():
    config = load_config("config/config.yaml")
    client = FeishuClient("config/config.yaml")
    
    table_id = config["feishu"]["table_id_notes"]
    records = client.get_table_records(table_id)
    
    published = []
    
    for r in records:
        f = r.get("fields", {})
        if f.get("状态") == "待发布":
            record_id = r.get("record_id")
            title = f.get("标题", "未命名")
            
            # 发布
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            fields = {
                "状态": "已发布",
                "发布时间文本": now_str
            }
            client.update_table_record(table_id, record_id, fields)
            published.append(title)
    
    if published:
        return f"✅ 已自动发布：\n" + "\n".join(f"- {t}" for t in published)
    else:
        return "没有待发布的笔记"

if __name__ == "__main__":
    result = auto_publish()
    print(result)
