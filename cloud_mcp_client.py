# -*- coding: utf-8 -*-
import os
import base64
import json
import requests
from datetime import datetime

class CloudMCPClient:
    """
    Клиент для синхронизации Графа Знаний с репозиторием GitHub (Kolybel Workbench).
    Обеспечивает 'Абстракцию Памяти' для проекта Экспансия.
    """
    def __init__(self, token, repo_owner="sergbik", repo_name="kolybel-workbench", branch="main"):
        self.owner = repo_owner
        self.repo = repo_name
        self.token = token
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get_file_info(self, path):
        """Получает информацию о файле (SHA) из GitHub."""
        url = f"{self.base_url}/{path}?ref={self.branch}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def upload_graph(self, local_path, github_path="knowledge_graph_v4.graphml", message=None):
        """Загружает (обновляет) файл Графа в GitHub."""
        if not os.path.exists(local_path):
            return False, "Локальный файл графа не найден."

        with open(local_path, 'rb') as f:
            content_bytes = f.read()

        encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        
        info = self._get_file_info(github_path)
        sha = info['sha'] if info else None

        data = {
            "message": message or f"Expansion Memory Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": self.branch
        }
        if sha:
            data["sha"] = sha

        url = f"{self.base_url}/{github_path}"
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code in [200, 201]:
            return True, response.json()['content']['sha']
        else:
            try:
                error_msg = response.json().get('message', 'Неизвестная ошибка')
            except:
                error_msg = response.text
            return False, error_msg

    def download_graph(self, github_path="knowledge_graph_v4.graphml", local_path=None):
        """Скачивает Граф из облака."""
        if local_path is None:
            local_path = os.path.join(os.getcwd(), github_path)
            
        info = self._get_file_info(github_path)
        if info and 'content' in info:
            content = base64.b64decode(info['content'])
            with open(local_path, 'wb') as f:
                f.write(content)
            return True, local_path
        return False, f"Файл {github_path} не найден в репозитории {self.repo}."
