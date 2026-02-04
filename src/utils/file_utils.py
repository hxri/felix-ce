import httpx
from pathlib import Path


def download_file(url: str, save_path: Path, timeout: float = 120.0):

    save_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.stream("GET", url, timeout=timeout) as r:
        r.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)

    return save_path
