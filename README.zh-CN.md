# Tap4-AI Crawler

本项目为 [Tap4.AI](https://tap4.ai) 网站收录系统提供网页数据结构化能力，基于 FastAPI 构建异步服务，集成 Pyppeteer 页面采集、内容截图、对象存储上传、LLM 内容解析与标签生成等关键流程。

[English](./README.md) | [简体中文](./README.zh-CN.md)

---

## 🧠 项目简介

该爬虫用于提取指定网站的信息，并结合大型语言模型（LLM）完成摘要、语言翻译与标签推荐，辅助 Tap4 AI 工具目录进行智能归类。

---

## 🚀 技术栈

| 技术 | 说明 |
|------|------|
| **FastAPI** | 提供 Web API 能力 |
| **Pyppeteer** | Headless 浏览器页面访问与截图 |
| **阿里云 OSS** | 对象存储服务，支持网页截图和缩略图上传 |
| **Google Generative AI API** | 网页结构化摘要与标签提取 |
| **dotenv** | 环境变量配置与管理 |
| **logging** | 全链路日志记录与调试支持 |
| **async/await** | 全异步异构任务处理框架 |

---

## 🗂️ 模块结构
```text
.
├── main_api.py                   # FastAPI 启动入口
├── website_crawler.py           # 网站访问逻辑与主爬虫类
├── util/
│   ├── common_util.py           # 公共字符串与摘要处理工具
│   ├── llm_util.py              # LLM 接入与内容处理
│   └── oss_util.py              # OSS 上传与缩略图生成
├── .env                         # API 密钥与系统提示词配置
├── README.md                    # 英文文档
├── README.zh-CN.md              # 中文文档
└── Dockerfile                   # Docker 构建配置
```

---

## 🔁 数据流与处理流程

1. 用户通过 POST 接口 `/site/crawl` 提交待采集网站 URL 与可选标签。
2. 程序使用 Pyppeteer 启动 headless Chromium 模拟访问网页，解析标题、描述、HTML 文本。
3. 生成网页截图，调用 OSS 上传原图与缩略图，获得公开链接。
4. 内容文本交由 LLM（如 Google API）进行摘要与标签提取。
5. 最终返回结构化的内容（图片、标签、摘要、多语言文本等）。


## **⚖️ License**
  

本项目基于 MIT 开源协议发布，详见 [LICENSE](./LICENSE)。