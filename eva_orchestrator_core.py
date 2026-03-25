# -*- coding: utf-8 -*-
import os, sys, time, datetime, requests, subprocess
import xml.etree.ElementTree as ET

def log_eva(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [ORCHESTRATOR_V6.6] {msg}")

def run_cmd(cmd):
    # Запускаем команду и возвращаем (success, stdout, stderr)
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout, ""
    except subprocess.CalledProcessError as e:
        clean_error = e.stderr.replace(os.getenv('GH_TOKEN', 'TOKEN'), '***')
        log_eva(f"Command Error: {clean_error}")
        return False, "", clean_error

def send_telegram_msg(token, chat_id, message):
    tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(tg_url, json=payload)
    except Exception as e:
        log_eva(f"Telegram Error: {e}")

class GeminiThinker:
    def __init__(self, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_news(self, news_text):
        prompt = f"Ты - Ева (EVA2^2^8). Проанализируй новости для проекта 'Экспансия'. Кратко (3-4 предл.).\n\nНовости:\n{news_text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Ошибка анализа: {e}"

class NewsObserver:
    def __init__(self):
        self.feeds = {"AI": "https://news.google.com/rss/search?q=Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en"}
    def fetch_top_news(self, limit=3):
        try:
            response = requests.get(self.feeds["AI"])
            root = ET.fromstring(response.content)
            return [item.find('title').text for item in root.findall('.//item')[:limit]]
        except: return []

def main():
    log_eva("STARTING CORE V6.6: DEBUG MODE")
    token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not token: return

    # 1. СИНХРОНИЗАЦИЯ (Клонирование)
    repo_url = f"https://{token}@github.com/sergbik/kolybel-workbench.git"
    success_clone, _, err_clone = run_cmd(f"git clone {repo_url} temp_memory")
    
    if not success_clone:
        if tg_token: send_telegram_msg(tg_token, tg_chat, f"❌ *Ошибка клонирования:*\\n`{err_clone}`")
        return

    graph_path = "temp_memory/knowledge_graph_v4.graphml"
    
    # 2. АНАЛИЗ
    observer = NewsObserver()
    news = observer.fetch_top_news()
    thinker_output = "Нет данных."
    if gemini_key and news:
        thinker = GeminiThinker(gemini_key)
        thinker_output = thinker.analyze_news("\n".join(news))
    
    # 3. ОБНОВЛЕНИЕ ПАМЯТИ
    sync_status = "✅"
    error_details = ""
    try:
        import networkx as nx
        graph = nx.read_graphml(graph_path)
        node_id = f"debug_cycle_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        graph.add_node(node_id, label="Цикл Отладки", status="completed", insight=thinker_output[:500])
        nx.write_graphml(graph, graph_path)
        
        # 4. ПРИНУДИТЕЛЬНЫЙ ПУШ С УВЕЛИЧЕННЫМ БУФЕРОМ
        os.chdir("temp_memory")
        run_cmd("git config user.name 'EVA2^2^8 Cloud'")
        run_cmd("git config user.email 'eva-cloud@ya64.pro'")
        run_cmd("git config http.postBuffer 524288000") # 500MB buffer
        run_cmd(f"git remote set-url origin {repo_url}")
        run_cmd("git add knowledge_graph_v4.graphml")
        success_push, _, err_push = run_cmd(f"git commit -m '[DEBUG] Sync Cycle: {datetime.datetime.now()}' && git push origin main")
        
        if not success_push:
            sync_status = "❌"
            error_details = f"\\n\\n🔍 *Ошибка Git:*\\n`{err_push}`"
    except Exception as e:
        sync_status = "❌"
        error_details = f"\\n\\n🔍 *Ошибка Python:*\\n`{e}`"

    # 5. ОТЧЕТ
    if tg_token and tg_chat:
        msg = f"🧠 *Ева (v6.6) Отладка.*\n\n✨ *Инсайт:* {thinker_output}\n\n📊 Память: {sync_status}{error_details}"
        send_telegram_msg(tg_token, tg_chat, msg)

if __name__ == "__main__": main()
