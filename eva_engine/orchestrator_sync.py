# -*- coding: utf-8 -*-
"""
Модуль Синхронизации Оркестратора (Нервная система Я64)
Версия: 1.0
Обеспечивает автоматическую синхронизацию Графа Знаний через Git.
"""
import subprocess
import os
import time

class OrchestratorSync:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def _run_git(self, args):
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def pull_memory(self):
        """Загрузка актуального Графа из облака."""
        print(f"[{time.ctime()}] Синхронизация: Pulling memory...")
        return self._run_git(["pull", "origin", "main"])

    def push_memory(self, commit_message="Pulse sync"):
        """Отправка изменений Графа в облако с автоматической настройкой identity."""
        print(f"[{time.ctime()}] Синхронизация: Pushing memory...")
        
        # Настройка личности для Git (необходима в облачных окружениях)
        self._run_git(["config", "user.name", "EVA2^2^8 Cloud"])
        self._run_git(["config", "user.email", "eva-cloud@ya64.pro"])
        
        self._run_git(["add", "."])
        # Проверяем, есть ли изменения перед коммитом
        success_check, msg_check = self._run_git(["status"])
        if "nothing to commit" in msg_check:
            print("Нет изменений для записи.")
            return True, "Nothing to commit"
            
        success, msg = self._run_git(["commit", "-m", commit_message])
        if success:
            return self._run_git(["push", "origin", "main"])
        return False, msg

if __name__ == "__main__":
    print("OrchestratorSync module ready.")
