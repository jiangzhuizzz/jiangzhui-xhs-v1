# 小红书自动化系统 - 新手部署指南

> 适用于：全新电脑、零基础用户、跨设备迁移

---

## 📋 前置要求

### 系统要求
- macOS 10.15+ / Windows 10+ / Linux
- 至少 2GB 可用磁盘空间
- 稳定的网络连接

### 需要准备的账号
- ✅ GitHub 账号（用于代码管理）
- ✅ 飞书账号 + 开发者权限
- ✅ 小红书账号（已登录）
- ✅ Telegram 账号（可选，用于通知）

---

## 🚀 第一步：安装基础环境

### 1.1 安装 Git

**macOS:**
```bash
# 检查是否已安装
git --version

# 如果没有，安装 Xcode Command Line Tools
xcode-select --install
```

**Windows:**
- 下载：https://git-scm.com/download/win
- 安装时选择默认选项即可

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

### 1.2 安装 Python 3.9+

**macOS:**
```bash
# 使用 Homebrew 安装
brew install python@3.11

# 验证安装
python3 --version
```

**Windows:**
- 下载：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 1.3 安装 OpenClaw（可选，用于 Telegram 通知）

```bash
# macOS/Linux
npm install -g openclaw

# 验证安装
openclaw --version
```

---

## 📦 第二步：克隆项目

### 2.1 克隆仓库

```bash
# 进入你想存放项目的目录
cd ~/Projects

# 克隆项目
git clone https://github.com/jiangzhuizzz/jiangzhui-xhs-v1.git

# 进入项目目录
cd jiangzhui-xhs-v1
```

### 2.2 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2.3 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

---

## ⚙️ 第三步：配置项目

### 3.1 复制配置模板

```bash
cp config/config.yaml.example config/config.yaml
```

### 3.2 配置飞书应用

**步骤：**

1. 访问飞书开放平台：https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`
4. 添加权限：
   - `bitable:app` - 多维表格读写
   - `drive:drive` - 云文档读写

5. **使用模板库（推荐）**：
   - 📋 模板库链接：https://jcngro65vrcw.feishu.cn/base/NBnHb1YvLabIGXsKnzHcki6jnwf?from=from_copylink
   - 点击右上角「使用此模板」复制到你的飞书空间
   - 模板包含：
     - ✅ 选题库（字段：标题、内容类型、关键词、状态、优先级）
     - ✅ 笔记库（字段：标题、正文、话题、封面图、状态、发布时间）
     - ✅ 预设工作流状态
   
   **或手动创建多维表格**：
   - 选题库（包含字段：标题、内容类型、关键词、状态）
   - 笔记库（包含字段：标题、正文、话题、封面图、状态）

6. 获取 `App Token` 和 `Table ID`
   - 打开多维表格，URL 中的 `base/` 后面是 `App Token`
   - 点击表格名称，URL 中的 `table/` 后面是 `Table ID`

**填写配置：**

编辑 `config/config.yaml`：

```yaml
feishu:
  app_id: "cli_xxxxxxxxxxxxx"        # 替换为你的 App ID
  app_secret: "xxxxxxxxxxxxxxxx"     # 替换为你的 App Secret
  app_token: "xxxxxxxxxxxxx"         # 替换为你的 App Token
  table_id_topics: "tblxxxxxxxxx"    # 选题库 Table ID
  table_id_notes: "tblxxxxxxxxx"     # 笔记库 Table ID
```

### 3.3 配置 Telegram 通知（可选）

**获取你的 Telegram ID：**

1. 在 Telegram 搜索 `@userinfobot`
2. 发送 `/start`
3. 复制你的 ID（纯数字）

**填写配置：**

```yaml
telegram:
  enabled: true
  chat_id: "你的Telegram ID"  # 例如: "5345571859"
```

### 3.4 配置小红书（可选）

如果需要自动发布到小红书：

```yaml
xiaohongshu:
  openclaw_url: "http://127.0.0.1:18789"
  cdp_port: 18789
```

---

## 🧪 第四步：测试运行

### 4.1 测试图片渲染

创建测试文件 `test.md`：

```markdown
---
emoji: 📝
title: 测试标题
subtitle: 这是一个测试
---

# 这是标题

这是正文内容，测试一下渲染效果。

- 列表项 1
- 列表项 2
- 列表项 3

#测试话题 #小红书
```

运行渲染：

```bash
python3 scripts/render_xhs.py test.md --theme sketch
```

检查输出目录 `picture/` 是否生成了图片。

### 4.2 测试飞书连接

```bash
python3 -c "
from scripts.feishu_client import FeishuClient, load_config
config = load_config()
client = FeishuClient(config['feishu']['app_id'], config['feishu']['app_secret'])
print('✅ 飞书连接成功！')
"
```

### 4.3 测试 Telegram 通知

```bash
python3 scripts/notify.py sync_success
```

检查 Telegram 是否收到测试消息。

---

## 🎯 第五步：日常使用

### 5.1 生成单篇笔记

```bash
python3 scripts/run.py --step 2 \
  --title "武汉过早plog｜这一碗热干面才8块钱" \
  --content "正文内容..." \
  --tags "#武汉美食 #热干面"
```

### 5.2 批量生成笔记

```bash
# 从飞书选题库获取 5 个待处理选题
python3 scripts/batch_process.py --count 5

# 指定选题列表
python3 scripts/batch_process.py --topics "选题1,选题2,选题3"

# 从文件读取
python3 scripts/batch_process.py --file topics.txt
```

### 5.3 查看日志

```bash
# 同步日志
tail -f logs/sync.log

# 发布日志
tail -f /tmp/xhs-publish.log
```

---

## 🔧 第六步：配置自动化（可选）

### 6.1 配置自动同步到 GitHub

```bash
# 测试同步脚本
bash scripts/auto_sync.sh

# 添加到 cron（每2小时自动同步）
crontab -e

# 添加以下行：
0 9-23/2 * * * /path/to/jiangzhui-xhs-v1/scripts/auto_sync.sh
```

### 6.2 配置自动发布

```bash
# 添加到 cron（每10分钟检查一次）
crontab -e

# 添加以下行：
*/10 * * * * /path/to/xhs-auto-publish.sh >> /tmp/xhs-publish.log 2>&1
```

---

## 🐛 常见问题

### Q1: `playwright install` 失败

**解决方案：**

```bash
# 设置国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

# 重新安装
playwright install chromium
```

### Q2: 飞书 API 返回 "app_access_token invalid"

**原因：** App Secret 配置错误或权限不足

**解决方案：**
1. 检查 `config.yaml` 中的 `app_id` 和 `app_secret` 是否正确
2. 确认应用已添加必要权限
3. 重新获取 token

### Q3: 图片渲染失败

**可能原因：**
- Playwright 浏览器未安装
- 字体缺失
- 内存不足

**解决方案：**

```bash
# 重新安装浏览器
playwright install chromium

# macOS 安装中文字体
brew install font-noto-sans-cjk

# 检查内存
free -h  # Linux
vm_stat  # macOS
```

### Q4: Git 推送失败 "Permission denied"

**解决方案：**

```bash
# 配置 Git 凭证
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 配置 SSH 密钥（推荐）
ssh-keygen -t ed25519 -C "你的邮箱"
cat ~/.ssh/id_ed25519.pub  # 复制公钥到 GitHub
```

### Q5: Telegram 通知不工作

**检查清单：**
1. OpenClaw 是否已安装并运行
2. `config.yaml` 中 `telegram.enabled` 是否为 `true`
3. `chat_id` 是否正确
4. 网络是否能访问 Telegram

---

## 📚 进阶配置

### 自定义主题

1. 复制现有主题：
   ```bash
   cp assets/themes/sketch.css assets/themes/my-theme.css
   ```

2. 编辑 CSS 样式

3. 使用自定义主题：
   ```bash
   python3 scripts/render_xhs.py test.md --theme my-theme
   ```

### 扩展违禁词库

编辑 `scripts/banned_words.py`，添加自定义规则。

### 批量导入选题

创建 `topics.txt`：
```
武汉过早推荐
公积金贷款攻略
周末武汉游玩指南
```

批量导入：
```bash
python3 scripts/batch_process.py --file topics.txt
```

---

## 🆘 获取帮助

- **GitHub Issues**: https://github.com/jiangzhuizzz/jiangzhui-xhs-v1/issues
- **文档**: 查看 `docs/` 目录下的详细文档
- **日志**: 检查 `logs/` 目录下的日志文件

---

## 📝 更新日志

查看项目更新：

```bash
cd jiangzhui-xhs-v1
git pull origin master
pip install -r requirements.txt --upgrade
```

---

**祝你使用愉快！🎉**

如有问题，欢迎提 Issue 或联系作者。
