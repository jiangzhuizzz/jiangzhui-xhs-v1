# 数据收集与 A/B 测试 - 详细实现方案

> 版本：v1.0  
> 更新时间：2026-03-19

---

## 📊 第一部分：数据收集实现方案

### 1.1 数据架构设计

#### 数据库选择

**推荐方案**：飞书多维表格（已有基础设施）

**优势**：
- ✅ 无需额外部署数据库
- ✅ 可视化界面，方便查看
- ✅ 支持 API 操作
- ✅ 自带权限管理

**备选方案**：SQLite 本地数据库（如需高级查询）

---

### 1.2 数据表设计

#### 表 1：笔记发布记录（notes_published）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| note_id | 文本 | 小红书笔记 ID | `65f8a9b2000000001e03e8f9` |
| title | 文本 | 标题 | `武汉过早plog｜这一碗热干面才8块钱` |
| content_type | 单选 | 内容类型 | `武汉生活` |
| publish_time | 日期时间 | 发布时间 | `2026-03-19 10:00:00` |
| tags | 多选 | 话题标签 | `#武汉美食 #热干面 #过早` |
| image_count | 数字 | 图片数量 | `3` |
| word_count | 数字 | 字数 | `520` |
| ab_test_group | 文本 | A/B测试分组 | `A` / `B` / `null` |
| ab_test_variant | 文本 | 测试变量 | `title_v1` / `tags_v2` |

#### 表 2：互动数据（notes_metrics）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| note_id | 文本 | 关联笔记 ID | `65f8a9b2000000001e03e8f9` |
| collected_at | 日期时间 | 数据采集时间 | `2026-03-19 11:00:00` |
| likes | 数字 | 点赞数 | `128` |
| collects | 数字 | 收藏数 | `45` |
| comments | 数字 | 评论数 | `12` |
| shares | 数字 | 分享数 | `8` |
| views | 数字 | 浏览量 | `1520` |
| engagement_rate | 数字 | 互动率 | `12.8%` |

**计算公式**：
```python
engagement_rate = (likes + collects + comments + shares) / views * 100
```

#### 表 3：粉丝增长（followers_growth）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | 日期 | 日期 | `2026-03-19` |
| followers | 数字 | 粉丝数 | `156` |
| new_followers | 数字 | 新增粉丝 | `8` |
| unfollowers | 数字 | 取关数 | `2` |
| net_growth | 数字 | 净增长 | `6` |

#### 表 4：对标账号监控（competitor_notes）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| account_name | 文本 | 账号名称 | `武汉美食探店` |
| note_id | 文本 | 笔记 ID | `xxx` |
| title | 文本 | 标题 | `xxx` |
| publish_time | 日期时间 | 发布时间 | `xxx` |
| likes | 数字 | 点赞数 | `xxx` |
| collects | 数字 | 收藏数 | `xxx` |
| tags | 多选 | 话题标签 | `xxx` |

#### 表 5：热点追踪（trending_topics）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| topic | 文本 | 话题名称 | `#武汉美食` |
| heat_score | 数字 | 热度分数 | `8520` |
| collected_at | 日期时间 | 采集时间 | `2026-03-19 10:00` |
| trend | 文本 | 趋势 | `上升` / `下降` / `稳定` |
| related_notes | 数字 | 相关笔记数 | `1250` |

---

### 1.3 数据收集实现

#### 方案 1：浏览器自动化抓取（推荐）

**技术栈**：Playwright + OpenClaw 浏览器

**实现步骤**：

```python
# scripts/data_collector.py

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from scripts.feishu_client import FeishuClient, load_config

async def collect_note_metrics(note_id: str):
    """采集单条笔记的互动数据"""
    
    async with async_playwright() as p:
        # 使用 OpenClaw 浏览器（已登录）
        browser = await p.chromium.connect_over_cdp(
            "http://127.0.0.1:18789"
        )
        
        page = await browser.new_page()
        
        # 访问笔记页面
        await page.goto(f"https://www.xiaohongshu.com/explore/{note_id}")
        await page.wait_for_load_state('networkidle')
        
        # 提取数据
        likes = await page.locator('.like-count').text_content()
        collects = await page.locator('.collect-count').text_content()
        comments = await page.locator('.comment-count').text_content()
        
        # 保存到飞书
        config = load_config()
        client = FeishuClient(
            config['feishu']['app_id'],
            config['feishu']['app_secret']
        )
        
        client.add_record(
            app_token=config['feishu']['app_token'],
            table_id='notes_metrics_table_id',
            fields={
                'note_id': note_id,
                'collected_at': datetime.now().isoformat(),
                'likes': int(likes),
                'collects': int(collects),
                'comments': int(comments)
            }
        )
        
        await browser.close()

async def collect_all_notes():
    """批量采集所有已发布笔记的数据"""
    
    config = load_config()
    client = FeishuClient(
        config['feishu']['app_id'],
        config['feishu']['app_secret']
    )
    
    # 获取所有已发布笔记
    notes = client.list_records(
        app_token=config['feishu']['app_token'],
        table_id=config['feishu']['table_id_notes']
    )
    
    published_notes = [
        n for n in notes 
        if n.get('fields', {}).get('状态') == '已发布'
    ]
    
    # 逐个采集数据
    for note in published_notes:
        note_id = note.get('fields', {}).get('note_id')
        if note_id:
            await collect_note_metrics(note_id)
            await asyncio.sleep(2)  # 避免请求过快

if __name__ == '__main__':
    asyncio.run(collect_all_notes())
```

**定时任务配置**：

```bash
# 每小时采集一次
0 * * * * cd /path/to/project && python3 scripts/data_collector.py >> logs/collector.log 2>&1
```

---

#### 方案 2：小红书 API（如果有）

**优势**：
- 更稳定
- 数据更准确
- 不依赖浏览器

**劣势**：
- 需要官方 API 权限
- 可能有调用限制

**实现**：（待小红书开放 API）

---

### 1.4 数据分析脚本

```python
# scripts/data_analyzer.py

import pandas as pd
from scripts.feishu_client import FeishuClient, load_config

def analyze_best_publish_time():
    """分析最佳发布时间"""
    
    config = load_config()
    client = FeishuClient(
        config['feishu']['app_id'],
        config['feishu']['app_secret']
    )
    
    # 获取所有笔记数据
    notes = client.list_records(
        app_token=config['feishu']['app_token'],
        table_id=config['feishu']['table_id_notes']
    )
    
    # 转换为 DataFrame
    df = pd.DataFrame([n['fields'] for n in notes])
    
    # 提取发布时间的小时
    df['hour'] = pd.to_datetime(df['publish_time']).dt.hour
    
    # 按小时分组，计算平均互动率
    hourly_performance = df.groupby('hour').agg({
        'likes': 'mean',
        'collects': 'mean',
        'engagement_rate': 'mean'
    }).sort_values('engagement_rate', ascending=False)
    
    print("最佳发布时间（按互动率排序）：")
    print(hourly_performance.head(5))
    
    return hourly_performance

def analyze_top_content():
    """分析爆款内容特征"""
    
    config = load_config()
    client = FeishuClient(
        config['feishu']['app_id'],
        config['feishu']['app_secret']
    )
    
    notes = client.list_records(
        app_token=config['feishu']['app_token'],
        table_id=config['feishu']['table_id_notes']
    )
    
    df = pd.DataFrame([n['fields'] for n in notes])
    
    # 筛选高赞内容（点赞数 > 平均值 * 2）
    avg_likes = df['likes'].mean()
    top_notes = df[df['likes'] > avg_likes * 2]
    
    print(f"\n爆款内容分析（点赞 > {avg_likes * 2:.0f}）：")
    print(f"总数：{len(top_notes)} 篇")
    print(f"\n内容类型分布：")
    print(top_notes['content_type'].value_counts())
    print(f"\n平均字数：{top_notes['word_count'].mean():.0f}")
    print(f"\n平均图片数：{top_notes['image_count'].mean():.1f}")
    
    return top_notes

if __name__ == '__main__':
    analyze_best_publish_time()
    analyze_top_content()
```

---

## 🧪 第二部分：A/B 测试实现方案

### 2.1 A/B 测试框架设计

#### 测试流程

```
1. 定义测试目标
   ↓
2. 生成变体（A/B/C...）
   ↓
3. 随机分配发布时间
   ↓
4. 发布并监测
   ↓
5. 数据收集
   ↓
6. 统计分析
   ↓
7. 选出最优版本
```

---

### 2.2 测试维度设计

#### 维度 1：标题测试

**测试变量**：
- 标题公式（数字型 vs 疑问型 vs 情感型）
- 关键词位置（前置 vs 后置）
- emoji 使用（有 vs 无）
- 标题长度（短 vs 长）

**示例**：

| 版本 | 标题 | 公式 |
|------|------|------|
| A | 武汉过早plog｜这一碗热干面才8块钱 | 数字型 |
| B | 在武汉，8块钱能吃到什么？ | 疑问型 |
| C | 这家热干面，让我想起了家的味道 | 情感型 |

---

#### 维度 2：话题测试

**测试变量**：
- 话题数量（3个 vs 5个）
- 话题类型（地域 vs 内容 vs 情感）
- 话题热度（热门 vs 精准）

**示例**：

| 版本 | 话题组合 |
|------|---------|
| A | #武汉美食 #热干面 #过早 |
| B | #武汉 #武汉生活 #美食探店 #热干面 #本地推荐 |
| C | #热干面 #早餐 #美食分享 |

---

#### 维度 3：图片测试

**测试变量**：
- 主题风格（sketch vs modern vs cute）
- 图片数量（1张 vs 3张 vs 5张）
- 封面类型（纯文字 vs 图文结合）

---

#### 维度 4：发布时间测试

**测试变量**：
- 早上（7:00-9:00）
- 中午（11:00-13:00）
- 下午（15:00-17:00）
- 晚上（19:00-21:00）

---

### 2.3 A/B 测试实现

#### 脚本实现

```python
# scripts/ab_test.py

import random
from datetime import datetime, timedelta
from scripts.feishu_client import FeishuClient, load_config

class ABTest:
    """A/B 测试管理器"""
    
    def __init__(self):
        config = load_config()
        self.client = FeishuClient(
            config['feishu']['app_id'],
            config['feishu']['app_secret']
        )
        self.config = config
    
    def generate_title_variants(self, base_content: str) -> list:
        """生成标题变体"""
        
        # 从配置读取提示词
        writing_guide = self.config['prompts']['xiaohongshu_writing_guide']
        
        # 调用 AI 生成 3 个不同公式的标题
        variants = [
            {
                'version': 'A',
                'title': '武汉过早plog｜这一碗热干面才8块钱',
                'formula': '数字型'
            },
            {
                'version': 'B',
                'title': '在武汉，8块钱能吃到什么？',
                'formula': '疑问型'
            },
            {
                'version': 'C',
                'title': '这家热干面，让我想起了家的味道',
                'formula': '情感型'
            }
        ]
        
        return variants
    
    def generate_tags_variants(self) -> list:
        """生成话题变体"""
        
        variants = [
            {
                'version': 'A',
                'tags': ['#武汉美食', '#热干面', '#过早'],
                'strategy': '精准'
            },
            {
                'version': 'B',
                'tags': ['#武汉', '#武汉生活', '#美食探店', '#热干面', '#本地推荐'],
                'strategy': '广泛'
            },
            {
                'version': 'C',
                'tags': ['#热干面', '#早餐', '#美食分享'],
                'strategy': '通用'
            }
        ]
        
        return variants
    
    def schedule_ab_test(self, variants: list, test_type: str):
        """安排 A/B 测试发布时间"""
        
        # 随机分配发布时间（间隔 2-4 小时）
        base_time = datetime.now() + timedelta(hours=1)
        
        for i, variant in enumerate(variants):
            publish_time = base_time + timedelta(hours=i * 3)
            
            # 保存到飞书选题库
            self.client.add_record(
                app_token=self.config['feishu']['app_token'],
                table_id=self.config['feishu']['table_id_topics'],
                fields={
                    '标题': variant['title'],
                    '状态': '待生成',
                    '计划发布时间': publish_time.isoformat(),
                    'AB测试分组': variant['version'],
                    'AB测试类型': test_type,
                    'AB测试变量': variant.get('formula') or variant.get('strategy')
                }
            )
            
            print(f"✅ 已安排 {variant['version']} 版本，发布时间：{publish_time}")
    
    def analyze_ab_test_results(self, test_id: str):
        """分析 A/B 测试结果"""
        
        # 获取测试相关的所有笔记
        notes = self.client.list_records(
            app_token=self.config['feishu']['app_token'],
            table_id=self.config['feishu']['table_id_notes']
        )
        
        test_notes = [
            n for n in notes 
            if n.get('fields', {}).get('AB测试ID') == test_id
        ]
        
        if not test_notes:
            print("❌ 未找到测试数据")
            return
        
        # 对比各版本表现
        results = []
        for note in test_notes:
            fields = note['fields']
            results.append({
                'version': fields.get('AB测试分组'),
                'likes': fields.get('likes', 0),
                'collects': fields.get('collects', 0),
                'engagement_rate': fields.get('engagement_rate', 0)
            })
        
        # 排序找出最优版本
        best = max(results, key=lambda x: x['engagement_rate'])
        
        print(f"\n🏆 A/B 测试结果：")
        print(f"最优版本：{best['version']}")
        print(f"互动率：{best['engagement_rate']:.2f}%")
        print(f"\n详细对比：")
        for r in sorted(results, key=lambda x: x['engagement_rate'], reverse=True):
            print(f"  {r['version']}: 互动率 {r['engagement_rate']:.2f}% | 点赞 {r['likes']} | 收藏 {r['collects']}")
        
        return best

# 使用示例
if __name__ == '__main__':
    ab = ABTest()
    
    # 生成标题变体
    title_variants = ab.generate_title_variants("武汉热干面推荐")
    
    # 安排测试
    ab.schedule_ab_test(title_variants, test_type='title')
    
    # 等待发布和数据收集...
    
    # 分析结果
    # ab.analyze_ab_test_results('test_001')
```

---

### 2.4 统计显著性检验

```python
# scripts/ab_test_stats.py

from scipy import stats
import numpy as np

def chi_square_test(group_a: dict, group_b: dict):
    """卡方检验：判断两组差异是否显著"""
    
    # 构建列联表
    observed = np.array([
        [group_a['likes'], group_a['views'] - group_a['likes']],
        [group_b['likes'], group_b['views'] - group_b['likes']]
    ])
    
    # 卡方检验
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)
    
    print(f"卡方值: {chi2:.4f}")
    print(f"P值: {p_value:.4f}")
    
    if p_value < 0.05:
        print("✅ 差异显著（p < 0.05）")
        return True
    else:
        print("❌ 差异不显著（p >= 0.05）")
        return False

# 使用示例
group_a = {'likes': 120, 'views': 1500}
group_b = {'likes': 85, 'views': 1450}

chi_square_test(group_a, group_b)
```

---

### 2.5 自动化 A/B 测试流程

```bash
# 完整流程脚本
# scripts/run_ab_test.sh

#!/bin/bash

# 1. 生成变体
python3 scripts/ab_test.py generate --type title

# 2. 等待发布（由定时任务自动发布）
echo "等待发布..."

# 3. 定时采集数据（每小时）
while true; do
    python3 scripts/data_collector.py
    sleep 3600
done

# 4. 24小时后分析结果
sleep 86400
python3 scripts/ab_test.py analyze --test-id test_001
```

---

## 📊 第三部分：数据可视化

### 3.1 飞书仪表盘配置

**推荐图表**：

1. **粉丝增长曲线**（折线图）
   - X轴：日期
   - Y轴：粉丝数

2. **互动率趋势**（折线图）
   - X轴：日期
   - Y轴：互动率

3. **内容类型表现**（柱状图）
   - X轴：内容类型
   - Y轴：平均点赞数

4. **最佳发布时间**（热力图）
   - X轴：星期
   - Y轴：小时
   - 颜色：互动率

5. **话题表现对比**（气泡图）
   - X轴：使用次数
   - Y轴：平均互动率
   - 气泡大小：总点赞数

---

### 3.2 定期报告生成

```python
# scripts/generate_report.py

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

def generate_weekly_report():
    """生成周报"""
    
    # 获取过去7天数据
    # ...
    
    # 生成图表
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 图1：粉丝增长
    axes[0, 0].plot(dates, followers)
    axes[0, 0].set_title('粉丝增长')
    
    # 图2：互动率趋势
    axes[0, 1].plot(dates, engagement_rates)
    axes[0, 1].set_title('互动率趋势')
    
    # 图3：内容类型表现
    axes[1, 0].bar(content_types, avg_likes)
    axes[1, 0].set_title('内容类型表现')
    
    # 图4：爆款内容 TOP 5
    axes[1, 1].barh(top_titles, top_likes)
    axes[1, 1].set_title('爆款内容 TOP 5')
    
    plt.tight_layout()
    plt.savefig(f'reports/weekly_{datetime.now().strftime("%Y%m%d")}.png')
    
    print("✅ 周报已生成")
```

---

## 🎯 实施计划

### Week 1：数据收集基础
- ✅ 设计飞书数据表结构
- ✅ 实现数据采集脚本
- ✅ 配置定时任务

### Week 2：A/B 测试框架
- ✅ 实现变体生成
- ✅ 实现测试调度
- ✅ 实现结果分析

### Week 3：数据分析与可视化
- ✅ 实现分析脚本
- ✅ 配置飞书仪表盘
- ✅ 实现报告生成

### Week 4：优化与迭代
- ✅ 根据数据优化策略
- ✅ 完善自动化流程
- ✅ 文档完善

---

## 📝 注意事项

### 1. 数据隐私
- 不采集用户个人信息
- 仅采集公开数据
- 遵守平台规则

### 2. 采集频率
- 避免请求过快（建议间隔 2-5 秒）
- 使用代理（如需）
- 错误重试机制

### 3. 数据准确性
- 多次采集取平均值
- 异常值检测和过滤
- 定期校验数据

### 4. A/B 测试原则
- 单一变量原则（一次只测一个维度）
- 样本量充足（至少 30 个数据点）
- 时间充足（至少 24 小时）
- 统计显著性检验

---

**最后更新**：2026-03-19
