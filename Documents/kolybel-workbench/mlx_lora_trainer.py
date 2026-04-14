import os
import subprocess
import sys
import shutil

# ==========================================================
# КОНФИГУРАЦИЯ ОБУЧЕНИЯ (Настраивай здесь)
# ==========================================================
MODEL_NAME = "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"
ITERS = 500           # 500 - база, 2000+ - для сложных навыков
LORA_LAYERS = 16      # 8 - эконом, 16 - стандарт, 32 - максимум (RAM!)
LEARNING_RATE = 1e-5  # Скорость обучения (рекомендуется 1e-5)
BATCH_SIZE = 1        # Всегда 1 для 24GB RAM
# ==========================================================

BASE_PATH = os.path.expanduser("~/Documents/kolybel-workbench/")
DATASET_NAME = "adam_golden_dataset_v1.jsonl"
ADAPTER_PATH = "adam_lora_adapter"

def run_training():
    print(f"=== ЗАПУСК ЛОКАЛЬНОГО СИНТЕЗА АДАМА (ITERS: {ITERS}, LAYERS: {LORA_LAYERS}) ===")
    
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    source_dataset = os.path.join(BASE_PATH, DATASET_NAME)
    train_file = os.path.join(BASE_PATH, "train.jsonl")
    valid_file = os.path.join(BASE_PATH, "valid.jsonl")

    if not os.path.exists(source_dataset):
        print(f"ОШИБКА: Исходный датасет не найден: {source_dataset}")
        return

    print("[*] Синхронизация файлов данных...")
    shutil.copy(source_dataset, train_file)
    shutil.copy(source_dataset, valid_file)

    command = [
        "python3", "-m", "mlx_lm.lora",
        "--model", MODEL_NAME,
        "--train",
        "--data", BASE_PATH,
        "--iters", str(ITERS),
        "--batch-size", str(BATCH_SIZE),
        "--grad-accumulation-steps", "4",
        "--num-layers", str(LORA_LAYERS),
        "--learning-rate", str(LEARNING_RATE),
        "--grad-checkpoint",
        "--adapter-path", ADAPTER_PATH
    ]

    print(f"[*] Выполнение: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
        process.communicate()
        
        if process.returncode == 0:
            print(f"\n=== УСПЕХ ===\nАдаптер сохранен: {ADAPTER_PATH}")
        else:
            print(f"\n[!] Ошибка обучения. Код: {process.returncode}")
            
    except Exception as e:
        print(f"Критический сбой: {e}")

if __name__ == "__main__":
    run_training()
