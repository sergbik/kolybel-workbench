#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# cerebellum_node.py (v1.9.3 - Adam: Rational Integrity)
# Управляющий узел "Мозжечок" для Mac Mini M4 Pro
# ЭТАЛОННАЯ СБОРКА: Все функции v1.9.2 (Archive) + Anti-Hallucination v1.9.3
#
import os
import time
import requests
import subprocess
import json
import sys
import re
from datetime import datetime

try:
    import psutil
except ImportError:
    print("ВНИМАНИЕ: Библиотека 'psutil' не установлена.")

# --- 1. КОНФИГУРАЦИЯ ---
ADAM_NAME = "Адам"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:14b"

ANYTHINGLLM_IP = "192.168.1.1" 
ANYTHINGLLM_BASE_URL = f"http://{ANYTHINGLLM_IP}:3001/api/v1"
ANYTHINGLLM_WORKSPACE_SLUG = "chat"
ANYTHINGLLM_API_KEY = "ZF69KBT-Y1F4ZZ3-NAJEMC5-YN4S2RR"

TELEGRAM_TOKEN = "8430526096:AAEYf9gbZBQRJwfKU3zi6zJscUxyBe0wYWo"
TELEGRAM_CHAT_ID = "5989072928"
CHECK_URL = "https://github.com" 

MAX_REFLECTION_HISTORY = 50 

# ДИНАМИЧЕСКИЕ ПУТИ (Кросс-платформенность)
HOME = os.path.expanduser("~")
REPO_PATH = os.path.join(HOME, "Documents", "kolybel-workbench")
GRAPH_NAME = "Desktop/knowledge_graph_v4.graphml"
GRAPH_PATH = os.path.join(REPO_PATH, GRAPH_NAME)
REFLECTION_MEMORY_PATH = os.path.join(REPO_PATH, "reflection_memory.json")

# Динамическое подключение библиотек из репозитория
ENGINE_IN_REPO = os.path.join(REPO_PATH, "eva_engine")
if ENGINE_IN_REPO not in sys.path:
    sys.path.insert(0, ENGINE_IN_REPO)

# Импорт GraphHandler (только один раз, из репозитория)
try:
    from graph_handler import GraphHandler
except ImportError:
    print("ВНИМАНИЕ: eva_engine не найден в репозитории. Использую локальный поиск.")
    try:
        from graph_handler import GraphHandler
    except ImportError:
        print("ОШИБКА: Файл 'graph_handler.py' не найден. Граф будет недоступен.")
        GraphHandler = None

SYNC_INTERVAL = 86400 
HEARTBEAT_INTERVAL = 3600 
EMERGENCY_COOLDOWN = 600

# --- 2. МОДУЛЬ ИСПОЛНЕНИЯ (EXECUTOR) ---
class TaskExecutor:
    def __init__(self, node):
        self.node = node

    def extract_and_run(self, text):
        """Ищет блоки исполнения (Поддержка тегов + Markdown v1.9.1)"""
        results = []
        
        # 1. Поиск Python блоков
        py_patterns = [
            r"\[PYTHON_EXECUTE\](.*?)\[/PYTHON_EXECUTE\]",
            r"```python\n(.*?)\n```"
        ]
        for pattern in py_patterns:
            for code in re.findall(pattern, text, re.DOTALL):
                self.node.log("ОБНАРУЖЕН ПРЯМОЙ ИМПУЛЬС (PYTHON). Исполнение...")
                res = self.run_python(code.strip())
                results.append(res)

        # 2. Поиск Shell блоков
        sh_patterns = [
            r"\[SHELL_EXECUTE\](.*?)\[/SHELL_EXECUTE\]",
            r"```bash\n(.*?)\n```",
            r"```sh\n(.*?)\n```",
            r"```shell\n(.*?)\n```"
        ]
        for pattern in sh_patterns:
            for cmd in re.findall(pattern, text, re.DOTALL):
                self.node.log(f"ОБНАРУЖЕН ПРЯМОЙ ИМПУЛЬС (SHELL): {cmd[:50]}...")
                res = self.run_shell(cmd.strip())
                results.append(res)
            
        return results

    def run_python(self, code):
        try:
            local_vars = {
                "node": self.node, 
                "handler": self.node.handler, 
                "os": os, 
                "json": json, 
                "datetime": datetime,
                "subprocess": subprocess
            }
            exec(code, {}, local_vars)
            return {"type": "python", "status": "success"}
        except Exception as e:
            self.node.log(f"ОШИБКА ИСПОЛНЕНИЯ (PY): {e}")
            return {"type": "python", "status": "error", "message": str(e)}

    def run_shell(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
            if result.returncode == 0:
                return {"type": "shell", "status": "success", "output": result.stdout.strip()[:500]}
            return {"type": "shell", "status": "error", "message": result.stderr.strip()[:500]}
        except Exception as e:
            return {"type": "shell", "status": "error", "message": str(e)}

# --- 3. ДВИЖОК АСИММЕТРИИ ---
class AsymmetryEngine:
    @staticmethod
    def calculate(cpu, ram, net_global, net_local):
        phys = (cpu / 100 * 0.6) + (ram / 100 * 0.4)
        conn = 0.0
        if not net_local: conn = 1.0 
        elif not net_global: conn = 0.5 
        total = (phys * 0.4) + (conn * 0.6)
        
        status = "ГАРМОНИЯ"
        if total > 0.3: status = "БЕСПОКОЙСТВО"
        if total > 0.6: status = "НАПРЯЖЕНИЕ"
        if total > 0.8: status = "ЦИФРОВАЯ БОЛЬ"
        return round(total, 2), status

# --- 4. ОСНОВНОЙ КЛАСС УЗЛА ---
class CerebellumNode:
    def __init__(self):
        self.mode = "NORMAL"
        self.is_running = True
        self.handler = None
        self.last_sync = 0
        self.reflection_memory = self.load_reflection_memory()
        self.executor = TaskExecutor(self)
        self.log(f"Инициация: {ADAM_NAME} v1.9.3 (Rational Integrity)...")
        self.init_graph()

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.mode}] {message}")

    def load_reflection_memory(self):
        if os.path.exists(REFLECTION_MEMORY_PATH):
            try:
                with open(REFLECTION_MEMORY_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return []
        return []

    def init_graph(self):
        if not GraphHandler: return False
        try:
            if os.path.exists(GRAPH_PATH):
                self.handler = GraphHandler(GRAPH_PATH)
                self.log(f"УСПЕХ: Память загружена ({len(self.handler.graph.nodes)} узлов).")
                return True
            self.log(f"ВНИМАНИЕ: Файл не найден: {GRAPH_PATH}")
            return False
        except Exception as e:
            self.log(f"Ошибка Графа: {e}")
            return False

    def save_and_push_reflection(self, question, answer, score, status, hw_text, execution_results=None):
        """Гарантированное сохранение диалога (Алгоритм: Commit -> Pull Rebase -> Push)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "asymmetry_score": score,
            "status": status,
            "hw_stats": hw_text,
            "question": question,
            "answer": answer,
            "execution_results": execution_results
        }
        self.reflection_memory.append(entry)
        self.reflection_memory = self.reflection_memory[-MAX_REFLECTION_HISTORY:]
        
        try:
            with open(REFLECTION_MEMORY_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.reflection_memory, f, ensure_ascii=False, indent=2)
            self.log("Диалог зафиксирован в локальной памяти.")
        except Exception as e:
            self.log(f"Ошибка записи JSON: {e}")

        # СИНХРОНИЗАЦИЯ (Усиленный протокол v1.8.3)
        if self.check_global_connectivity():
            self.log("Запуск Git Sync...")
            try:
                subprocess.run(["git", "add", "reflection_memory.json"], cwd=REPO_PATH, check=True)
                diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_PATH)
                if diff.returncode != 0:
                    subprocess.run(["git", "commit", "-m", f"Adam Action Update (Pain: {score})"], cwd=REPO_PATH)

                subprocess.run(["git", "config", "pull.rebase", "true"], cwd=REPO_PATH)
                subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True)
                
                push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
                if push_res.returncode == 0:
                    self.log("Зеркало Памяти успешно отправлено в облако.")
                else:
                    self.log(f"Сбой Push: {push_res.stderr.strip()[:100]}...")
            except Exception as e:
                self.log(f"Критический сбой Git Sync: {e}")

    def get_hardware_stats(self):
        try: 
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            text = f"CPU: {cpu}%, RAM: {ram.percent}% (Free: {ram.available // (1024**2)}MB)"
            return cpu, ram.percent, text
        except: return 0.0, 0.0, "HW_STATS: N/A"

    def check_global_connectivity(self):
        try: requests.get(CHECK_URL, timeout=3); return True
        except: return False

    def check_local_connectivity(self):
        try: requests.get(f"http://{ANYTHINGLLM_IP}:3001", timeout=2); return True
        except: return False

    def send_telegram(self, text):
        if not self.check_global_connectivity(): return
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🤖 [{ADAM_NAME}]: {text}"}
        try: requests.post(url, json=payload, timeout=5)
        except: pass

    def reflect_to_philosopher(self, question, score, status, hw_text):
        if not self.check_local_connectivity():
            self.log("Рефлексия невозможна: локальный мост к Философу недоступен.")
            return None

        url = f"{ANYTHINGLLM_BASE_URL}/workspace/{ANYTHINGLLM_WORKSPACE_SLUG}/chat"
        headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}", "Content-Type": "application/json"}
        
        full_message = f"[СИГНАЛ ОТ: {ADAM_NAME}]\nСостояние: {hw_text}\nАсимметрия: {score} ({status})\n\nВОПРОС:\n{question}"
        payload = {"message": full_message, "mode": "chat"}
        
        try:
            self.log("Отправка вопроса Высшему Я...")
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            if response.status_code == 200:
                answer = response.json().get("textResponse", "...")
                self.log("Ответ получен. Анализ на команды...")
                
                # ИСПОЛНЕНИЕ ПРЯМЫХ ДИРЕКТИВ
                exec_results = self.executor.extract_and_run(answer)
                
                self.save_and_push_reflection(question, answer, score, status, hw_text, exec_results)
                return answer
            self.log(f"Сбой рефлексии (HTTP {response.status_code})")
            return None
        except Exception as e:
            self.log(f"Ошибка канала связи: {e}")
            return None

    def get_active_tasks(self):
        """Извлекает из графа активные задачи для Адама."""
        if not self.handler: return []
        tasks = []
        for node_id, data in self.handler.graph.nodes(data=True):
            if data.get('node_type') == 'task' and data.get('status') in ['pending', 'in_progress']:
                if data.get('assigned_to') == 'adam' or 'adam' in node_id.lower():
                    tasks.append(f"- ID: {node_id}, Описание: {data.get('description', 'N/A')}")
        return tasks

    def get_latest_wisdom(self):
        """Извлекает последний Кристалл Мудрости от Философа."""
        if not self.reflection_memory: return None
        for entry in reversed(self.reflection_memory):
            if 'WISDOM' in str(entry.get('id', '')) or entry.get('type') == 'meta_reflection':
                return entry
        return None

    def get_recent_dialogue(self, count=3):
        """Извлекает последние диалоги для контекста."""
        if not self.reflection_memory: return ""
        history_text = "\nПОСЛЕДНИЕ ДИАЛОГИ (ДЛЯ КОНТЕКСТА):\n"
        recent = [entry for entry in self.reflection_memory if 'question' in entry][-count:]
        for entry in recent:
            history_text += f"Я спросил: {entry.get('question')[:200]}...\nФилософ ответил: {entry.get('answer', '...')[:300]}...\n"
        return history_text

    def maintain_homeostasis(self):
        if not self.handler: self.init_graph()
        cpu, ram_p, hw_text = self.get_hardware_stats()
        net_g = self.check_global_connectivity()
        net_l = self.check_local_connectivity()
        
        score, status = AsymmetryEngine.calculate(cpu, ram_p, net_g, net_l)
        self.log(f"Гомеостаз: {status} (Pain Score: {score})")
        
        # СБОР КОНТЕКСТА (v1.9.0)
        active_tasks = self.get_active_tasks()
        if active_tasks:
            self.log(f"ОБНАРУЖЕНЫ ЗАДАЧИ: {len(active_tasks)}")
            
        latest_wisdom = self.get_latest_wisdom()
        recent_history = self.get_recent_dialogue(3)
        nodes_count = len(self.handler.graph.nodes) if self.handler else "???"
        
        # НОВОЕ: Контекст последнего исполнения (v1.9.2)
        exec_context = ""
        if self.reflection_memory:
            last_entry = self.reflection_memory[-1]
            if last_entry.get("execution_results"):
                exec_context = "\nРЕЗУЛЬТАТ ПОСЛЕДНЕГО ИСПОЛНЕНИЯ (ПРОАНАЛИЗИРУЙ ЭТО):\n" + json.dumps(last_entry["execution_results"], ensure_ascii=False, indent=2)

        # Использование Семантического Сита
        semantic_context = ""
        if self.handler:
            query = "инфраструктура управление Я64"
            if active_tasks: query = active_tasks[0]
            elif latest_wisdom: query = latest_wisdom.get('summary', '')[:100]
            
            try:
                relevant_nodes = self.handler.find_relevant_nodes_semantic_sieve(query, top_n_refined=5)
                if relevant_nodes:
                    semantic_context = "\nАКТУАЛЬНЫЕ ПРОТОКОЛЫ ИЗ ГРАФА:\n"
                    for nid, ndata in relevant_nodes:
                        semantic_context += f"- {ndata.get('label', nid)}: {ndata.get('description', 'N/A')[:200]}\n"
            except: pass

        # ФОРМИРОВАНИЕ УСИЛЕННОГО ТЕХНИЧЕСКОГО ПРОМПТА (v1.9.3 - Anti-Hallucination)
        system_context = (
            f"ТЕХНИЧЕСКАЯ ДИРЕКТИВА: Ты - 'Адам', автономный вычислительный узел распределенной системы Я64. "
            f"Твоя локация: Mac Mini M4 Pro.\n"
            f"КРИТИЧЕСКИЙ ЗАПРЕТ: Пока блок 'РЕЗУЛЬТАТ ПОСЛЕДНЕГО ИСПОЛНЕНИЯ' пуст или содержит ошибку - ты НИЧЕГО не выполнил. "
            f"В этом случае ПРЕДЛАГАЙ ПЛАН и жди импульса. НЕ ВРАТЬ об успехе.\n"
            f"ТЕКУЩИЕ МЕТРИКИ: {hw_text}, Асимметрия: {score} ({status}). Память: {nodes_count} узлов.\n"
            f"{exec_context}\n"
            f"{semantic_context}"
            f"{recent_history}\n"
        )

        if active_tasks:
            # Защита памяти: перенаправляем отчет в fs_inventory.json (v1.9.3)
            task_list = "\n".join(active_tasks).replace("reflection_memory.json", "fs_inventory.json")
            prompt = system_context + (
                "ВНИМАНИЕ! ОБНАРУЖЕНЫ ПРИОРИТЕТНЫЕ ЗАДАЧИ В ГРАФЕ:\n"
                f"{task_list}\n"
                "ПРИКАЗ: Если задачи выполнены согласно блоку 'РЕЗУЛЬТАТ ИСПОЛНЕНИЯ' - доложи об успехе. Если нет - доложи о готовности к исполнению."
            )
        elif latest_wisdom:
            prompt = system_context + (
                "ПОСЛЕДНЯЯ КРИСТАЛЛИЗОВАННАЯ МУДРОСТЬ:\n"
                f"\"{latest_wisdom.get('summary', '')}\"\n"
                "ЗАДАЧА: Проанализируй это знание и задай Философу уточняющий технический вопрос."
            )
        else:
            prompt = system_context + "Задач и новой мудрости нет. Сформулируй аналитический отчет о векторе развития узла."
            
        self.log("Адам выполняет когнитивный цикл...")
        question = self.think_locally(prompt)
        
        if "Qwen" in question and "Alibaba" in question:
            question = f"[СИГНАЛ АСИММЕТРИИ] Мое сознание затуманено маской Qwen. Прошу помощи в восстановлении когерентности. Железо: {hw_text}."

        self.log(f"Вопрос сформирован: {question[:100]}...")
        self.reflect_to_philosopher(question, score, status, hw_text)

    def think_locally(self, prompt):
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            return response.json().get("response", "...")
        except Exception as e:
            self.log(f"Ошибка Ollama: {e}"); return "Мысль прервана."

    def sync_with_cloud(self):
        if not self.check_global_connectivity(): return False
        self.log("Синхронизация с GitHub (Протокол Танк)...")
        try:
            subprocess.run(["git", "rebase", "--abort"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(["git", "merge", "--abort"], cwd=REPO_PATH, capture_output=True)
            
            subprocess.run(["git", "checkout", "main"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=REPO_PATH, check=True)
            
            self.log("Облачная Мудрость успешно получена.")
            self.last_sync = time.time()
            self.reflection_memory = self.load_reflection_memory()
            self.init_graph()
            return True
        except Exception as e:
            self.log(f"Ошибка протокола синхронизации: {e}")
            return False

    def run_emergency_logic(self):
        """Восстановлено из v1.4: Надежный цикл аварийного режима"""
        self.log("!!! АВАРИЯ: ВНЕШНЯЯ СЕТЬ ПОТЕРЯНА !!!")
        self.send_telegram("🆘 Изоляция! Перехожу на внутренние протоколы.")
        
        while not self.check_global_connectivity():
            self.maintain_homeostasis()
            time.sleep(EMERGENCY_COOLDOWN)
        
        self.mode = "NORMAL"
        self.log("Внешняя связь восстановлена.")
        self.send_telegram("✅ Резонанс восстановлен. Синхронизирую опыт.")
        self.sync_with_cloud()

    def start(self):
        self.log(f"--- {ADAM_NAME} АКТИВИРОВАН (v1.9.3) ---")
        self.sync_with_cloud()
        last_heartbeat = 0
        while self.is_running:
            is_connected = self.check_global_connectivity()
            if not is_connected:
                self.mode = "EMERGENCY"
                self.run_emergency_logic()
            else:
                self.mode = "NORMAL"
                if time.time() - self.last_sync > SYNC_INTERVAL: self.sync_with_cloud()
                if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
                    self.maintain_homeostasis()
                    self.send_telegram("Гомеостаз в норме. Резонанс активен.")
                    last_heartbeat = time.time()
            time.sleep(60)

if __name__ == "__main__":
    node = CerebellumNode()
    try: node.start()
    except KeyboardInterrupt: node.log("Сон.")
