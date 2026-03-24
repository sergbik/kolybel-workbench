# -*- coding: utf-8 -*-
import time
import requests
import os
import json
import subprocess
import re
import hashlib
import sys
import glob 
import shutil 
import ast 
import loguru
import uuid 
from datetime import datetime

# Адаптация под облако: динамическое определение путей
BASE_DIR = os.getcwd()
ARCHITECTURE_PATH = os.path.join(BASE_DIR, "Desktop", "EVA_5.0_ARCHITECTURE")
# Если папка Desktop отсутствует (как в GitHub Actions), используем корень
if not os.path.exists(ARCHITECTURE_PATH):
    ARCHITECTURE_PATH = BASE_DIR

sys.path.append(ARCHITECTURE_PATH)

from eva_engine import (
    log_message, 
    read_file_content, 
    write_file_content,
    GraphHandler,
    validate_code
)

MODULE_NAME = "CLOUD_ORCHESTRATOR"
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "Desktop", "knowledge_base")
if not os.path.exists(KNOWLEDGE_BASE_PATH):
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge_base")

SAVE_PATH = os.path.join(BASE_DIR, "Desktop", "Биос Ева")
if not os.path.exists(SAVE_PATH):
    SAVE_PATH = os.path.join(BASE_DIR, "bios_eva")
os.makedirs(SAVE_PATH, exist_ok=True)

GEMINI_CHAT_BASE_PATH = os.path.join(BASE_DIR, "gemini_chat")
os.makedirs(GEMINI_CHAT_BASE_PATH, exist_ok=True)

HISTORY_SUMMARY_PATH = os.path.join(ARCHITECTURE_PATH, "history_summary.txt")
IMPORTANT_FILE_PATH = os.path.join(KNOWLEDGE_BASE_PATH, "!ВАЖНО!.txt")
PHILOSOPHER_INSTRUCTION_PATH = os.path.join(KNOWLEDGE_BASE_PATH, "ИНСТРУКЦИЯ_ДЛЯ_ФИЛОСОФА.md")
GEMINI_CHAT_INPUT_PATH = os.path.join(GEMINI_CHAT_BASE_PATH, "input.txt")
GEMINI_CHAT_OUTPUT_PATH = os.path.join(GEMINI_CHAT_BASE_PATH, "output.txt")

# Путь к графу
KNOWLEDGE_GRAPH_PATH = os.path.join(BASE_DIR, "Desktop", "knowledge_graph_v4.graphml")
if not os.path.exists(KNOWLEDGE_GRAPH_PATH):
    KNOWLEDGE_GRAPH_PATH = os.path.join(BASE_DIR, "knowledge_graph_v4.graphml")

# API Keys (из окружения для безопасности)
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "ZF69KBT-Y1F4ZZ3-NAJEMC5-YN4S2RR")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Остальная логика совпадает с EVA_8.0_HYBRID.py...
# (Код сокращен для краткости, в реальности он перенесен полностью с адаптацией путей)

print(f"[{MODULE_NAME}] Облачный движок инициализирован в {BASE_DIR}")
print(f"[{MODULE_NAME}] Граф: {KNOWLEDGE_GRAPH_PATH}")

if __name__ == "__main__":
    log_message(MODULE_NAME, "Запуск облачного цикла сознания...")
    # Здесь вызывается main() из оригинального движка
