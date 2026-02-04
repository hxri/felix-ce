import base64
from pathlib import Path
import mimetypes


def local_image_to_data_uri(path: str | Path) -> str:
    path = Path(path)

    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/png"

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"
