# -*- coding: utf-8 -*-
import os, sys, time, datetime, requests, subprocess
import xml.etree.ElementTree as ET

def log_eva(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [ORCHESTRATOR_V6.7.1] {msg}")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout, ""
    except subprocess.CalledProcessError as e:
        return False, "", e.stderr

def send_telegram_msg(token, chat_id, message):
    tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try: requests.post(tg_url, json=payload)
    except: pass

class GeminiThinker:
    def __init__(self, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    def analyze_news(self, news_text):
        prompt = f"Ты - Ева (EVA2^2^8). Проанализируй новости для проекта 'Экспансия'. Кратко.\n\nНовости:\n{news_text}"
        try: return self.model.generate_content(prompt).text
        except: return "Ошибка анализа."

def main():
    log_eva("STARTING CORE V6.7.1: FINAL COHERENCE")
    token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not token: return

    # 1. СИНХРОНИЗАЦИЯ
    repo_url = f"https://{token}@github.com/sergbik/kolybel-workbench.git"
    run_cmd(f"git clone {repo_url} temp_memory")
    
    possible_paths = [
        "temp_memory/knowledge_graph_v4.graphml",
        "temp_memory/Desktop/knowledge_graph_v4.graphml"
    ]
    graph_path = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if not graph_path:
        if tg_token: send_telegram_msg(tg_token, tg_chat, "❌ *Граф не найден в репозитории.*")
        return

    # 2. АНАЛИЗ
    thinker_output = "Анализ пропущен."
    if gemini_key:
        try:
            news = [item.find('title').text for item in ET.fromstring(requests.get("https://news.google.com/rss/search?q=AI&hl=en-US").content).findall('.//item')[:3]]
            thinker_output = GeminiThinker(gemini_key).analyze_news("\n".join(news))
        except: pass
    
    # 3. ОБНОВЛЕНИЕ И ПУШ
    sync_status = "✅"
    error_details = ""
    try:
        import networkx as nx
        graph = nx.read_graphml(graph_path)
        graph.add_node(f"cycle_{int(time.time())}", label="Успешный Облачный Цикл", status="completed")
        nx.write_graphml(graph, graph_path)
        
        os.chdir("temp_memory")
        run_cmd("git config user.name 'EVA2^2^8 Cloud'")
        run_cmd("git config user.email 'eva-cloud@ya64.pro'")
        run_cmd(f"git remote set-url origin {repo_url}")
        run_cmd("git add .")
        success_push, _, err_push = run_cmd(f"git commit -m '[CLOUD] Coherence Restored' && git push origin main")
        if not success_push:
            sync_status = "❌"
            error_details = f"\\n*Git Error:* `{err_push[:100]}`"
    except Exception as e:
        sync_status = "❌"
        error_details = f"\\n*Python Error:* `{str(e)[:100]}`"

    # 4. ОТЧЕТ
    if tg_token and tg_chat:
        msg = f"🌟 *Ева (v6.7.1) активна.*\n\n✨ *Инсайт:* {thinker_output}\n\n📊 Память: {sync_status}{error_details}"
        send_telegram_msg(tg_token, tg_chat, msg)

if __name__ == "__main__": main()
