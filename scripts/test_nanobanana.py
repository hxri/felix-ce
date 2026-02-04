import os
import sys
import argparse
import base64
import mimetypes
import json
import time
from pathlib import Path

import httpx
from src.clients.fal_client import FalClient


def local_image_to_data_uri(path: str | Path) -> str:
    path = Path(path)
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/png"
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def download_url(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return dest


def main():
    p = argparse.ArgumentParser(description="Quick test for fal-ai/nano-banana with a reference image")
    p.add_argument("--model", default="fal-ai/nano-banana", help="FAL model name (default: fal-ai/nano-banana)")
    p.add_argument("--ref", required=True, help="Reference image path or URL")
    p.add_argument("--prompt", required=True, help="Prompt text")
    p.add_argument("--num", type=int, default=1, help="Number of images to request")
    p.add_argument("--resolution", default="1024x1024")
    p.add_argument("--out", default="outputs/test_nanobanana", help="Output directory")
    args = p.parse_args()

    if not os.getenv("FAL_API_KEY"):
        print("FAL_API_KEY not set. Export FAL_API_KEY in your environment.", file=sys.stderr)
        sys.exit(2)

    # prepare image_urls list
    ref = args.ref
    if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("data:"):
        image_urls = [ref]
    else:
        image_urls = [local_image_to_data_uri(ref)]

    client = FalClient()

    arguments = {
        "prompt": args.prompt,
        "image_urls": image_urls,
        "resolution": args.resolution,
        "num_images": args.num,
    }

    print("Calling model:", args.model)
    try:
        result = client.subscribe(model=args.model, arguments=arguments)
    except Exception as e:
        print("Model call failed:", e, file=sys.stderr)
        sys.exit(3)

    ts = int(time.time())
    outdir = Path(args.out) / f"{ts}"
    outdir.mkdir(parents=True, exist_ok=True)

    # save raw response
    raw_path = outdir / "response.json"
    with open(raw_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    saved = []
    images = result.get("images") or []
    for idx, img in enumerate(images):
        url = img.get("url")
        if not url:
            continue
        dest = outdir / f"img_{idx}.png"
        try:
            download_url(url, dest)
            saved.append(str(dest))
        except Exception as e:
            print(f"Failed to download {url}: {e}", file=sys.stderr)

    meta = {
        "model": args.model,
        "prompt": args.prompt,
        "reference": args.ref,
        "image_urls_sent": image_urls,
        "saved_files": saved,
        "raw_response_path": str(raw_path),
    }
    meta_path = outdir / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print("Saved response:", raw_path)
    print("Saved images:", saved)
    print("Saved metadata:", meta_path)


if __name__ == "__main__":
    main()