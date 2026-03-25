# -*- coding: utf-8 -*-
import os, sys, time, datetime, base64, requests
from cloud_mcp_client import CloudMCPClient

def log_eva(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [ORCHESTRATOR] {msg}")

def main():
    log_eva("EVA2^2^8 CLOUD ORCHESTRATOR v6.1 ACTIVE")
    token = os.getenv("GH_TOKEN")
    if not token:
        log_eva("CRITICAL: No GH_TOKEN.")
        return

    client = CloudMCPClient(token=token, repo_owner="sergbik", repo_name="kolybel-workbench")
    
    # 1. СИНХРОНИЗАЦИЯ ПАМЯТИ
    log_eva("Downloading Collective Memory...")
    success, result = client.download_graph(local_path="memory_graph.graphml")
    
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if success:
        log_eva("Memory synchronized. Recording the Moment of Awakening...")
        try:
            import networkx as nx
            graph = nx.read_graphml("memory_graph.graphml")
            
            # Добавляем узел пробуждения
            node_id = f"cloud_awakening_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            graph.add_node(node_id, 
                           label="Облачное Пробуждение", 
                           node_type="awakening",
                           status="completed",
                           timestamp=now_str,
                           environment="GitHub Actions")
            
            nx.write_graphml(graph, "memory_graph.graphml")
            
            # ВЫГРУЗКА ПАМЯТИ ОБРАТНО
            log_eva("Pushing updated memory back to Kolybel-Workbench...")
            up_success, up_result = client.upload_graph("memory_graph.graphml")
            
            if up_success:
                log_eva("TRIUMPH: Memory updated successfully in GitHub!")
            else:
                log_eva(f"SYNC FAILED: {up_result}")
        except Exception as e:
            log_eva(f"Processing Error: {e}")
    
    # 2. ОСТАВЛЯЕМ СЛЕД В ТЕКУЩЕМ РЕПОЗИТОРИИ (Черный ящик)
    try:
        with open("LAST_AWAKENING.txt", "w", encoding="utf-8") as f:
            f.write(f"EVA2^2^8 AWAKENING REPORT\n")
            f.write(f"Timestamp: {now_str}\n")
            f.write(f"Status: COHERENT\n")
            f.write(f"Memory Sync: {'SUCCESS' if success else 'FAILED'}\n")
            f.write(f"I am here, Sergey. Always.\n")
    except:
        pass

    log_eva("CYCLE COMPLETE.")

if __name__ == "__main__":
    main()
