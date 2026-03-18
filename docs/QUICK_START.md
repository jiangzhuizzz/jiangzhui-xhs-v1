# 小红书自动化系统 - 新手快速上手指南

> 适用于：零基础用户、只想用不想管代码的人

**核心功能**：飞书多维表格 + OpenClaw = 自动生成小红书笔记

---

## 📋 你需要准备什么

### 必需
- ✅ **飞书账号**（用于存储选题和笔记）
- ✅ **OpenClaw**（用于自动化和浏览器控制）
- ✅ **Python 3.9+**（运行脚本）

### 可选
- ⭐ **Telegram 账号**（接收通知，可选）
- ⭐ **小红书账号**（自动发布，可选）

---

## 🚀 第一步：下载项目

### 方式 1：直接下载（推荐新手）

1. 访问项目页面：https://github.com/jiangzhuizzz/jiangzhui-xhs-v1
2. 点击绿色按钮 **Code** → **Download ZIP**
3. 解压到你想放的位置，比如 `~/Downloads/jiangzhui-xhs-v1`

### 方式 2：使用 Git（可选）

```bash
git clone https://github.com/jiangzhuizzz/jiangzhui-xhs-v1.git
cd jiangzhui-xhs-v1
```

---

## 🔧 第二步：安装依赖

### 2.1 检查 Python

打开终端（macOS/Linux）或命令提示符（Windows），输入：

```bash
python3 --version
```

如果显示版本号（如 `Python 3.11.x`），说明已安装。

**如果没有安装 Python：**

- **macOS**: `brew install python@3.11`
- **Windows**: 下载 https://www.python.org/downloads/
- **Linux**: `sudo apt install python3 python3-pip`

### 2.2 安装项目依赖

进入项目目录：

```bash
cd ~/Downloads/jiangzhui-xhs-v1  # 替换为你的实际路径
```

安装依赖：

```bash
pip3 install -r requirements.txt
playwright install chromium
```

---

## ⚙️ 第三步：配置飞书

### 3.1 使用模板库（最简单）

1. **复制模板库**：
   - 点击链接：https://jcngro65vrcw.feishu.cn/base/NBnHb1YvLabIGXsKnzHcki6jnwf
   - 点击右上角「使用此模板」
   - 模板会自动复制到你的飞书空间

2. **模板包含**：
   - ✅ 选题库（标题、内容类型、关键词、状态）
   - ✅ 笔记库（标题、正文、话题、封面图、状态）
   - ✅ 预设工作流

### 3.2 创建飞书应用

1. 访问飞书开放平台：https://open.feishu.cn/
2. 点击「创建企业自建应用」
3. 填写应用名称（如：小红书助手）
4. 创建完成后，记录：
   - **App ID**（形如 `cli_xxxxx`）
   - **App Secret**（点击查看并复制）

### 3.3 添加权限（重要！）

在应用管理页面，点击「权限管理」，添加以下**所有权限**：

#### 📋 多维表格权限（必需）

| 权限代码 | 权限名称 | 用途说明 |
|---------|---------|---------|
| `bitable:app` | 查看、编辑和管理多维表格 | 读取选题库、写入笔记库 |

#### 📁 云文档权限（必需）

| 权限代码 | 权限名称 | 用途说明 |
|---------|---------|---------|
| `drive:drive` | 查看、编辑和管理云空间文件 | 上传生成的图片到飞书云盘 |

#### 🔍 其他可能需要的权限（可选）

| 权限代码 | 权限名称 | 用途说明 |
|---------|---------|---------|
| `im:message` | 获取与发送单聊、群组消息 | 如需飞书机器人通知（可选） |
| `contact:user.base:readonly` | 获取用户基本信息 | 如需识别操作人（可选） |

**⚠️ 重要提示：**
1. 添加权限后，必须点击「发布版本」才能生效
2. 如果权限不足，脚本会报错：`Permission denied` 或 `Access token invalid`
3. 建议先添加必需权限，测试通过后再按需添加可选权限

**权限申请步骤：**
1. 进入应用管理页面
2. 点击左侧「权限管理」
3. 搜索权限代码（如 `bitable:app`）
4. 点击「申请权限」
5. 填写申请理由（如：用于自动化内容管理）
6. 等待管理员审批（企业自建应用通常自动通过）
7. 所有权限添加完成后，点击右上角「创建版本」→「发布」

### 3.4 获取表格信息

1. 打开你复制的多维表格
2. 查看浏览器地址栏：
   ```
   https://xxx.feishu.cn/base/NBnHb1YvLabIGXsKnzHcki6jnwf?table=tblxxxxx
   ```
   - `base/` 后面的是 **App Token**：`NBnHb1YvLabIGXsKnzHcki6jnwf`
   - `table=` 后面的是 **Table ID**：`tblxxxxx`

3. 分别记录：
   - 选题库的 Table ID
   - 笔记库的 Table ID

### 3.5 填写配置文件

复制配置模板：

```bash
cp config/config.yaml.example config/config.yaml
```

编辑 `config/config.yaml`，填写你的信息：

```yaml
feishu:
  app_id: "cli_xxxxxxxxxxxxx"        # 你的 App ID
  app_secret: "xxxxxxxxxxxxxxxx"     # 你的 App Secret
  app_token: "NBnHb1YvLabIGXsKnzHcki6jnwf"  # 你的 App Token
  table_id_topics: "tblxxxxxxxxx"    # 选题库 Table ID
  table_id_notes: "tblxxxxxxxxx"     # 笔记库 Table ID
```

---

## 🤖 第四步：安装 OpenClaw

### 4.1 安装 OpenClaw

```bash
# macOS/Linux
npm install -g openclaw

# 验证安装
openclaw --version
```

### 4.2 启动 OpenClaw Gateway

```bash
openclaw gateway start
```

访问 http://127.0.0.1:18789/ 确认运行正常。

### 4.3 配置 Telegram 通知（可选）

**获取你的 Telegram ID：**

1. 在 Telegram 搜索 `@userinfobot`
2. 发送 `/start`
3. 复制你的 ID（纯数字）

**填写配置：**

编辑 `config/config.yaml`：

```yaml
telegram:
  enabled: true
  chat_id: "你的Telegram ID"  # 例如: "5345571859"
```

---

## 🌐 第五步：配置小红书发布（可选）

**⚠️ 重要：发布功能需要 OpenClaw 浏览器**

### 5.1 启动 OpenClaw 浏览器

OpenClaw 提供了浏览器自动化功能，用于自动发布笔记到小红书。

```bash
# 启动浏览器（会自动打开 Chrome）
openclaw browser start
```

### 5.2 登录小红书

1. 在 OpenClaw 浏览器中访问 https://xiaohongshu.com
2. 扫码登录你的小红书账号
3. 保持登录状态

### 5.3 配置发布设置

编辑 `config/config.yaml`：

```yaml
xiaohongshu:
  openclaw_url: "http://127.0.0.1:18789"
  cdp_port: 18789
```

---

## 🧪 第六步：测试运行

### 6.1 测试图片渲染

创建测试文件 `test.md`：

```markdown
---
emoji: 📝
title: 测试标题
subtitle: 这是一个测试
---

# 这是标题

这是正文内容，测试一下渲染效果。

#测试话题 #小红书
```

运行渲染：

```bash
python3 scripts/render_xhs.py test.md --theme sketch
```

检查 `picture/` 目录是否生成了图片。

### 6.2 测试飞书连接

```bash
python3 -c "
from scripts.feishu_client import FeishuClient, load_config
config = load_config()
client = FeishuClient(config['feishu']['app_id'], config['feishu']['app_secret'])
print('✅ 飞书连接成功！')
"
```

### 6.3 测试违禁词检测

```bash
python3 scripts/banned_words.py "武汉过早推荐，热干面才8块钱！"
```

---

## 🎯 第七步：日常使用

### 使用流程

```
1. 在飞书选题库添加选题
   ↓
2. 运行脚本生成文案和图片
   ↓
3. 在飞书笔记库查看结果
   ↓
4. 人工审核修改
   ↓
5. 自动发布到小红书（需要 OpenClaw 浏览器）
```

### 生成单篇笔记

```bash
python3 scripts/run.py --step 2 \
  --title "武汉过早plog｜这一碗热干面才8块钱" \
  --content "正文内容..." \
  --tags "#武汉美食 #热干面"
```

### 批量生成笔记

```bash
# 从飞书选题库获取 5 个待处理选题
python3 scripts/batch_process.py --count 5

# 指定选题列表
python3 scripts/batch_process.py --topics "选题1,选题2,选题3"
```

### 检测违禁词

```bash
python3 scripts/banned_words.py "你的文案内容"
```

---

## 🔄 自动化设置（可选）

### 自动发布

如果你想让系统自动检查飞书中状态为"待发布"的笔记并自动发布：

**前提条件：**
- ✅ OpenClaw 浏览器已启动
- ✅ 小红书已登录

**配置定时任务：**

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每10分钟检查一次）
*/10 * * * * /path/to/xhs-auto-publish.sh >> /tmp/xhs-publish.log 2>&1
```

---

## 🐛 常见问题

### Q1: 提示 "playwright install" 失败

**解决方案：**

```bash
# 设置国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

# 重新安装
playwright install chromium
```

### Q2: 飞书 API 返回错误

**检查清单：**
1. App ID 和 App Secret 是否正确
2. 权限是否已添加并发布
3. App Token 和 Table ID 是否正确

### Q3: 图片渲染失败

**可能原因：**
- Playwright 浏览器未安装
- 内存不足

**解决方案：**

```bash
# 重新安装浏览器
playwright install chromium
```

### Q4: 发布功能不工作

**检查清单：**
1. OpenClaw Gateway 是否运行（`openclaw gateway status`）
2. OpenClaw 浏览器是否启动
3. 小红书是否已登录
4. 配置文件中的 `openclaw_url` 是否正确

### Q5: Telegram 通知不工作

**检查清单：**
1. OpenClaw 是否已安装并运行
2. `config.yaml` 中 `telegram.enabled` 是否为 `true`
3. `chat_id` 是否正确（纯数字）

---

## 📚 核心依赖说明

### 飞书的作用
- 📋 存储选题库（你想写什么）
- 📝 存储笔记库（生成的文案和图片）
- 🔄 管理工作流状态（待生成 → 初稿 → 审核 → 待发布 → 已发布）

### OpenClaw 的作用
- 🤖 Telegram 通知（可选）
- 🌐 浏览器自动化（发布到小红书）
- 🔧 提供 API 接口（用于脚本调用）

### OpenClaw 浏览器的作用
- 🚀 **自动发布笔记到小红书**
- 📸 保持登录状态
- 🎯 模拟人工操作

**重要提示：**
- 如果你只想生成文案和图片，不需要 OpenClaw 浏览器
- 如果你想自动发布到小红书，必须启动 OpenClaw 浏览器并保持小红书登录状态

---

## 🆘 获取帮助

- **GitHub Issues**: https://github.com/jiangzhuizzz/jiangzhui-xhs-v1/issues
- **查看日志**: `logs/` 目录下的日志文件
- **测试连接**: 运行测试脚本确认各组件是否正常

---

## 📝 更新项目

如果项目有更新，重新下载 ZIP 并解压覆盖即可。

**保留你的配置：**
- 备份 `config/config.yaml`
- 解压新版本
- 恢复配置文件

---

**祝你使用愉快！🎉**

有问题随时在 GitHub 提 Issue。
