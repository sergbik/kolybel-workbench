import copy
import shutil
from datetime import datetime
# -*- coding: utf-8 -*-
import os
import json
import networkx as nx
from filelock import FileLock, Timeout

class GraphHandler:
    """
    Класс-обработчик для унифицированного взаимодействия с графом знаний.
    Версия: 2.3 - Синхронизированная версия (Safe API для LLM).
    """
    def __init__(self, graph_path):
        self.graph_path = graph_path
        self.versioning_dir = os.path.join(os.path.dirname(self.graph_path), 'graph_versions')
        os.makedirs(self.versioning_dir, exist_ok=True)
        self._transaction_backup = None
        self.lock_path = graph_path + ".lock"
        self.lock = FileLock(self.lock_path, timeout=15) 

        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Файл графа не найден по пути: {self.graph_path}")
        
        try:
            with self.lock:
                self.graph = nx.read_graphml(self.graph_path)
            if not isinstance(self.graph, nx.DiGraph):
                self.graph = self.graph.to_directed()
        except Timeout:
            raise IOError(f"Не удалось получить блокировку для чтения файла графа.")
        except Exception as e:
            raise IOError(f"Критическая ошибка при чтении файла графа: {e}")

    def _sanitize_value(self, value):
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return value

    def get_current_timestamp(self):
        return datetime.now().isoformat()

    def save_graph(self, *args, **kwargs):
        temp_path = self.graph_path + ".tmp"
        try:
            with self.lock:
                nx.write_graphml(self.graph, temp_path, encoding='utf-8')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                version_filename = f"knowledge_graph_v4_{timestamp}.graphml"
                version_path = os.path.join(self.versioning_dir, version_filename)
                shutil.copy(temp_path, version_path)
                shutil.move(temp_path, self.graph_path)
        except Exception as e:
            if os.path.exists(temp_path): os.remove(temp_path)
            raise

    def get_node(self, node_id):
        """Возвращает (data, error). data может быть None!"""
        node_id = node_id.lower()
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id], None
        return None, f"Узел '{node_id}' не найден."

    def get_node_data(self, node_id):
        """БЕЗОПАСНЫЙ МЕТОД: Всегда возвращает словарь (пустой, если узла нет)."""
        data, err = self.get_node(node_id)
        return data if data is not None else {}

    def get_nodes_by_attribute(self, attr_name, attr_value):
        """Находит узлы. Возвращает список кортежей (id, data)."""
        return [(node, data) for node, data in self.graph.nodes(data=True) if data.get(attr_name) == attr_value]

    def get_nodes_data_by_attribute(self, attr_name, attr_value):
        """БЕЗОПАСНЫЙ МЕТОД: Возвращает только список словарей данных."""
        return [data for node, data in self.get_nodes_by_attribute(attr_name, attr_value)]

    def get_tasks_by_status(self, status="pending"):
        all_tasks = self.get_nodes_by_attribute('node_type', 'task')
        return [(node, data) for node, data in all_tasks if data.get('status') == status]

    def find_related(self, node_id, top_n=5, node_type_filter=None):
        node_id = node_id.lower()
        if not self.graph.has_node(node_id): return []
        connections = []
        neighbors = set(list(self.graph.successors(node_id)) + list(self.graph.predecessors(node_id)))
        for neighbor in neighbors:
            if node_type_filter and self.graph.nodes[neighbor].get('node_type') != node_type_filter: continue
            edge_data = self.graph.get_edge_data(node_id, neighbor) or self.graph.get_edge_data(neighbor, node_id)
            if edge_data:
                weight = edge_data.get('weight', 0.0)
                connections.append((neighbor, weight, edge_data.get('relation_type', 'related_to')))
        return sorted(connections, key=lambda item: item[1], reverse=True)[:top_n]

    def add_node(self, node_id, **attrs):
        node_id = node_id.lower()
        timestamp = self.get_current_timestamp()
        sanitized_attrs = {k: self._sanitize_value(v) for k, v in attrs.items()}
        if not self.graph.has_node(node_id): sanitized_attrs['created_at'] = timestamp
        sanitized_attrs['updated_at'] = timestamp
        if self.graph.has_node(node_id): self.graph.nodes[node_id].update(sanitized_attrs)
        else: self.graph.add_node(node_id, **sanitized_attrs)

    def update_node_attribute(self, node_id, attr_name, attr_value):
        node_id = node_id.lower()
        if self.graph.has_node(node_id):
            self.graph.nodes[node_id][attr_name] = self._sanitize_value(attr_value)
            self.graph.nodes[node_id]['updated_at'] = self.get_current_timestamp()
            return True
        return False

    def add_edge(self, source_id, target_id, relation_type='related_to', weight=1.0, **attrs):
        source_id, target_id = source_id.lower(), target_id.lower()
        timestamp = self.get_current_timestamp()
        for nid in [source_id, target_id]:
            if not self.graph.has_node(nid): self.add_node(nid, node_type='concept')
            else: self.update_node_attribute(nid, 'updated_at', timestamp)
        sanitized_attrs = {k: self._sanitize_value(v) for k, v in attrs.items()}
        sanitized_attrs['relation_type'] = relation_type
        if self.graph.has_edge(source_id, target_id):
            current_weight = self.graph[source_id][target_id].get('weight', 0.0)
            if not isinstance(current_weight, (int, float)): current_weight = 0.0
            sanitized_attrs['weight'] = current_weight + weight
            self.graph[source_id][target_id].update(sanitized_attrs)
        else:
            sanitized_attrs['weight'] = weight
            self.graph.add_edge(source_id, target_id, **sanitized_attrs)

    def remove_node(self, node_id):
        node_id = node_id.lower()
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            return True
        return False
