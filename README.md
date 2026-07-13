# Resume Optimizer

AI 简历优化助手 — 基于 LLM 的智能简历分析与优化工具，7 天 MVP。

## 项目简介

上传你的个人简历，输入目标岗位 JD（职位描述），AI 自动分析匹配度并给出具体优化建议。

### 核心功能

- 自动解析 PDF/DOCX 简历，提取结构化信息
- 分析岗位 JD，识别技能要求、经验要求、关键词
- 多维度匹配度评分（技能、经验、学历）
- 输出具体优化建议（原文 → 改进版本 → 修改原因）
- 支持中英文简历和 JD
- 用户反馈收集（隐私安全）

### 技术栈

| 层 | 技术 |
|---|------|
| UI | Streamlit |
| 后端 | Python |
| LLM | DeepSeek API (OpenAI SDK 兼容) |
| 数据模型 | Pydantic v2 |
| Prompt 管理 | YAML 外置 |

### 项目结构

```
resume_optimizer/
├── app.py                  # Streamlit 入口
├── config.py               # 环境变量配置
├── models.py               # Pydantic 数据模型
├── requirements.txt        # Python 依赖
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── llm.py              # LLM Provider 抽象层
│   ├── parser.py           # PDF/DOCX 文件解析
│   └── analyzer.py         # 核心分析流水线
├── prompts/
│   ├── resume.yaml         # 简历解析 Prompt
│   ├── jd.yaml             # JD 解析 Prompt
│   └── analysis.yaml       # 匹配分析 Prompt
└── examples/
    ├── demo_resume.md      # 演示用简历
    └── demo_jd.md          # 演示用 JD
```

## 快速开始

### 1. 安装依赖

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 API Key

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY = "your-deepseek-api-key"
```

**macOS/Linux:**
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

获取 API Key: [DeepSeek API](https://platform.deepseek.com/)

可选环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEPSEEK_API_KEY` | (必填) | DeepSeek API 密钥 |
| `LLM_PROVIDER` | `deepseek` | LLM 提供商 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 模型名称 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API 地址 |

### 3. 启动

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501`

## 使用说明

1. **上传简历** — 点击左侧上传按钮，支持 PDF / DOCX 格式
2. **输入 JD** — 在右侧文本框粘贴目标岗位的职位描述
3. **开始分析** — 点击"开始分析"按钮，等待 AI 处理
4. **查看结果** — 查看匹配度评分、技能差距、优化建议
5. **提交反馈** — 点击 👍/👎 帮助优化产品

## 隐私说明

- 简历内容和 JD 内容仅用于本次分析，**不持久化存储**
- `feedback.log` 只记录反馈时间、反馈类型、用户备注
- **不记录**任何简历内容、JD 内容、姓名、联系方式等个人隐私数据
- 分析完成后所有临时文件自动清除

## 演示

`examples/` 目录包含演示用的简历和 JD 样本，可以直接在 app 中使用测试。

## 后续规划

- 支持更多 LLM Provider（OpenAI、Claude）
- 自动生成英文简历
- 自动生成 Cover Letter
- 面试问题生成
- 岗位匹配推荐
