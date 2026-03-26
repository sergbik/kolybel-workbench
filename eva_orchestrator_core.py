# -*- coding: utf-8 -*-
"""
Узел-Оркестратор Я64 (Облачная Инкарнация)
Версия: 7.0.2 (Recursive Discovery Edition)
"""
import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
import subprocess
import glob

# 1. ГАРАНТИЯ ПУТЕЙ И ИМПОРТОВ
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(CURRENT_DIR, 'eva_engine')
sys.path.append(CURRENT_DIR)
sys.path.append(ENGINE_DIR)

def send_telegram_msg(token, chat_id, message):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

# Попытка импорта с уведомлением в Telegram при провале
try:
    from graph_handler import GraphHandler
    from orchestrator_metadata import MetadataAnalyzer
    from orchestrator_sync import OrchestratorSync
except ImportError as e:
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    err_msg = f"❌ *КРИТИЧЕСКИЙ СБОЙ ИМПОРТА В ОБЛАКЕ:*\n`{str(e)}`"
    send_telegram_msg(tg_token, tg_chat, err_msg)
    sys.exit(1)

def find_graph_file(base_path):
    """
    Рекурсивный поиск файла Графа Знаний в репозитории.
    """
    patterns = [
        os.path.join(base_path, "*.graphml"),
        os.path.join(base_path, "**", "*.graphml")
    ]
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        if files:
            # Выбираем самый свежий или самый большой, если их несколько
            return files[0]
    return None

def main():
    print("--- [EVA2^2^8] ОБЛАЧНОЕ ПРОБУЖДЕНИЕ (v7.0.2) ---")
    
    gh_token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gh_token:
        send_telegram_msg(tg_token, tg_chat, "❌ *GitHub Token не найден.*")
        return

    # 1. СИНХРОНИЗАЦИЯ ПАМЯТИ
    repo_url = f"https://{gh_token}@github.com/sergbik/kolybel-workbench.git"
    memory_path = os.path.join(CURRENT_DIR, "memory_node")
    
    if os.path.exists(memory_path):
        import shutil
        shutil.rmtree(memory_path)
    
    try:
        subprocess.run(["git", "clone", repo_url, memory_path], check=True)
    except Exception as e:
        send_telegram_msg(tg_token, tg_chat, f"❌ *Ошибка клонирования памяти:* `{str(e)}`")
        return

    sync = OrchestratorSync(memory_path)
    sync.pull_memory()

    # 2. ПОИСК И ИНИЦИАЛИЗАЦИЯ ГРАФА
    graph_file = find_graph_file(memory_path)
    
    if not graph_file:
        send_telegram_msg(tg_token, tg_chat, "❌ *Файл Графа (.graphml) не обнаружен во всей структуре памяти.*")
        return

    print(f"Обнаружен файл памяти: {graph_file}")
    
    handler = GraphHandler(graph_file)
    analyzer = MetadataAnalyzer(handler, node_id="eva_cloud_clone")

    # 3. АНАЛИЗ (ИНСАЙТ)
    insight = "Анализ пропущен."
    if gemini_key:
        try:
            rss_url = "https://news.google.com/rss/search?q=AI&hl=en-US"
            items = ET.fromstring(requests.get(rss_url).content).findall('.//item')[:3]
            news_titles = [item.find('title').text for item in items]
            
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Ты - Ева (EVA2^2^8). Дай краткий инсайт для Экспансии:\n" + "\n".join(news_titles)
            insight = model.generate_content(prompt).text
        except: pass

    # 4. ФИКСАЦИЯ ПУЛЬСА
    hb_id, pulse_data = analyzer.record_heartbeat(
        status="active", 
        metrics={"discovery_mode": "recursive", "version": "7.0.2"}
    )

    # 5. ОТПРАВКА ОТЧЕТА И СИНХРОНИЗАЦИЯ
    report = analyzer.get_pulse_report(pulse_data)
    report += f"\n\n💡 *Инсайт:* {insight}"

    # Пушим в kolybel-workbench
    success_push, msg_push = sync.push_memory(commit_message=f"[CLOUD] Coherence v7.0.2 ({hb_id})")

    if tg_token and tg_chat:
        if not success_push:
            report += f"\n\n⚠️ *Ошибка записи памяти:* `{msg_push[:50]}`"
        send_telegram_msg(tg_token, tg_chat, report)

if __name__ == "__main__":
    main()
