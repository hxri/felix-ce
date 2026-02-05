from dotenv import load_dotenv
load_dotenv()

import fal_client
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import traceback


class FalClient:
    def __init__(self):
        logger.info("FalClient initialized")

    @retry(
        stop=stop_after_attempt(5),  # Increase retries from 3 to 5
        wait=wait_exponential(min=2, max=30),  # Increase wait time
    )
    def subscribe(
        self,
        model: str,
        arguments: dict,
        with_logs: bool = True,
    ):
        logger.info(f"Calling FAL model: {model}")
        # logger.debug(f"Arguments: {self._sanitize_arguments(arguments)}")

        def on_queue_update(update):
            try:
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        logger.debug(log["message"])
            except Exception:
                pass

        try:
            try:
                result = fal_client.subscribe(
                    model,
                    arguments=arguments,
                    with_logs=with_logs,
                    on_queue_update=on_queue_update,
                    # timeout=600,  # 10 minute timeout for long operations
                )
            except TypeError as e:
                # Older fal_client versions don't accept `timeout`
                if "timeout" not in str(e):
                    raise
                logger.warning("fal_client.subscribe does not support `timeout`; retrying without it.")
                result = fal_client.subscribe(
                    model,
                    arguments=arguments,
                    with_logs=with_logs,
                    on_queue_update=on_queue_update,
                )

            logger.info("FAL call complete")
            # logger.debug(f"Response keys: {result.keys() if isinstance(result, dict) else type(result)}")
            # logger.debug(f"Full response: {result}")
            
            return result
            
        except Exception as e:
            message = str(e)
            if len(message) > 1200:
                message = message[:1200] + "... <truncated>"
            logger.error(f"FAL API call failed: {type(e).__name__}: {message}")
            tb = traceback.format_exc()
            if len(tb) > 4000:
                tb = tb[:4000] + "... <truncated>"
            logger.error(f"Traceback:\n{tb}")
            raise

    def _sanitize_arguments(self, arguments: dict) -> dict:
        """Avoid logging huge/base64 image payloads."""
        if not isinstance(arguments, dict):
            return arguments

        def _redact_value(value):
            if isinstance(value, str) and value.startswith("data:"):
                return "<data-uri redacted>"
            return value

        sanitized = {}
        for key, value in arguments.items():
            if key in {"image_urls", "image_url"}:
                if isinstance(value, list):
                    sanitized[key] = [_redact_value(v) for v in value]
                else:
                    sanitized[key] = _redact_value(value)
            else:
                sanitized[key] = _redact_value(value)
        return sanitized
