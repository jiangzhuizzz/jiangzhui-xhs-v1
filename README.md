# 小红书自动化内容生成与发布系统

一键生成小红书文案、渲染图片、上传飞书多维表格的自动化工具。

**核心功能**：飞书多维表格 + OpenClaw = 自动生成小红书笔记

---

## 📖 使用指南

### 🎯 新手快速上手（推荐）

**适合人群**：零基础用户、只想用不想管代码

👉 **[新手快速上手指南](docs/QUICK_START.md)**

- ✅ 无需 GitHub 账号
- ✅ 无需代码管理
- ✅ 只需飞书 + OpenClaw
- ✅ 详细图文教程

### 🔧 开发者完整指南

**适合人群**：需要二次开发、跨设备部署

👉 **[完整部署指南](docs/SETUP_GUIDE.md)**

- Git 克隆和版本管理
- 虚拟环境配置
- 高级功能定制

---

## ✨ 功能特性

- 📝 **智能文案生成**：基于主题和关键词自动生成小红书风格文案
- 🎨 **图片自动渲染**：支持 8 种精美主题，自动生成封面和内容卡片
- 🚫 **违禁词检测**：自动检测并标记小红书平台违禁词
- 📤 **飞书集成**：自动上传文案和图片到飞书多维表格
- 🔄 **全流程自动化**：从内容生成到素材准备一键完成

## 🚀 快速开始

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
- 其他必要参数

### 基础使用

**一键生成文案+图片+上传飞书：**

```bash
python3 scripts/run.py --step 2 \
  --title "武汉过早plog｜这一碗热干面才8块钱" \
  --content "正文内容(支持markdown)" \
  --tags "#武汉美食 #热干面"
```

**仅生成文案（不渲染图片）：**

```bash
python3 scripts/run.py --step 2 \
  --title "标题" \
  --content "正文" \
  --no-render
```

## 📁 项目结构

```
jiangzhui-xhs-v1/
├── config/
│   └── config.yaml          # 配置文件
├── scripts/
│   ├── run.py              # 主入口脚本
│   ├── feishu_client.py    # 飞书 API 客户端
│   ├── render_xhs.py       # 图片渲染引擎
│   └── banned_words.py     # 违禁词检测
├── picture/                # 生成的图片输出目录
├── templates/              # 图片模板
└── README.md
```

## 🎨 支持的图片主题

- `sketch` - 手绘风格
- `modern` - 现代简约
- `cute` - 可爱卡通
- `elegant` - 优雅风格
- `vibrant` - 活力色彩
- `minimal` - 极简主义
- `retro` - 复古风格
- `tech` - 科技感

使用方式：

```bash
python3 scripts/render_xhs.py --theme sketch 内容.md
```

## 🔧 高级配置

### 飞书多维表格字段映射

在 `config/config.yaml` 中配置字段映射：

```yaml
feishu:
  app_id: "your_app_id"
  app_secret: "your_app_secret"
  bitable_id: "your_bitable_id"
  table_id: "your_table_id"
  
  field_mapping:
    title: "标题"
    content: "正文"
    tags: "话题"
    images: "封面图"
    status: "状态"
```

### 违禁词自定义

编辑 `scripts/banned_words.py` 添加自定义违禁词规则。

## 📝 工作流程

1. **生成文案** → 根据输入生成小红书风格内容
2. **违禁词检测** → 自动标记需要修改的词汇
3. **渲染图片** → 生成封面和内容卡片
4. **上传飞书** → 将文案和图片同步到多维表格
5. **状态管理** → 自动更新记录状态（初稿/待发布/已发布）

## 🛠️ 开发说明

### 本地开发

```bash
# 克隆项目
git clone https://github.com/jiangzhuizzz/jiangzhui-xhs-v1.git
cd jiangzhui-xhs-v1

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp config/config.yaml.example config/config.yaml
# 编辑 config.yaml 填写必要信息

# 运行测试
python3 scripts/run.py --step 2 --title "测试" --content "测试内容"
```

### 更新同步

```bash
# 拉取最新代码
git pull origin master

# 推送本地修改
git add .
git commit -m "描述你的修改"
git push origin master
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- GitHub: [@jiangzhuizzz](https://github.com/jiangzhuizzz)

---

**最后更新**: 2026-03-18
