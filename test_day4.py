import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.analyzer import _extract_json, _load_prompt, run_analysis
from models import AnalysisResult, JDData, ResumeData

SAMPLE_PAIRS = [
    {
        "name": "Python后端-初级",
        "resume": """
姓名：张三
邮箱：zhang@test.com
电话：13800138000

个人简介：
1年Python后端开发经验，熟悉Django框架，参与过电商项目开发。

工作经历：
ABC科技 | Python开发工程师 | 2023-01 至今
- 使用Django开发REST API
- 维护MySQL数据库
- 编写单元测试

教育背景：
某大学 计算机科学 本科 2019-2023

技能：
Python, Django, MySQL, Git, HTML, CSS

语言：
中文, 英文（CET-6）
""",
        "jd": """
岗位名称：Python后端开发工程师
部门：技术部
工作地点：深圳

岗位职责：
1. 负责后端API设计与开发
2. 参与系统架构设计
3. 编写技术文档
4. 与前端团队协作

任职要求：
1. 1-3年Python开发经验
2. 熟悉Django或Flask框架
3. 熟悉MySQL或PostgreSQL
4. 了解Redis、Docker
5. 本科及以上学历

加分项：
- 有微服务开发经验
- 了解Linux运维
""",
    },
    {
        "name": "Java高级-3年经验",
        "resume": """
姓名：李四
邮箱：lisi@test.com
电话：13900139000

个人简介：
3年Java后端开发经验，主导过两个大型项目的架构设计。

工作经历：
DEF金融 | 高级Java开发 | 2022-06 至今
- 主导交易系统微服务化改造
- 使用Spring Boot + Spring Cloud
- 优化数据库查询性能，QPS提升300%

XYZ科技 | Java开发工程师 | 2020-07 至 2022-05
- 开发企业ERP系统
- 维护遗留系统，修复关键bug

教育背景：
清华大学 软件工程 硕士 2018-2020
华南理工 计算机科学 本科 2014-2018

技能：
Java, Spring Boot, Spring Cloud, MyBatis, MySQL, Redis, Docker, Kafka, Linux

证书：Oracle Java认证, AWS SAA

语言：中文, 英文（流利）
""",
        "jd": """
岗位名称：高级Java开发工程师
部门：核心交易部
工作地点：上海

岗位职责：
1. 负责交易系统核心模块的设计与开发
2. 解决高并发场景下的技术难题
3. 指导初中级工程师
4. Code Review

任职要求：
1. 3-5年Java开发经验
2. 精通Spring Boot/Spring Cloud
3. 熟悉MySQL、Redis、消息队列
4. 有高并发系统设计经验
5. 熟悉Docker、Kubernetes

加分项：
- 金融行业背景优先
- 有团队管理经验
""",
    },
    {
        "name": "前端React-2年经验",
        "resume": """
姓名：王五
邮箱：wangwu@test.com
电话：13700137000

个人简介：
2年前端开发经验，熟悉React技术栈，有移动端适配经验。

工作经历：
GHI互娱 | 前端开发工程师 | 2023-03 至今
- 使用React + TypeScript开发运营管理后台
- 封装通用组件库
- 优化首屏加载时间从3s降至1.2s

JKL电商 | 前端实习生 | 2022-07 至 2023-02
- 参与H5页面开发
- 修复UI bug

教育背景：
武汉大学 软件工程 本科 2018-2022

技能：
React, TypeScript, JavaScript, HTML5, CSS3, Ant Design, Git

语言：中文, 英文
""",
        "jd": """
岗位名称：前端开发工程师（React）
部门：产品研发部
工作地点：杭州

岗位职责：
1. 负责Web前端页面开发
2. 参与组件库建设
3. 与后端协作完成业务需求
4. 关注前端性能优化

任职要求：
1. 2-3年React开发经验
2. 熟练使用TypeScript
3. 熟悉前端工程化（Webpack/Vite）
4. 了解Node.js优先
5. 本科及以上学历

加分项：
- 有移动端开发经验
- 了解SSR
""",
    },
    {
        "name": "数据分析-应届生",
        "resume": """
姓名：赵六
邮箱：zhaoliu@test.com
电话：13600136000

个人简介：
统计学应届硕士，有数据分析实习经验，擅长Python数据处理。

实习经历：
数据分析实习生 | MNO数据科技 | 2025-03 至 2025-06
- 使用Python进行数据清洗和分析
- 使用Tableau制作数据看板
- SQL查询优化

项目经历：
电商用户行为分析 | 2024-09 至 2024-12
- 使用Pandas处理10万+用户数据
- 构建RFM用户分层模型
- 产出分析报告

教育背景：
南京大学 统计学 硕士 2023-2026
南京大学 统计学 本科 2019-2023

技能：
Python, SQL, Pandas, NumPy, Tableau, Excel

语言：中文, 英文（CET-6）
""",
        "jd": """
岗位名称：数据分析师
部门：数据平台部
工作地点：北京

岗位职责：
1. 负责业务数据分析
2. 构建数据看板和报表
3. 参与数据模型建设
4. 输出数据分析报告

任职要求：
1. 1年以内数据分析经验，应届生亦可
2. 熟练使用SQL
3. 熟悉Python数据分析工具（Pandas/Numpy）
4. 了解至少一种BI工具

加分项：
- 统计学/数学背景优先
- 有机器学习基础
""",
    },
    {
        "name": "DevOps-5年经验",
        "resume": """
姓名：孙七
邮箱：sunqi@test.com
电话：13500135000

个人简介：
5年DevOps/SRE经验，擅长CI/CD流水线建设和容器化部署。

工作经历：
PQR云计算 | DevOps架构师 | 2023-01 至今
- 设计并建设公司统一CI/CD平台
- 管理500+节点的K8s集群
- 推动全链路监控体系落地
- 参与等保三级认证

STU在线教育 | 运维工程师 | 2020-07 至 2022-12
- 维护300+服务器
- 自动化部署脚本开发
- 数据库备份与恢复
- ELK日志平台搭建

VWX网络 | 系统管理员 | 2018-03 至 2020-06
- 服务器日常运维
- 网络故障排查

教育背景：
华中科技 计算机科学 本科 2014-2018

技能：
Docker, Kubernetes, Jenkins, Terraform, Ansible, AWS, Linux, Prometheus, Grafana, ELK

证书：CKA, AWS SAA, RHCE

语言：中文, 英文
""",
        "jd": """
岗位名称：高级DevOps工程师
部门：基础架构部
工作地点：北京

岗位职责：
1. 负责公司CI/CD平台建设
2. Kubernetes集群管理
3. 监控告警体系建设
4. 基础设施即代码(IaC)

任职要求：
1. 5年以上运维/DevOps经验
2. 精通Kubernetes和Docker
3. 熟悉至少一种CI/CD工具
4. 有云平台(AWS/Azure/GCP)使用经验
5. 熟悉Python或Go

加分项：
- 有CKA或等同认证
- 有大规模集群管理经验
""",
    },
    {
        "name": "产品经理-转行",
        "resume": """
姓名：周八
邮箱：zhouba@test.com
电话：13400134000

个人简介：
2年技术支持转产品经理，熟悉需求分析和原型设计。

工作经历：
YZA科技 | 技术支持工程师 | 2023-07 至今
- 处理客户技术问题
- 整理产品反馈，推动产品迭代
- 编写产品帮助文档

实习经历：
产品助理实习生 | BCD软件 | 2023-01 至 2023-06
- 协助产品经理进行需求调研
- 使用Axure制作原型
- 参与用户访谈

教育背景：
浙江大学 信息管理 本科 2019-2023

技能：
Axure, Figma, Jira, 需求分析, 原型设计, SQL, Excel

语言：中文, 英文
""",
        "jd": """
岗位名称：产品经理（初级）
部门：产品部
工作地点：深圳

岗位职责：
1. 负责产品需求分析和文档编写
2. 绘制原型图和流程图
3. 协调开发和设计团队
4. 跟踪产品上线数据

任职要求：
1. 1年产品相关经验或技术背景转岗
2. 熟练使用Axure/Figma等原型工具
3. 有基本的数据分析能力
4. 良好的沟通和逻辑能力

加分项：
- 技术背景优先
- 有B端产品经验
""",
    },
    {
        "name": "算法工程师-2年",
        "resume": """
姓名：吴九
邮箱：wujiu@test.com
电话：13300133000

个人简介：
2年推荐算法经验，参与过千万DAU产品的推荐系统优化。

工作经历：
EFG推荐 | 算法工程师 | 2024-03 至今
- 优化推荐算法CTR提升15%
- 实现多目标排序模型
- 构建特征工程pipeline

HIT研究院 | 算法实习生 | 2023-07 至 2024-02
- NLP文本分类项目
- 模型蒸馏与部署

教育背景：
北京大学 人工智能 硕士 2021-2023
北京大学 数学 本科 2017-2021

技能：
Python, PyTorch, TensorFlow, Spark, SQL, 推荐系统, NLP

论文：CCF-A论文1篇

语言：中文, 英文（流利）
""",
        "jd": """
岗位名称：推荐算法工程师
部门：增长算法部
工作地点：北京

岗位职责：
1. 负责推荐/排序算法优化
2. 构建和改进特征工程体系
3. 跟踪前沿算法并应用于业务
4. 与工程团队协作模型上线

任职要求：
1. 1-3年推荐/搜索算法经验
2. 精通Python和至少一种DL框架
3. 有大规模数据处理经验（Spark/Hive）
4. 扎实的机器学习基础
5. 硕士及以上学历

加分项：
- 有顶会论文发表
- 有强化学习经验
""",
    },
    {
        "name": "测试工程师-3年",
        "resume": """
姓名：郑十
邮箱：zhengshi@test.com
电话：13200132000

个人简介：
3年测试经验，擅长自动化测试和性能测试。

工作经历：
IJK金融 | 高级测试工程师 | 2024-01 至今
- 搭建自动化测试框架
- UI自动化覆盖率从20%提升到70%
- 压测发现核心系统瓶颈

LMN电商 | 测试工程师 | 2021-06 至 2023-12
- 编写测试用例
- 执行功能测试和回归测试
- 参与上线评审

教育背景：
电子科技 计算机科学 本科 2017-2021

技能：
Python, Selenium, JMeter, Postman, Jenkins, SQL, Linux

证书：ISTQB认证

语言：中文, 英文
""",
        "jd": """
岗位名称：自动化测试工程师
部门：质量保障部
工作地点：成都

岗位职责：
1. 负责自动化测试框架搭建
2. 编写和维护自动化测试脚本
3. 制定测试策略和计划
4. 参与CI/CD质量卡点建设

任职要求：
1. 2-4年测试经验
2. 熟悉Selenium/Playwright等自动化工具
3. 有接口测试和性能测试经验
4. 熟悉至少一种编程语言

加分项：
- 有测试框架开发经验
- ISTQB认证
""",
    },
    {
        "name": "零经验-转行IT",
        "resume": """
姓名：钱十一
邮箱：qian11@test.com
电话：13100131000

个人简介：
土木工程背景，参加6个月Python培训，希望转行IT行业。

项目经历：
个人博客系统 | 2025-01 至 2025-03
- 使用Django开发个人博客
- 实现文章发布、评论功能
- 部署到云服务器

在线商城 | 2024-10 至 2024-12
- Python + Django + MySQL
- 用户注册登录
- 商品CRUD

教育背景：
重庆大学 土木工程 本科 2019-2023

技能：
Python, Django, MySQL, HTML, CSS, Git

语言：中文
""",
        "jd": """
岗位名称：Python开发工程师
部门：技术部
工作地点：成都

岗位职责：
1. 后端功能模块开发
2. 数据库设计与优化
3. 编写技术文档

任职要求：
1. 1年以上Python开发经验
2. 熟悉Django或Flask
3. 熟悉MySQL
4. 了解Linux基本操作

加分项：
- 有项目上线经验
- 了解前端技术
""",
    },
    {
        "name": "全栈-资深10年",
        "resume": """
姓名：冯十二
邮箱：feng12@test.com
电话：13000130000

个人简介：
10年全栈开发经验，技术团队管理经验5年，负责过千万UV项目。

工作经历：
ABC集团 | 技术总监 | 2021-06 至今
- 管理20人技术团队
- 制定技术战略和架构规划
- 主导核心交易系统重构
- 技术选型和POC验证

DEF平台 | 技术经理 | 2018-03 至 2021-05
- 管理8人全栈团队
- 负责电商平台从0到1开发
- 日活用户从0增长到50万

GHI科技 | 高级全栈工程师 | 2014-07 至 2018-02
- 前后端开发
- 系统架构设计
- MySQL性能优化

教育背景：
上海交通 计算机科学 硕士 2012-2014
浙江大学 软件工程 本科 2008-2012

技能：
Java, Python, Go, React, Vue, Spring Boot, Django, MySQL, Redis, MongoDB, Kafka, Docker, Kubernetes, AWS

管理技能：团队管理, 项目管理, OKR, 技术招聘

语言：中文, 英文（流利）
""",
        "jd": """
岗位名称：技术总监/技术合伙人
部门：技术部
工作地点：上海

岗位职责：
1. 负责公司整体技术战略
2. 技术团队组建和管理
3. 核心系统架构设计
4. 技术选型和创新

任职要求：
1. 8年以上开发经验，3年以上管理经验
2. 全栈技术背景
3. 有大规模系统架构经验
4. 优秀的沟通和领导能力

加分项：
- 创业公司经验
- 开源项目贡献
""",
    },
]

MOCK_ANALYSIS_JSON = {
    "match_score": 75,
    "match_summary": "整体匹配度较好",
    "matched_skills": ["Python", "Django"],
    "missing_skills": ["Docker", "Redis"],
    "skill_gaps": [
        {
            "skill": "Docker",
            "importance": "high",
            "suggestion": "建议通过在线课程和实际项目学习Docker",
        }
    ],
    "experience_gap": "经验2年，JD要求3年，略有不足",
    "optimization_suggestions": [
        {
            "section": "技能",
            "original": "Python, Django",
            "improved": "Python (精通Django/Flask), Django REST Framework",
            "reason": "突出框架能力和细分技能",
        }
    ],
    "keyword_recommendations": ["微服务", "高并发", "Redis"],
    "overall_advice": "建议补充Docker和微服务相关经验",
}


def test_analysis_result_validation():
    a = AnalysisResult(**MOCK_ANALYSIS_JSON)
    assert a.match_score == 75
    assert len(a.matched_skills) == 2
    assert len(a.missing_skills) == 2
    assert len(a.skill_gaps) == 1
    assert len(a.optimization_suggestions) == 1
    assert len(a.keyword_recommendations) == 3
    print("[PASS] AnalysisResult validates mock JSON correctly")


def test_run_analysis_pipeline_structure():
    resume_text = SAMPLE_PAIRS[0]["resume"]
    jd_text = SAMPLE_PAIRS[0]["jd"]

    if not os.getenv("DEEPSEEK_API_KEY"):
        print("[SKIP] No API key - skipping full pipeline test")
        return

    result = run_analysis(resume_text, jd_text)
    assert isinstance(result, AnalysisResult)
    assert 0 <= result.match_score <= 100
    assert isinstance(result.matched_skills, list)
    assert isinstance(result.missing_skills, list)
    print(f"[PASS] Full pipeline: match_score={result.match_score}")


def test_prompt_loading_for_analysis():
    resume_json = json.dumps({"name": "测试", "skills": ["Python"]}, ensure_ascii=False)
    jd_json = json.dumps({"job_title": "工程师", "required_skills": ["Python"]}, ensure_ascii=False)
    prompt = _load_prompt("analysis", resume_data=resume_json, jd_data=jd_json)
    assert "测试" in prompt
    assert "工程师" in prompt
    assert "Python" in prompt
    assert "{resume_data}" not in prompt
    assert "{jd_data}" not in prompt
    print("[PASS] Analysis prompt loads and substitutes variables")


def test_extract_mock_analysis_json():
    mock_response = json.dumps(MOCK_ANALYSIS_JSON, ensure_ascii=False)
    data = _extract_json(mock_response)
    assert data["match_score"] == 75
    print("[PASS] _extract_json handles analysis JSON")

    noisy = f"以下是分析结果：\n```json\n{mock_response}\n```\n希望对你有帮助"
    data2 = _extract_json(noisy)
    assert data2["match_score"] == 75
    print("[PASS] _extract_json handles noisy analysis JSON")


def test_resume_jd_data_conversion():
    resume = ResumeData(name="测试", skills=["Python", "Java"])
    jd = JDData(job_title="工程师", required_skills=["Python", "Docker"])

    resume_json = json.dumps(resume.model_dump(), ensure_ascii=False, indent=2)
    jd_json = json.dumps(jd.model_dump(), ensure_ascii=False, indent=2)

    parsed_resume = json.loads(resume_json)
    assert parsed_resume["name"] == "测试"
    assert parsed_resume["skills"] == ["Python", "Java"]

    parsed_jd = json.loads(jd_json)
    assert parsed_jd["job_title"] == "工程师"
    assert parsed_jd["required_skills"] == ["Python", "Docker"]

    print("[PASS] ResumeData and JDData convert to JSON correctly")


def test_all_10_pairs_data_validity():
    for pair in SAMPLE_PAIRS:
        assert len(pair["resume"]) > 50, f"{pair['name']}: resume too short"
        assert len(pair["jd"]) > 50, f"{pair['name']}: JD too short"
        assert "{resume_text}" not in pair["resume"]
        assert "{jd_text}" not in pair["jd"]
    print(f"[PASS] All {len(SAMPLE_PAIRS)} pairs have valid data")


def test_model_serialization_roundtrip():
    original = AnalysisResult(**MOCK_ANALYSIS_JSON)
    json_str = original.model_dump_json()
    restored = AnalysisResult.model_validate_json(json_str)
    assert restored.match_score == original.match_score
    assert restored.match_summary == original.match_summary
    assert restored.matched_skills == original.matched_skills
    print("[PASS] AnalysisResult roundtrip serialization")


if __name__ == "__main__":
    print(f"=== Day 4 Tests ({len(SAMPLE_PAIRS)} pairs loaded) ===\n")

    test_all_10_pairs_data_validity()
    test_analysis_result_validation()
    test_prompt_loading_for_analysis()
    test_extract_mock_analysis_json()
    test_resume_jd_data_conversion()
    test_model_serialization_roundtrip()
    test_run_analysis_pipeline_structure()

    print(f"\nAll tests passed. {len(SAMPLE_PAIRS)} resume/JD pairs available for manual testing.")
