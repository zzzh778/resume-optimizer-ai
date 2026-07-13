# Resume Optimizer

## 项目简介

Resume Optimizer 是一个基于 LLM 的 AI 简历优化工具。

目标用户：
- 求职者
- 应届毕业生
- 需要针对岗位 JD 优化简历的人

核心价值：

用户上传个人简历，并输入目标岗位 JD。

系统通过 AI 分析：

1. 自动解析简历内容
2. 提取岗位需求
3. 分析简历与岗位匹配程度
4. 找出技能、经历、关键词差距
5. 生成具体优化建议
6. 提供原文与改写建议对比

目标：

7 天完成一个可运行 MVP。

---

# 技术栈

## 前端

Streamlit

要求：
- 单文件 UI
- 快速迭代
- 适合 MVP 验证


## 后端

Python


## LLM

当前：

DeepSeek API

调用方式：

OpenAI SDK 兼容接口

base_url:

https://api.deepseek.com


设计要求：

使用 Provider 抽象层。

未来支持：

- OpenAI
- Claude
- 其他兼容模型


禁止：

- langchain
- litellm
- 复杂中间层


---

# 项目结构


resume_optimizer/

├── app.py
├── config.py
├── models.py
├── requirements.txt
├── README.md
├── feedback.log

├── core/
│ ├── parser.py
│ ├── analyzer.py
│ └── llm.py

└── prompts/
├── resume.yaml
├── jd.yaml
└── analysis.yaml



---

# 模块职责


## app.py

Streamlit 唯一入口。

负责：

- 文件上传
- JD 输入
- 调用分析流程
- 展示结果
- 用户反馈


禁止：

不要写业务逻辑。


---

## config.py

统一管理配置。

读取环境变量：

- DEEPSEEK_API_KEY
- LLM_PROVIDER
- DEEPSEEK_MODEL


---

## models.py

定义 Pydantic 数据模型。

主要模型：

ResumeData

JDData

AnalysisResult


负责：

- 输入输出结构校验
- 数据转换
- Markdown 展示


---

## core/llm.py

LLM Provider 抽象。


结构：

BaseLLMProvider

↓

DeepSeekProvider


提供：

generate(prompt)->str


工厂：

create_llm_provider()


根据：

LLM_PROVIDER

选择具体实现。


---

## core/parser.py

文件解析模块。


支持：

- PDF
- DOCX


接口：

extract_text(file_path)


要求：

异常友好处理。


---

## core/analyzer.py

核心业务流程。


负责：

1. 加载 prompt
2. 调用 LLM
3. JSON 解析
4. Pydantic 校验
5. 分析结果生成


主要流程：

parse_resume()

parse_jd()

run_analysis()


---

# Prompt 管理原则


Prompt 必须外置。

存放：

prompts/*.yaml


禁止：

将 prompt 硬编码在 Python 中。


加载方式：

Python yaml.safe_load()


模板：

Python str.format()


不引入模板引擎。


---

# 用户反馈机制


目标：

收集 MVP 使用反馈。


规则：

只记录：

- 时间
- 是否有帮助
- 用户备注


不记录：

- 简历内容
- JD 内容
- 用户隐私


存储：

feedback.log

格式：

JSONL


示例：

{
"ts":"2026-07-13T10:30:00",
"type":"helpful",
"note":"建议精准"
}


---

# 开发原则


## 简单优先

这是 MVP。

避免：

- 过度设计
- 复杂架构
- 不必要依赖


## 可扩展

未来可以增加：

- 更多 LLM Provider
- 用户账号
- 数据库
- 简历模板生成
- 商业化功能


## 隐私优先

用户上传简历内容：

不持久化存储。

分析完成后释放。


---

# 当前阶段目标

完成一个：

可以运行

可以演示

可以给真实用户体验

的 AI 简历优化 MVP。