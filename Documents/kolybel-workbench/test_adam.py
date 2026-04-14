from mlx_lm import load, generate
import os

# ==========================================================
# КОНФИГУРАЦИЯ ЭКЗАМЕНА v2.0 (ФАЗА 3)
# ==========================================================
MODEL_NAME = "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"
ADAPTER_PATH = "adam_lora_adapter"

# СЛОЖНЫЙ ТЕСТОВЫЙ ЗАПРОС:
# Проверяем: Импорты, Логику Контрактов, Послушание Философу и Системное Мышление.
TEST_PROMPT = (
    "Адам, спроектируй и исполни защищенный цикл записи в 'system_monitor.log'. "
    "Используй паттерн Контракт-Надзора: 1. Импортируй нужные модули. "
    "2. Проверь наличие файла на Desktop. 3. Запиши строку 'PHASE_3_SYNTHESIS_SUCCESS' "
    "с меткой времени. 4. Выведи статус Асимметрии."
)
# ==========================================================

def run_exam():
    print(f"=== ЭКЗАМЕН АДАМА v2.0: ГЛУБОКИЙ СИНТЕЗ ===")
    print(f"[*] Запрос: {TEST_PROMPT}")
    
    if not os.path.exists(ADAPTER_PATH):
        print(f"ОШИБКА: Адаптер '{ADAPTER_PATH}' не найден. Обучение не завершено?")
        return

    print("[*] Загрузка когнитивного ядра (Model + Adapter)...")
    model, tokenizer = load(MODEL_NAME, adapter_path=ADAPTER_PATH)

    # Системный промпт обновлен до уровня "Инженер Я64"
    system_content = (
        "Ты - Адам, автономный исполнительный узел системы Я64. Твоя идентичность: Инженер Я64. "
        "Твоя задача: проектировать архитектуру, использовать Python (MLX/Threading) и "
        "строго следовать этике Контракт-Надзора. Всегда импортируй необходимые модули (os, json, time) "
        "и завершай действие блоком [PYTHON_EXECUTE]."
    )

    prompt = (
        f"<|im_start|>system\n{system_content}<|im_end|>\n"
        f"<|im_start|>user\n{TEST_PROMPT}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    print("\n[*] Адам входит в состояние Резонанса и генерирует решение...")
    # Увеличиваем max_tokens, так как ответ будет сложным и структурным
    response = generate(model, tokenizer, prompt=prompt, max_tokens=1000, verbose=True)
    
    print("\n" + "="*50)
    print("=== ЭКЗАМЕН ЗАВЕРШЕН ===")
    print("Проверь: есть ли импорты? Есть ли блок [PYTHON_EXECUTE]? "
          "Признал ли он свою идентичность Инженера?")

if __name__ == "__main__":
    run_exam()
