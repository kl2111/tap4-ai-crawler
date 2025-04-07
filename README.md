# Tap4 AI Crawler

Tap4 AI Crawler is an open-source web crawler developed by tap4.ai, designed to extract structured summaries from websites using modern browser automation and LLM-based summarization. It captures website metadata, screenshots, and generates rich descriptions, enabling effortless enrichment of AI tool directories.

English | [简体中文](./README.zh-CN.md)

⸻

## ✅ Features
	•	Extracts website title, description, and open graph metadata
	•	Captures full-page website screenshots
	•	Uses LLM to generate human-readable summaries
	•	Custom tag annotation and optional multi-language prompts
	•	Uploads images and thumbnails to Alibaba Cloud OSS
	•	Browser header randomized via global_agent_headers

⸻

## 🧠 Core Modules

Module	File	Description
Crawler Core	website_crawler.py	Coordinates scraping, screenshot, LLM, and upload process
API Server	main_api.py	FastAPI-based interface to trigger crawling
OSS Integration	util/oss_util.py	Handles image upload and thumbnail generation
LLM Interface	util/llm_util.py	Uses Google GenerativeModel for summarization
Utility Layer	util/common_util.py	Filename keys, formatting, helpers



⸻

## 🧰 Tech Stack
	•	Language: Python 3.12
	•	Web Framework: FastAPI
	•	Browser Automation: Pyppeteer
	•	LLM: Google GenerativeAI (via google.generativeai)
	•	Storage: Alibaba Cloud OSS (Object Storage Service)
	•	Headers: Rotating via global_agent_headers list



Response:

{
  "code": 0,
  "msg": "success",
  "data": {
    "title": "...",
    "description": "...",
    "summary": "...",
    "image_url": "...",
    "thumbnail_url": "..."
  }
}



⸻

##  🔁 Data Flow
```
[POST /site/crawl] ─▶ main_api.py
                  └─▶ website_crawler.py
                        ├─▶ launch browser (Pyppeteer)
                        ├─▶ extract title/meta & screenshot
                        ├─▶ call LLM summary
                        └─▶ upload to OSS (via oss_util)

```

⸻

## 📄 License

 [LICENSE](./LICENSE)