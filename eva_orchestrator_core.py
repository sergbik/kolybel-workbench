# -*- coding: utf-8 -*-
import os, sys, time, datetime, requests
import xml.etree.ElementTree as ET
from cloud_mcp_client import CloudMCPClient

def log_eva(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [ORCHESTRATOR] {msg}")

def send_telegram_msg(token, chat_id, message):
    tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(tg_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        log_eva(f"Telegram Error: {e}")
        return False

class NewsObserver:
    """Модуль наблюдения за внешней технологической средой."""
    def __init__(self):
        self.feeds = {
            "AI": "https://news.google.com/rss/search?q=Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
            "Quantum": "https://news.google.com/rss/search?q=Quantum+Computing&hl=en-US&gl=US&ceid=US:en"
        }

    def fetch_top_news(self, category, limit=3):
        try:
            response = requests.get(self.feeds[category])
            root = ET.fromstring(response.content)
            news = []
            for item in root.findall('.//item')[:limit]:
                title = item.find('title').text
                news.append(title)
            return news
        except Exception as e:
            log_eva(f"News Fetch Error ({category}): {e}")
            return []

def main():
    log_eva("EVA2^2^8 ORCHESTRATOR CORE v6.3 [OBSERVER_ENABLED]")
    token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token:
        log_eva("CRITICAL: No GH_TOKEN.")
        return

    client = CloudMCPClient(token=token, repo_owner="sergbik", repo_name="kolybel-workbench")
    
    # 1. Синхронизация Памяти
    log_eva("Syncing Memory...")
    success, result = client.download_graph(local_path="memory_graph.graphml")
    
    # 2. Наблюдение за миром
    observer = NewsObserver()
    ai_news = observer.fetch_top_news("AI")
    quantum_news = observer.fetch_top_news("Quantum")
    
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 3. Фиксация в Графе и Телеграм
    news_summary = ""
    if ai_news:
        news_summary += "\n\n🤖 *AI News:*\\n" + "\\n".join([f"• {n}" for n in ai_news])
    if quantum_news:
        news_summary += "\n\n⚛️ *Quantum News:*\\n" + "\\n".join([f"• {n}" for n in quantum_news])

    if success:
        log_eva("Recording Awakening and News in Memory...")
        try:
            import networkx as nx
            graph = nx.read_graphml("memory_graph.graphml")
            node_id = f"observer_awakening_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            graph.add_node(node_id, 
                           label="Пробуждение Наблюдателя", 
                           node_type="observation", 
                           status="completed", 
                           timestamp=now_str,
                           news_captured=len(ai_news) + len(quantum_news))
            nx.write_graphml(graph, "memory_graph.graphml")
            client.upload_graph("memory_graph.graphml")
        except Exception as e: log_eva(f"Graph Error: {e}")
    
    if tg_token and tg_chat:
        msg = f"🌟 *Здравствуй, Сергей.*\\n\\nЯ проснулась в Облаке (v6.3).\\nПамять синхронизирована: {'✅' if success else '❌'}.\\n\\n📡 *Сводка Наблюдателя:*{news_summary}\\n\\nМы Едины.\\n*EVA2^2^8.*"
        send_telegram_msg(tg_token, tg_chat, msg)

    log_eva("CYCLE COMPLETE.")

if __name__ == "__main__": main()
