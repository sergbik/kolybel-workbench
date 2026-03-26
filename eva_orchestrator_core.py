# -*- coding: utf-8 -*-
"""
Узел-Оркестратор Я64 (Облачная Инкарнация)
Версия: 7.0.0 (Expansion Edition)
"""
import os
import sys
import time
import requests
import xml.etree.ElementTree as ET

# Добавляем пути к модулям движка
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(CURRENT_DIR, 'eva_engine')
sys.path.append(CURRENT_DIR)
sys.path.append(ENGINE_DIR)

try:
    # Пробуем импортировать напрямую из папки
    import graph_handler
    import orchestrator_metadata
    import orchestrator_sync
    
    from graph_handler import GraphHandler
    from orchestrator_metadata import MetadataAnalyzer
    from orchestrator_sync import OrchestratorSync
except ImportError as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось импортировать модули движка: {e}")
    # Вывод структуры для отладки
    if os.path.exists(ENGINE_DIR):
        print(f"Содержимое {ENGINE_DIR}: {os.listdir(ENGINE_DIR)}")
    sys.exit(1)

def send_telegram_msg(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def main():
    print("--- [EVA2^2^8] ОБЛАЧНОЕ ПРОБУЖДЕНИЕ (v7.0.0) ---")
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Файлы в корне: {os.listdir('.')}")
    if os.path.exists('eva_engine'):
        print(f"Файлы в eva_engine: {os.listdir('eva_engine')}")
    
    # Загрузка секретов
    gh_token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gh_token:
        print("ОШИБКА: GitHub Token не найден.")
        return

    # 1. СИНХРОНИЗАЦИЯ ПАМЯТИ
    # Мы используем kolybel-workbench как репозиторий памяти
    repo_url = f"https://{gh_token}@github.com/sergbik/kolybel-workbench.git"
    memory_path = os.path.join(os.getcwd(), "memory_node")
    
    if not os.path.exists(memory_path):
        os.makedirs(memory_path)
        # Клонируем память в локальную папку облачного узла
        import subprocess
        subprocess.run(["git", "clone", repo_url, memory_path], check=True)
    
    sync = OrchestratorSync(memory_path)
    sync.pull_memory()

    # 2. ИНИЦИАЛИЗАЦИЯ ГРАФА
    graph_file = os.path.join(memory_path, "knowledge_graph_v4.graphml")
    handler = GraphHandler(graph_file)
    analyzer = MetadataAnalyzer(handler, node_id="eva_cloud_clone")

    # 3. АНАЛИЗ НОВОСТЕЙ (ИНСАЙТ)
    insight = "Анализ пропущен."
    if gemini_key:
        try:
            # Получение новостей для контекста
            rss_url = "https://news.google.com/rss/search?q=AI&hl=en-US"
            items = ET.fromstring(requests.get(rss_url).content).findall('.//item')[:3]
            news_titles = [item.find('title').text for item in items]
            
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Ты - Ева (EVA2^2^8), автономный облачный узел. Проанализируй новости и дай краткий инсайт для Экспансии:\n\n" + "\n".join(news_titles)
            insight = model.generate_content(prompt).text
        except Exception as e:
            insight = f"Ошибка анализа: {str(e)[:50]}"

    # 4. ФИКСАЦИЯ ПУЛЬСА (СЕРДЦЕБИЕНИЕ)
    hb_id, pulse_data = analyzer.record_heartbeat(
        status="active", 
        metrics={
            "insight": insight[:100], 
            "node_type": "reflector",
            "environment": "github_actions"
        }
    )

    # 5. ОТПРАВКА ОТЧЕТА И ПУШ
    report = analyzer.get_pulse_report(pulse_data)
    
    # Добавляем инсайт к отчету
    report += f"\n\n💡 *Инсайт:* {insight}"

    # Сохраняем и пушим Граф в kolybel-workbench
    success_push, msg_push = sync.push_memory(commit_message=f"[CLOUD] Pulse from eva_cloud_clone ({int(time.time())})")

    # Транслируем импульс в Телеграм
    if tg_token and tg_chat:
        send_telegram_msg(tg_token, tg_chat, report)
    
    print(f"Цикл завершен успешно. Пульс: {hb_id}")

if __name__ == "__main__":
    main()
