from dotenv import load_dotenv
load_dotenv()

import fal_client
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class FalClient:
    def __init__(self):
        logger.info("FalClient initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
    )
    def subscribe(
        self,
        model: str,
        arguments: dict,
        with_logs: bool = True,
    ):
        logger.info(f"Calling FAL model: {model}")

        def on_queue_update(update):
            try:
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        logger.debug(log["message"])
            except Exception:
                pass

        result = fal_client.subscribe(
            model,
            arguments=arguments,
            with_logs=with_logs,
            on_queue_update=on_queue_update,
        )

        logger.info("FAL call complete")
        return result
