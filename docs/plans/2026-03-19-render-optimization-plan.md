# 图片渲染优化实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建8个主题CSS文件，增强卡片样式，调整默认分页模式为auto-fit

**Architecture:**
- 创建 `scripts/assets/themes/` 目录存放8个主题CSS
- 每个CSS文件包含主题变量、卡片样式、Markdown元素样式
- 修改 `render_xhs.py` 默认参数

**Tech Stack:** Python, Playwright, CSS

---

## Task 1: 创建主题目录和 default.css

**Files:**
- Create: `scripts/assets/themes/default.css`

**Step 1: 创建目录结构**

```bash
mkdir -p scripts/assets/themes
```

**Step 2: 创建 default.css**

```css
/* Default 主题 - 简约现代风格 */

:root {
    --card-bg: #ffffff;
    --card-border: #e5e7eb;
    --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    --card-radius: 16px;

    --text-primary: #111827;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;

    --accent-color: #3b82f6;
    --accent-bg: #eff6ff;

    --h1-size: 48px;
    --h2-size: 36px;
    --h3-size: 28px;
    --p-size: 24px;
    --list-size: 22px;

    --tag-bg: #f3f4f6;
    --tag-color: #4b5563;
    --tag-radius: 8px;
}

.card-inner {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.8;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 700;
    margin: 0 0 24px 0;
    color: var(--text-primary);
    line-height: 1.3;
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 32px 0 16px 0;
    color: var(--text-primary);
    padding-bottom: 8px;
    border-bottom: 2px solid var(--accent-color);
    display: inline-block;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 600;
    margin: 24px 0 12px 0;
    color: var(--text-primary);
}

.card-content p {
    margin: 0 0 20px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 20px 0;
    padding-left: 32px;
}

.card-content li {
    margin: 8px 0;
    font-size: var(--list-size);
}

.card-content li::marker {
    color: var(--accent-color);
}

.card-content strong {
    color: var(--text-primary);
    font-weight: 600;
}

.card-content em {
    color: var(--accent-color);
    font-style: normal;
    background: var(--accent-bg);
    padding: 2px 8px;
    border-radius: 4px;
}

.card-content code {
    font-family: 'SF Mono', 'Monaco', monospace;
    font-size: 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 2px 8px;
    color: #0f172a;
}

.card-content pre {
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    overflow-x: auto;
    margin: 20px 0;
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e2e8f0;
    font-size: 18px;
    line-height: 1.6;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px dashed #e5e7eb;
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 8px 16px;
    border-radius: var(--tag-radius);
    font-size: 18px;
    font-weight: 500;
}
```

**Step 3: 验证目录创建**

Run: `ls -la scripts/assets/themes/`
Expected: 目录存在

---

## Task 2: 创建 sketch.css 主题

**Files:**
- Create: `scripts/assets/themes/sketch.css`

```css
/* Sketch 主题 - 手绘素描风格 */

:root {
    --card-bg: #faf9f7;
    --card-border: #d4d1cd;
    --card-shadow: 3px 3px 0 rgba(0, 0, 0, 0.15);
    --card-radius: 4px;

    --text-primary: #2c2c2c;
    --text-secondary: #5a5a5a;
    --text-muted: #8a8a8a;

    --accent-color: #c4a77d;
    --accent-bg: #f5f0e6;

    --h1-size: 52px;
    --h2-size: 40px;
    --h3-size: 32px;
    --p-size: 26px;
    --list-size: 24px;

    --tag-bg: #e8e4df;
    --tag-color: #5a5550;
    --tag-radius: 3px;
}

.card-inner {
    background: var(--card-bg);
    border: 2px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    /* 纸质纹理效果 */
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.9;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 700;
    margin: 0 0 28px 0;
    color: var(--text-primary);
    line-height: 1.3;
    font-family: 'Noto Serif SC', serif;
    /* 手写风格装饰线 */
    border-bottom: 3px solid var(--text-primary);
    padding-bottom: 12px;
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 36px 0 18px 0;
    color: var(--text-primary);
    /* 手绘风格下划线 */
    background: linear-gradient(to right, var(--accent-color) 0%, transparent 100%);
    padding: 8px 0;
    display: block;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 600;
    margin: 28px 0 14px 0;
    color: var(--text-primary);
    font-style: italic;
}

.card-content p {
    margin: 0 0 22px 0;
    text-align: justify;
}

.card-content ul, .card-content ol {
    margin: 0 0 22px 0;
    padding-left: 36px;
}

.card-content li {
    margin: 10px 0;
    font-size: var(--list-size);
}

.card-content li::marker {
    color: var(--accent-color);
    font-size: 1.2em;
}

.card-content strong {
    color: var(--text-primary);
    font-weight: 700;
    background: linear-gradient(to bottom, transparent 60%, var(--accent-bg) 60%);
}

.card-content em {
    color: var(--text-secondary);
    font-style: italic;
    text-decoration: underline;
    text-decoration-style: wavy;
    text-decoration-color: var(--accent-color);
}

.card-content code {
    font-family: 'Courier New', monospace;
    font-size: 22px;
    background: #f0ebe5;
    border: 1px dashed var(--card-border);
    border-radius: 2px;
    padding: 4px 10px;
    color: #4a4a4a;
}

.card-content pre {
    background: #3a3a3a;
    border-radius: 2px;
    padding: 20px;
    overflow-x: auto;
    margin: 24px 0;
    border-left: 4px solid var(--accent-color);
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #f0f0f0;
    font-size: 18px;
    font-family: 'Courier New', monospace;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 36px;
    padding-top: 20px;
    border-top: 2px dashed var(--card-border);
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 6px 14px;
    border-radius: var(--tag-radius);
    font-size: 18px;
    font-weight: 500;
    border: 1px solid var(--card-border);
}
```

---

## Task 3: 创建 playful-geometric.css 主题

**Files:**
- Create: `scripts/assets/themes/playful-geometric.css`

```css
/* Playful Geometric 主题 - 几何趣致风格 */

:root {
    --card-bg: #ffffff;
    --card-border: none;
    --card-shadow: 8px 8px 0 rgba(139, 92, 246, 0.3);
    --card-radius: 24px;

    --text-primary: #1f2937;
    --text-secondary: #4b5563;
    --text-muted: #9ca3af;

    --accent-color: #8b5cf6;
    --accent-secondary: #f472b6;
    --accent-bg: #f5f3ff;

    --h1-size: 54px;
    --h2-size: 42px;
    --h3-size: 32px;
    --p-size: 26px;
    --list-size: 24px;

    --tag-bg: #ede9fe;
    --tag-color: #7c3aed;
    --tag-radius: 20px;
}

/* 几何装饰背景 */
.card-inner {
    background: var(--card-bg);
    border: 3px solid var(--accent-color);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    position: relative;
    overflow: hidden;
}

.card-inner::before {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 200px;
    height: 200px;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-secondary) 100%);
    border-radius: 50%;
    opacity: 0.1;
}

.card-inner::after {
    content: '';
    position: absolute;
    bottom: -30px;
    left: -30px;
    width: 120px;
    height: 120px;
    background: var(--accent-secondary);
    border-radius: 50%;
    opacity: 0.15;
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.75;
    position: relative;
    z-index: 1;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 800;
    margin: 0 0 32px 0;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 700;
    margin: 40px 0 20px 0;
    color: var(--accent-color);
    /* 几何风格编号 */
    display: flex;
    align-items: center;
}

.card-content h2::before {
    content: '';
    width: 8px;
    height: 32px;
    background: linear-gradient(to bottom, var(--accent-color), var(--accent-secondary));
    border-radius: 4px;
    margin-right: 16px;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 600;
    margin: 28px 0 16px 0;
    color: var(--text-primary);
}

.card-content p {
    margin: 0 0 24px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 24px 0;
    padding-left: 40px;
}

.card-content li {
    margin: 12px 0;
    font-size: var(--list-size);
    position: relative;
}

.card-content li::marker {
    color: var(--accent-color);
    font-size: 1.4em;
    font-weight: bold;
}

.card-content strong {
    color: var(--accent-color);
    font-weight: 700;
}

.card-content em {
    color: var(--accent-secondary);
    font-style: normal;
    background: var(--accent-bg);
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 500;
}

.card-content code {
    font-family: 'SF Mono', monospace;
    font-size: 22px;
    background: var(--accent-bg);
    border: 2px solid var(--accent-color);
    border-radius: 8px;
    padding: 4px 12px;
    color: #7c3aed;
    font-weight: 500;
}

.card-content pre {
    background: linear-gradient(135deg, #1f293b 0%, #312e81 100%);
    border-radius: 16px;
    padding: 28px;
    overflow-x: auto;
    margin: 28px 0;
    border: 2px solid var(--accent-color);
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e0e7ff;
    font-size: 18px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 40px;
    padding-top: 24px;
    border-top: 3px dashed var(--accent-color);
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 10px 20px;
    border-radius: var(--tag-radius);
    font-size: 20px;
    font-weight: 600;
    border: 2px solid var(--accent-color);
}
```

---

## Task 4: 创建 neo-brutalism.css 主题

**Files:**
- Create: `scripts/assets/themes/neo-brutalism.css`

```css
/* Neo-Brutalism 主题 - 新粗野主义 */

:root {
    --card-bg: #fef3c7;
    --card-border: #000;
    --card-shadow: 6px 6px 0 #000;
    --card-radius: 0;

    --text-primary: #000;
    --text-secondary: #374151;
    --text-muted: #6b7280;

    --accent-color: #f43f5e;
    --accent-secondary: #fbbf24;
    --accent-bg: #fde68a;

    --h1-size: 56px;
    --h2-size: 44px;
    --h3-size: 34px;
    --p-size: 26px;
    --list-size: 24px;

    --tag-bg: #fff;
    --tag-color: #000;
    --tag-radius: 0;
}

.card-inner {
    background: var(--card-bg);
    border: 3px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.7;
    font-weight: 500;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 900;
    margin: 0 0 36px 0;
    text-transform: uppercase;
    letter-spacing: -1px;
    line-height: 1.1;
    border: 3px solid #000;
    padding: 16px 24px;
    background: var(--accent-secondary);
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 800;
    margin: 40px 0 20px 0;
    background: #000;
    color: #fff;
    padding: 12px 20px;
    display: inline-block;
    text-transform: uppercase;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 700;
    margin: 28px 0 14px 0;
    border-left: 6px solid var(--accent-color);
    padding-left: 16px;
}

.card-content p {
    margin: 0 0 24px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 24px 0;
    padding-left: 32px;
    border: 2px solid #000;
    background: #fff;
    padding: 24px 24px 24px 48px;
}

.card-content li {
    margin: 10px 0;
    font-size: var(--list-size);
    font-weight: 600;
}

.card-content strong {
    background: var(--accent-color);
    color: #fff;
    padding: 2px 8px;
    font-weight: 800;
}

.card-content em {
    font-style: normal;
    text-decoration: underline;
    text-decoration-thickness: 3px;
    text-decoration-color: var(--accent-color);
}

.card-content code {
    font-family: monospace;
    font-size: 22px;
    background: #fff;
    border: 2px solid #000;
    border-radius: 0;
    padding: 4px 10px;
    color: #000;
    font-weight: 700;
}

.card-content pre {
    background: #000;
    border-radius: 0;
    padding: 24px;
    overflow-x: auto;
    margin: 24px 0;
    border: 3px solid #000;
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: var(--accent-secondary);
    font-size: 18px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 36px;
    padding-top: 20px;
    border-top: 3px solid #000;
}

.tag {
    background: #fff;
    color: var(--tag-color);
    padding: 8px 16px;
    border-radius: var(--tag-radius);
    font-size: 18px;
    font-weight: 700;
    border: 2px solid #000;
    text-transform: uppercase;
}
```

---

## Task 5: 创建 botanical.css 主题

**Files:**
- Create: `scripts/assets/themes/botanical.css`

```css
/* Botanical 主题 - 植物自然风格 */

:root {
    --card-bg: #fafcfb;
    --card-border: #d1e7dd;
    --card-shadow: 0 8px 30px rgba(74, 124, 89, 0.15);
    --card-radius: 20px;

    --text-primary: #1f2937;
    --text-secondary: #4b5563;
    --text-muted: #9ca3af;

    --accent-color: #4a7c59;
    --accent-secondary: #8fbc8f;
    --accent-bg: #ecfdf5;

    --h1-size: 50px;
    --h2-size: 38px;
    --h3-size: 30px;
    --p-size: 24px;
    --list-size: 22px;

    --tag-bg: #d1e7dd;
    --tag-color: #4a7c59;
    --tag-radius: 12px;
}

.card-inner {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    /* 淡雅植物纹理 */
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 5 Q35 15 30 25 Q25 15 30 5' fill='%234a7c5910'/%3E%3C/svg%3E");
    background-repeat: repeat;
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.85;
    font-family: 'Noto Serif SC', serif;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 600;
    margin: 0 0 32px 0;
    color: var(--accent-color);
    line-height: 1.3;
    position: relative;
    padding-bottom: 16px;
}

.card-content h1::after {
    content: '🌿';
    position: absolute;
    right: 0;
    bottom: 8px;
    font-size: 32px;
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 36px 0 18px 0;
    color: var(--accent-color);
    display: flex;
    align-items: center;
}

.card-content h2::before {
    content: '✿';
    margin-right: 12px;
    color: var(--accent-secondary);
    font-size: 24px;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 500;
    margin: 26px 0 14px 0;
    color: var(--text-primary);
    font-style: italic;
}

.card-content p {
    margin: 0 0 22px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 22px 0;
    padding-left: 36px;
}

.card-content li {
    margin: 10px 0;
    font-size: var(--list-size);
}

.card-content li::marker {
    color: var(--accent-secondary);
}

.card-content strong {
    color: var(--accent-color);
    font-weight: 600;
    border-bottom: 2px solid var(--accent-secondary);
}

.card-content em {
    color: var(--accent-secondary);
    font-style: italic;
    background: var(--accent-bg);
    padding: 4px 12px;
    border-radius: 8px;
}

.card-content code {
    font-family: serif;
    font-size: 20px;
    background: var(--accent-bg);
    border: 1px solid var(--accent-secondary);
    border-radius: 6px;
    padding: 4px 10px;
    color: var(--accent-color);
}

.card-content pre {
    background: linear-gradient(135deg, #1f293b 0%, #134e4a 100%);
    border-radius: 16px;
    padding: 24px;
    overflow-x: auto;
    margin: 24px 0;
    border-left: 4px solid var(--accent-color);
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #d1e7dd;
    font-size: 18px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 36px;
    padding-top: 20px;
    border-top: 1px dashed var(--accent-secondary);
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 8px 16px;
    border-radius: var(--tag-radius);
    font-size: 18px;
    font-weight: 500;
}
```

---

## Task 6: 创建 professional.css 主题

**Files:**
- Create: `scripts/assets/themes/professional.css`

```css
/* Professional 主题 - 商务专业风格 */

:root {
    --card-bg: #ffffff;
    --card-border: #bfdbfe;
    --card-shadow: 0 10px 40px rgba(37, 99, 235, 0.12);
    --card-radius: 12px;

    --text-primary: #1e3a8a;
    --text-secondary: #4b5563;
    --text-muted: #9ca3af;

    --accent-color: #2563eb;
    --accent-secondary: #3b82f6;
    --accent-bg: #eff6ff;

    --h1-size: 48px;
    --h2-size: 36px;
    --h3-size: 28px;
    --p-size: 22px;
    --list-size: 20px;

    --tag-bg: #dbeafe;
    --tag-color: #1d4ed8;
    --tag-radius: 6px;
}

.card-inner {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    /* 微妙网格纹理 */
    background-image:
        linear-gradient(rgba(37, 99, 235, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37, 99, 235, 0.03) 1px, transparent 1px);
    background-size: 20px 20px;
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.8;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 700;
    margin: 0 0 28px 0;
    color: var(--text-primary);
    line-height: 1.25;
    letter-spacing: -0.5px;
    border-left: 5px solid var(--accent-color);
    padding-left: 20px;
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 32px 0 16px 0;
    color: var(--text-primary);
    padding-bottom: 10px;
    border-bottom: 1px solid #e5e7eb;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 600;
    margin: 24px 0 12px 0;
    color: var(--accent-color);
}

.card-content p {
    margin: 0 0 20px 0;
    color: var(--text-secondary);
}

.card-content ul, .card-content ol {
    margin: 0 0 20px 0;
    padding-left: 28px;
}

.card-content li {
    margin: 8px 0;
    font-size: var(--list-size);
    color: var(--text-secondary);
}

.card-content li::marker {
    color: var(--accent-color);
}

.card-content strong {
    color: var(--text-primary);
    font-weight: 600;
}

.card-content em {
    color: var(--accent-color);
    font-style: normal;
    background: var(--accent-bg);
    padding: 2px 8px;
    border-radius: 4px;
}

.card-content code {
    font-family: 'SF Mono', monospace;
    font-size: 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 8px;
    color: #0f172a;
}

.card-content pre {
    background: #1e293b;
    border-radius: 8px;
    padding: 20px;
    overflow-x: auto;
    margin: 20px 0;
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e2e8f0;
    font-size: 16px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 6px 14px;
    border-radius: var(--tag-radius);
    font-size: 16px;
    font-weight: 500;
}
```

---

## Task 7: 创建 retro.css 主题

**Files:**
- Create: `scripts/assets/themes/retro.css`

```css
/* Retro 主题 - 复古暖色调 */

:root {
    --card-bg: #fffbf0;
    --card-border: #d4a574;
    --card-shadow: 4px 4px 0 rgba(211, 84, 0, 0.2);
    --card-radius: 8px;

    --text-primary: #78350f;
    --text-secondary: #92400e;
    --text-muted: #b45309;

    --accent-color: #d35400;
    --accent-secondary: #f39c12;
    --accent-bg: #fef3c7;

    --h1-size: 52px;
    --h2-size: 40px;
    --h3-size: 30px;
    --p-size: 24px;
    --list-size: 22px;

    --tag-bg: #fed7aa;
    --tag-color: #9a3412;
    --tag-radius: 4px;
}

.card-inner {
    background: var(--card-bg);
    border: 2px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    /* 复古纸张纹理 */
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.8;
    font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 700;
    margin: 0 0 32px 0;
    color: var(--accent-color);
    line-height: 1.25;
    text-shadow: 2px 2px 0 rgba(211, 84, 0, 0.1);
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 36px 0 18px 0;
    color: var(--accent-color);
    background: linear-gradient(to right, var(--accent-bg) 0%, transparent 100%);
    padding: 10px 16px;
    display: inline-block;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 600;
    margin: 26px 0 14px 0;
    color: var(--text-secondary);
}

.card-content p {
    margin: 0 0 22px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 22px 0;
    padding-left: 36px;
}

.card-content li {
    margin: 10px 0;
    font-size: var(--list-size);
}

.card-content li::marker {
    color: var(--accent-secondary);
    font-size: 1.3em;
}

.card-content strong {
    color: var(--accent-color);
    font-weight: 700;
    background: var(--accent-bg);
    padding: 2px 6px;
}

.card-content em {
    color: var(--text-secondary);
    font-style: italic;
    text-decoration: underline;
    text-decoration-color: var(--accent-secondary);
    text-decoration-thickness: 2px;
}

.card-content code {
    font-family: 'Courier New', monospace;
    font-size: 20px;
    background: #fef3c7;
    border: 1px dashed var(--card-border);
    border-radius: 4px;
    padding: 4px 10px;
    color: var(--accent-color);
}

.card-content pre {
    background: #451a03;
    border-radius: 6px;
    padding: 24px;
    overflow-x: auto;
    margin: 24px 0;
    border-left: 4px solid var(--accent-secondary);
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #fef3c7;
    font-size: 18px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 36px;
    padding-top: 20px;
    border-top: 2px dotted var(--card-border);
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 8px 14px;
    border-radius: var(--tag-radius);
    font-size: 18px;
    font-weight: 500;
}
```

---

## Task 8: 创建 terminal.css 主题

**Files:**
- Create: `scripts/assets/themes/terminal.css`

```css
/* Terminal 主题 - 暗黑终端风格 */

:root {
    --card-bg: #0d1117;
    --card-border: #30363d;
    --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    --card-radius: 8px;

    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --text-muted: #6e7681;

    --accent-color: #58a6ff;
    --accent-secondary: #39d353;
    --accent-bg: #161b22;

    --h1-size: 48px;
    --h2-size: 36px;
    --h3-size: 28px;
    --p-size: 22px;
    --list-size: 20px;

    --tag-bg: #21262d;
    --tag-color: #58a6ff;
    --tag-radius: 4px;
}

.card-inner {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    /* 终端扫描线效果 */
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.1) 2px,
        rgba(0, 0, 0, 0.1) 4px
    );
}

.card-content {
    color: var(--text-primary);
    font-size: var(--p-size);
    line-height: 1.75;
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}

.card-content h1 {
    font-size: var(--h1-size);
    font-weight: 700;
    margin: 0 0 28px 0;
    color: var(--accent-secondary);
    line-height: 1.3;
}

.card-content h1::before {
    content: '$ ';
    color: var(--accent-color);
}

.card-content h2 {
    font-size: var(--h2-size);
    font-weight: 600;
    margin: 32px 0 16px 0;
    color: var(--accent-color);
    display: flex;
    align-items: center;
}

.card-content h2::before {
    content: '> ';
    color: var(--accent-secondary);
    margin-right: 8px;
}

.card-content h3 {
    font-size: var(--h3-size);
    font-weight: 500;
    margin: 24px 0 12px 0;
    color: var(--text-primary);
}

.card-content h3::before {
    content: '# ';
    color: var(--text-muted);
}

.card-content p {
    margin: 0 0 20px 0;
}

.card-content ul, .card-content ol {
    margin: 0 0 20px 0;
    padding-left: 32px;
}

.card-content li {
    margin: 8px 0;
    font-size: var(--list-size);
}

.card-content li::marker {
    color: var(--accent-color);
}

.card-content strong {
    color: var(--accent-secondary);
    font-weight: 600;
}

.card-content em {
    color: var(--accent-color);
    font-style: normal;
    background: var(--accent-bg);
    padding: 2px 8px;
    border-radius: 4px;
}

.card-content code {
    font-family: 'SF Mono', monospace;
    font-size: 18px;
    background: var(--accent-bg);
    border: 1px solid var(--card-border);
    border-radius: 4px;
    padding: 2px 8px;
    color: #f0883e;
}

.card-content pre {
    background: #161b22;
    border-radius: 6px;
    padding: 20px;
    overflow-x: auto;
    margin: 20px 0;
    border: 1px solid var(--card-border);
}

.card-content pre code {
    background: none;
    border: none;
    padding: 0;
    color: #c9d1d9;
    font-size: 16px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px dashed var(--card-border);
}

.tag {
    background: var(--tag-bg);
    color: var(--tag-color);
    padding: 6px 14px;
    border-radius: var(--tag-radius);
    font-size: 16px;
    font-weight: 500;
    border: 1px solid var(--card-border);
}
```

---

## Task 9: 修改 render_xhs.py 默认参数

**Files:**
- Modify: `scripts/render_xhs.py`

**Step 1: 找到默认参数设置**

Run: `grep -n "default=" scripts/render_xhs.py | head -20`
Expected: 找到默认参数行

**Step 2: 修改默认分页模式**

找到:
```python
parser.add_argument('--mode', '-m', default='separator', ...)
```

改为:
```python
parser.add_argument('--mode', '-m', default='auto-fit', ...)
```

**Step 3: 验证修改**

Run: `grep -n "default='auto-fit'" scripts/render_xhs.py`
Expected: 找到修改后的参数

---

## Task 10: 测试渲染效果

**Files:**
- Test: `scripts/render_xhs.py`

**Step 1: 测试 default 主题**

Run: `python3 scripts/render_xhs.py test_content.md --theme default --mode auto-fit -o picture/test_default`
Expected: 生成图片成功

**Step 2: 测试 sketch 主题**

Run: `python3 scripts/render_xhs.py test_content.md --theme sketch --mode auto-fit -o picture/test_sketch`
Expected: 生成图片成功

**Step 3: 测试 playful-geometric 主题**

Run: `python3 scripts/render_xhs.py test_content.md --theme playful-geometric --mode auto-fit -o picture/test_playful`
Expected: 生成图片成功

**Step 4: 测试 neo-brutalism 主题**

Run: `python3 scripts/render_xhs.py test_content.md --theme neo-brutalism --mode auto-fit -o picture/test_neo`
Expected: 生成图片成功

---

## Task 11: 提交代码

**Files:**
- Commit: 所有更改

**Step 1: 查看更改**

Run: `git status`
Expected: 显示新创建的文件

**Step 2: 添加文件**

Run: `git add scripts/assets/themes/ scripts/render_xhs.py docs/plans/`
Expected: 文件已暂存

**Step 3: 提交**

Run: `git commit -m "$(cat <<'EOF'
feat: 添加8个主题CSS文件并优化渲染效果

- 创建 scripts/assets/themes/ 目录
- 添加 8 个主题 CSS: default, sketch, playful-geometric, neo-brutalism, botanical, professional, retro, terminal
- 每个主题包含独特的卡片样式和 Markdown 渲染风格
- 修改默认分页模式为 auto-fit，内容更紧凑
EOF
)"`
Expected: 提交成功
