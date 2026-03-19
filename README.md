# 小红书自动化内容生成与发布系统

一键生成小红书文案、渲染图片，上传飞书多维表格的自动化工具。

**核心功能**：飞书多维表格 + OpenClaw = 自动生成小红书笔记

---

## 核心功能

- 智能文案生成：基于主题和关键词自动生成小红书风格文案
- 图片自动渲染：支持多种精美主题，自动生成封面和内容卡片
- 违禁词检测：自动检测并标记小红书平台违禁词
- 飞书集成：自动上传文案和图片到飞书多维表格
- 全流程自动化：从内容生成到素材准备一键完成

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

复制配置模板并填写必要信息：

```bash
cp config/config.yaml.example config/config.yaml
```

编辑 `config/config.yaml`，配置：
- 飞书 App ID 和 App Secret
- 飞书多维表格 ID

### 使用方式

```bash
# 方式一：使用 render_xhs.py (8个主题 + 4种分页模式)
python3 scripts/render_xhs.py content.md -t sketch -m separator

# 方式二：使用 render_xhs_v2.py (7种内置样式 + 智能分页)
python3 scripts/render_xhs_v2.py content.md -s purple
```

---

## 项目结构

```
jiangzhui-xhs-v1/
├── config/
│   └── config.yaml          # 配置文件
├── scripts/
│   ├── run.py              # 主入口脚本
│   ├── feishu_client.py   # 飞书 API 客户端
│   ├── render_xhs.py      # 图片渲染 V1 (8个主题)
│   ├── render_xhs_v2.py   # 图片渲染 V2 (7种样式)
│   ├── banned_words.py    # 违禁词检测
│   ├── batch_process.py   # 批量处理
│   ├── check_xhs.py      # 小红书检查
│   ├── upload_xhs.py     # 上传脚本
│   ├── auto_publish.py    # 自动发布
│   ├── notify.py         # 通知模块
│   └── assets/           # 渲染资源
│       ├── themes/       # 主题 CSS
│       ├── card.html    # 卡片模板
│       ├── cover.html   # 封面模板
│       └── styles.css   # 样式
├── docs/                   # 文档
├── picture/              # 生成的图片
└── README.md
```

---

## 图片渲染

### V1: render_xhs.py

支持 8 种主题 + 4 种分页模式：

```bash
# 默认：sketch 主题 + separator 分页
python3 scripts/render_xhs.py content.md

# 切换主题
python3 scripts/render_xhs.py content.md -t playful-geometric

# 切换分页模式
python3 scripts/render_xhs.py content.md -m auto-split
```

**主题 (-t)**：
- sketch - 手绘素描风格
- default - 默认紫色渐变
- playful-geometric - 活泼几何风格
- neo-brutalism - 新粗野主义
- botanical - 植物园风格
- professional - 专业商务风格
- retro - 复古怀旧风格
- terminal - 终端命令行风格

**分页模式 (-m)**：
- separator - 按 --- 分隔符手动分页
- auto-fit - 自动缩放填满固定尺寸
- auto-split - 根据内容高度自动切分
- dynamic - 动态调整图片高度

### V2: render_xhs_v2.py

支持 7 种内置样式 + 智能分页：

```bash
# 默认：purple 样式
python3 scripts/render_xhs_v2.py content.md

# 切换样式
python3 scripts/render_xhs_v2.py content.md -s mint
```

**样式 (-s)**：
- purple - 紫韵（默认）
- xiaohongshu - 小红书红
- mint - 清新薄荷
- sunset - 日落橙
- ocean - 深海蓝
- elegant - 优雅白
- dark - 暗黑模式

---

## 文档

- [新手快速上手指南](docs/QUICK_START.md)
- [完整部署指南](docs/SETUP_GUIDE.md)
- [优化路线图](docs/ROADMAP.md)
- [数据收集与 A/B 测试方案](docs/DATA_COLLECTION_AB_TESTING.md)

---

## 开发说明

```bash
# 克隆项目
git clone https://github.com/jiangzhuizzz/jiangzhui-xhs-v1.git
cd jiangzhui-xhs-v1

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp config/config.yaml.example config/config.yaml

# 运行测试
python3 scripts/run.py --step 2 --title "测试" --content "测试内容"
```

---

## 更新同步

```bash
# 拉取最新代码
git pull origin master

# 推送本地修改
git add .
git commit -m "描述你的修改"
git push origin master
```

---

**最后更新**: 2026-03-19
