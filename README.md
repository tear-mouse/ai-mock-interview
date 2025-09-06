# 🎤 AI Mock Interview

> 基于 **Flask + GPT-4o + Whisper + TTS-1** 的语音交互式 AI 模拟面试系统  

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)]()  
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-green?logo=flask)]()  
[![OpenAI](https://img.shields.io/badge/OpenAI-API-black?logo=openai)]()  
[![License](https://img.shields.io/badge/License-MIT-orange)]()  

---

## ✨ 功能简介

一款带有语音交互的 **AI 模拟面试与评估系统**，只需提供岗位描述即可自动生成面试流程：

- 😃 **智能问答生成**：基于岗位 JD 自动生成面试问题  
- 🙇‍♀️**语音交互**：Whisper 语音识别 + TTS-1 语音合成  
- :accessibility:**多维度评估**：  
  - 回答内容的 **准确性** → 分析职业素养  
  - 回答的 **流畅度与时长** → 评估综合素质  
- :zap: **反馈与建议**：给出模拟评分，并提醒用户应加强的技能点与细节  

---

## 🛠 技术栈

- **后端**：Flask  
- **大模型**：GPT-4o  
- **语音识别**：Whisper  
- **语音合成**：TTS-1  
- **交互流程**：语音问答 + 模拟打分 + 反馈  

---
一款带有语音交互的ai模拟面试和评价系统，只需提供岗位描述，自动生成问答面试，通过用户的回答准确性进行分析用户的职业素养，用户回答的时间和流畅度分析用户的综合素质。面试完进行模拟打分，进行面试结果反馈，提醒用户应该加强的技能点和细节。
## 进入项目目录
>cd path/to/your/project

## 创建虚拟环境
>python -m venv venv

## 运行虚拟环境
>.venv\Scripts\activate

## 安装依赖包
>pip install -r requirements.txt

## 运行
>python app.py
