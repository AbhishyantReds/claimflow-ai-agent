---
title: ClaimFlow AI
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
pinned: false
license: mit
---

# ClaimFlow AI - Autonomous Insurance Claims Processor

An intelligent conversational AI agent that processes insurance claims end-to-end through natural dialogue. Built with LangGraph, ChromaDB, and GPT-4o.

## Features

- **Conversational Interface**: Natural chat-based claim submission
- **Auto-detection**: Automatically identifies claim type (motor/health/home)
- **RAG Integration**: Semantic policy retrieval using ChromaDB vector store
- **Database Layer**: SQLite for customers, policies, and claim history
- **Autonomous Processing**: 9-step automated evaluation pipeline

## Setup

**Required Secret**: Add your `OPENAI_API_KEY` in the Hugging Face Space settings.

## Tech Stack

LangGraph 1.0+ | GPT-4o | ChromaDB | SQLAlchemy | Gradio 6.5

## Author

**Abhishyant Reddy** - [GitHub](https://github.com/abhishyantreddy)
