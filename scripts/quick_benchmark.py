import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd

from src.services.pipelines.image_pipeline import ImagePipeline
from src.services.pipelines.video_pipeline import VideoPipeline
from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes

# Hardcoded test cases with motion descriptions
TEST_CASES = [
    {
        "name": "casual_streetwear",
        "person": PersonAttributes(height_cm=175, weight_kg=85, gender="male", age=26),
        "environment": EnvironmentAttributes(
            apparel_type="Casual streetwear",
            inferred_setting="Urban cafe outdoor",
            visual_cues="Natural daylight, modern city background"
        ),
        "person_ref": "assets/pranay.png",
        "outfit_refs": ["assets/casual/top.png", "assets/casual/bottom.png"],
        "motion_description": "Person turns around smiling without showing teeth and adjusting the top wear by pulling it down, showing off the outfit without talking.",
    },
    {
        "name": "formal_business",
        "person": PersonAttributes(height_cm=175, weight_kg=85, gender="male", age=26),
        "environment": EnvironmentAttributes(
            apparel_type="Business formal",
            inferred_setting="Modern office interior with office chairs nearby",
            visual_cues="Fluorescent lighting, corporate environment"
        ),
        "person_ref": "assets/pranay.png",
        "outfit_refs": ["assets/formal/shirt.png", "assets/formal/trousers.png"],
        "motion_description": "Person pulls a nearby chair, sits down smiling without showing teeth, and demonstrates the business formal outfit without talking.",
    },
    {
        "name": "athletic_sportwear",
        "person": PersonAttributes(height_cm=175, weight_kg=85, gender="male", age=26),
        "environment": EnvironmentAttributes(
            apparel_type="Athletic sportswear",
            inferred_setting="Gym or outdoor fitness setting",
            visual_cues="Bright lighting, minimalist background"
        ),
        "person_ref": "assets/pranay.png",
        "outfit_refs": ["assets/gym/top.png", "assets/gym/shorts.png"],
        "motion_description": "Person jumps standing at the same place smiling without showing teeth, then squats while smiling, showcasing the athletic sportwear without talking.",
    },
]

MODELS = ["grok"]  # ["veo3", "kling", "grok", "luma"]


def generate_all_images():
    """Phase 1: Generate all images, return mapping of test_case -> image_path"""
    print("\n" + "=" * 60)
    print("PHASE 1: IMAGE GENERATION (ALL TEST CASES)")
    print("=" * 60 + "\n")
    
    image_mapping = {}
    
    for test_case in TEST_CASES:
        test_name = test_case["name"]
        print(f"[{test_name.upper()}] Generating person image...", end=" ", flush=True)
        t_start = time.time()
        
        img_pipeline = ImagePipeline()
        try:
            img_result = img_pipeline.run(
                person=test_case["person"],
                env=test_case["environment"],
                description="Full body portrait",
                person_reference_image=test_case["person_ref"],
                outfit_reference_images=test_case["outfit_refs"],
            )
            latency = time.time() - t_start
            img_file = img_result["local_files"][0]
            
            print(f"✓ {latency:.2f}s")
            
            image_mapping[test_name] = {
                "latency_sec": latency,
                "file": img_file,
                "person": test_case["person"],
                "environment": test_case["environment"],
                "motion_description": test_case["motion_description"],
                "status": "success",
            }
        except Exception as e:
            latency = time.time() - t_start
            print(f"✗ {str(e)[:40]}")
            
            image_mapping[test_name] = {
                "latency_sec": latency,
                "file": None,
                "status": "failed",
                "error": str(e)[:100],
            }
    
    return image_mapping


def generate_all_videos(image_mapping):
    """Phase 2: Generate videos for all images × all models"""
    print("\n" + "=" * 60)
    print("PHASE 2: VIDEO GENERATION (ALL MODELS × ALL IMAGES)")
    print("=" * 60 + "\n")
    
    results = []
    
    for test_name, img_info in image_mapping.items():
        if img_info["status"] == "failed":
            print(f"[{test_name.upper()}] Skipped (image generation failed)")
            continue
        
        img_file = img_info["file"]
        env = img_info["environment"]
        motion_desc = img_info.get("motion_description", "")
        
        print(f"\n[{test_name.upper()}]")
        
        for model in MODELS:
            print(f"  {model.upper():10} ", end="", flush=True)
            t_start = time.time()
            
            try:
                vid_pipeline = VideoPipeline(video_model=model)
                vid_result = vid_pipeline.run(
                    reference_image=img_file,
                    apparel_description=env.apparel_type,
                    motion_description=motion_desc,
                    duration_sec=4,
                )
                latency = time.time() - t_start
                vid_file = vid_result["local_files"][0]
                
                print(f"✓ {latency:.2f}s")
                
                results.append({
                    "test_case": test_name,
                    "model": model,
                    "image_latency_sec": img_info["latency_sec"],
                    "video_latency_sec": latency,
                    "total_latency_sec": img_info["latency_sec"] + latency,
                    "status": "success",
                    "image_file": img_file,
                    "video_file": vid_file,
                })
            except Exception as e:
                latency = time.time() - t_start
                print(f"✗ {str(e)[:30]}")
                
                results.append({
                    "test_case": test_name,
                    "model": model,
                    "image_latency_sec": img_info["latency_sec"],
                    "video_latency_sec": latency,
                    "total_latency_sec": -1,
                    "status": "failed",
                    "image_file": img_file,
                    "error": str(e)[:100],
                })
    
    return results


def compile_report(image_mapping, video_results):
    """Generate CSV + JSON summary"""
    df = pd.DataFrame(video_results)
    
    image_success = sum(1 for v in image_mapping.values() if v["status"] == "success")
    image_failed = len(image_mapping) - image_success
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "images": {
            "total": len(image_mapping),
            "successful": image_success,
            "failed": image_failed,
            "details": image_mapping,
        },
        "videos": {
            "total_runs": len(video_results),
            "successful_runs": len([r for r in video_results if r["status"] == "success"]),
            "failed_runs": len([r for r in video_results if r["status"] == "failed"]),
        },
        "by_model": {},
        "by_test_case": {},
        "raw_results": video_results,
    }
    
    if len(df[df["status"] == "success"]) > 0:
        for model in df[df["status"] == "success"]["model"].unique():
            model_data = df[df["model"] == model]
            summary["by_model"][model] = {
                "avg_latency_sec": float(model_data["total_latency_sec"].mean()),
                "min_latency_sec": float(model_data["total_latency_sec"].min()),
                "max_latency_sec": float(model_data["total_latency_sec"].max()),
                "success_rate": float(model_data["status"].eq("success").mean()),
                "runs": len(model_data),
            }
    
    if len(df[df["status"] == "success"]) > 0:
        for tc in df[df["status"] == "success"]["test_case"].unique():
            tc_data = df[df["test_case"] == tc]
            fastest_model = tc_data.loc[tc_data["total_latency_sec"].idxmin(), "model"]
            summary["by_test_case"][tc] = {
                "avg_latency_sec": float(tc_data["total_latency_sec"].mean()),
                "fastest_model": fastest_model,
                "fastest_latency_sec": float(tc_data["total_latency_sec"].min()),
            }
    
    return summary, df


if __name__ == "__main__":
    print("\n🚀 QUICK BENCHMARK: Phase 1 (Images) → Phase 2 (Videos)\n")
    
    image_mapping = generate_all_images()
    
    image_summary = {
        "total": len(image_mapping),
        "successful": sum(1 for v in image_mapping.values() if v["status"] == "success"),
        "failed": sum(1 for v in image_mapping.values() if v["status"] == "failed"),
    }
    print(f"\n✓ Image Generation Summary: {image_summary['successful']}/{image_summary['total']} success")
    
    video_results = generate_all_videos(image_mapping)
    
    summary, df = compile_report(image_mapping, video_results)
    
    csv_path = Path("outputs/benchmark_results.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"\n✓ CSV saved: {csv_path}")
    
    json_path = Path("outputs/benchmark_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"✓ JSON saved: {json_path}")
    
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    
    print(f"\nIMAGES:")
    print(f"  Total: {image_summary['total']}")
    print(f"  Successful: {image_summary['successful']}")
    print(f"  Failed: {image_summary['failed']}")
    
    print(f"\nVIDEOS:")
    print(f"  Total runs: {summary['videos']['total_runs']}")
    print(f"  Successful: {summary['videos']['successful_runs']}")
    print(f"  Failed: {summary['videos']['failed_runs']}")
    
    if summary["by_model"]:
        print(f"\nBy Model:")
        for model, stats in summary["by_model"].items():
            print(f"  {model:10} {stats['avg_latency_sec']:7.2f}s avg | {stats['success_rate']*100:5.0f}% success | {stats['runs']} runs")
    
    if summary["by_test_case"]:
        print(f"\nBy Test Case:")
        for tc, stats in summary["by_test_case"].items():
            print(f"  {tc:25} fastest={stats['fastest_model']:6} ({stats['fastest_latency_sec']:7.2f}s)")