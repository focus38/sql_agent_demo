import asyncio
import logging
from functools import wraps
from inspect import signature
from typing import Optional, Callable


def s_retry(*, max_retries: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    multiplier: float = 1.0,
    logger: Optional[logging.Logger] = None
):
    """
    Декоратор для повторных попыток асинхронных функций с передачей attempt_number.
    """

    def decorator(func: Callable) -> Callable:
        sig = signature(func)
        if 'attempt_number' not in sig.parameters:
            raise ValueError(f"Функция {func.__name__} должна принимать аргумент 'attempt_number' как keyword-only.")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_retries + 1):
                # Передаём attempt_number внутрь
                kwargs_with_attempt = {**kwargs, 'attempt_number': attempt}

                try:
                    return await func(*args, **kwargs_with_attempt)
                except Exception as e:
                    last_exception = e
                    if logger:
                        logger.warning(f"[{func.__name__}] Попытка {attempt}/{max_retries} не удалась: {e}")

                    if attempt >= max_retries:
                        break

                    # Экспоненциальная задержка
                    wait_time = min(multiplier * (2 ** (attempt - 1)), max_wait)
                    wait_time = max(wait_time, min_wait)
                    await asyncio.sleep(wait_time)

            if logger:
                logger.error(f"[{func.__name__}] Все {max_retries} попыток завершились ошибкой.")
            raise last_exception

        return wrapper

    return decorator