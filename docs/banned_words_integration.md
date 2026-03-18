# 小红书违禁词库对接方案

## 现状分析

当前项目使用的是本地静态违禁词列表（`scripts/banned_words.py`），存在以下问题：
- ❌ 词库更新不及时
- ❌ 无法覆盖小红书最新规则
- ❌ 缺少分类和严重等级

---

## 🎯 推荐方案

### 方案 1：对接第三方违禁词 API（推荐）

**优势：**
- ✅ 实时更新，覆盖最新规则
- ✅ 专业团队维护
- ✅ 支持多平台（小红书/抖音/微信等）

**可用服务：**

1. **阿里云内容安全 API**
   - 官网：https://www.aliyun.com/product/lvwang
   - 价格：按量计费，约 ¥0.003/次
   - 支持：文本检测、图片检测
   - 覆盖：违禁词、广告、色情、暴恐等

2. **腾讯云天御 API**
   - 官网：https://cloud.tencent.com/product/tms
   - 价格：按量计费，约 ¥0.0025/次
   - 支持：文本检测、图片检测
   - 覆盖：违禁词、广告、色情、暴恐等

3. **网易易盾 API**
   - 官网：https://dun.163.com/
   - 价格：按量计费，约 ¥0.002/次
   - 支持：文本检测、图片检测
   - 覆盖：违禁词、广告、色情、暴恐等

**集成示例（阿里云）：**

```python
from aliyunsdkcore.client import AcsClient
from aliyunsdkgreen.request.v20180509 import TextScanRequest
import json

def check_text_aliyun(text: str) -> dict:
    """使用阿里云检测文本"""
    client = AcsClient(
        'your_access_key_id',
        'your_access_key_secret',
        'cn-shanghai'
    )
    
    request = TextScanRequest.TextScanRequest()
    request.set_accept_format('JSON')
    
    task = {
        "dataId": str(uuid.uuid4()),
        "content": text
    }
    request.set_content(json.dumps({"tasks": [task], "scenes": ["antispam"]}))
    
    response = client.do_action_with_exception(request)
    result = json.loads(response)
    
    return {
        'safe': result['data'][0]['results'][0]['suggestion'] == 'pass',
        'reason': result['data'][0]['results'][0].get('label', ''),
        'details': result['data'][0]['results'][0].get('details', [])
    }
```

---

### 方案 2：爬取小红书官方违禁词库（免费但不稳定）

**优势：**
- ✅ 免费
- ✅ 直接来自小红书官方

**劣势：**
- ❌ 需要定期爬取更新
- ❌ 可能被反爬
- ❌ 无法覆盖隐性规则

**实现思路：**
1. 定期爬取小红书创作者中心的违禁词提示
2. 解析并存储到本地数据库
3. 定时更新（每周一次）

---

### 方案 3：众包维护违禁词库（社区驱动）

**优势：**
- ✅ 免费
- ✅ 社区共建，更新快

**劣势：**
- ❌ 需要维护成本
- ❌ 准确性依赖社区质量

**可用资源：**
- GitHub 开源项目：https://github.com/topics/sensitive-words
- 小红书创作者社群分享

---

### 方案 4：混合方案（推荐用于生产环境）

**组合策略：**
1. **本地基础词库**（快速检测，免费）
   - 常见违禁词（互粉、私信、包下款等）
   - 行业敏感词（贷款中介、100%等）

2. **第三方 API**（深度检测，付费）
   - 仅对本地检测通过的内容调用
   - 降低 API 调用成本

3. **定期更新机制**
   - 每周从社区/官方更新本地词库
   - 记录 API 检测出的新违禁词

**成本估算：**
- 假设每天生成 10 篇文案
- 本地检测通过率 80%
- API 调用：10 × 20% × 30 天 = 60 次/月
- 费用：60 × ¥0.003 = ¥0.18/月

---

## 🚀 实施建议

### 短期方案（立即可用）
1. 扩充本地违禁词库（手动维护）
2. 添加分类和严重等级
3. 优化检测逻辑（正则匹配 + 模糊匹配）

### 中期方案（1-2 周）
1. 对接阿里云/腾讯云 API
2. 实现混合检测策略
3. 添加检测结果缓存

### 长期方案（1-2 月）
1. 建立违禁词数据库
2. 定期自动更新机制
3. 社区共建词库

---

## 📝 配置示例

```yaml
# config.yaml
banned_words:
  # 检测策略
  strategy: "hybrid"  # local/api/hybrid
  
  # 本地词库
  local:
    enabled: true
    file: "./data/banned_words.json"
    update_interval: 7  # 天
  
  # API 配置
  api:
    provider: "aliyun"  # aliyun/tencent/netease
    access_key_id: "your_key"
    access_key_secret: "your_secret"
    region: "cn-shanghai"
    cache_ttl: 3600  # 缓存时间（秒）
  
  # 严重等级
  severity:
    high: ["互粉", "私信", "包下款"]     # 直接拒绝
    medium: ["贷款", "中介", "找我"]    # 警告
    low: ["点赞", "关注", "收藏"]       # 提示
```

---

## 💡 推荐行动

**江sir，我建议：**

1. **现在立即做**：扩充本地违禁词库（免费，立即生效）
2. **本周内做**：对接阿里云 API（成本低，效果好）
3. **下个月做**：建立自动更新机制

需要我帮你实现哪个方案？
