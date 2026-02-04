from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes
from src.services.pipelines.image_pipeline import ImagePipeline
from src.services.pipelines.video_pipeline import VideoPipeline


def main():

    # ============================================================
    # IMAGE GENERATION
    # ============================================================
    image_pipeline = ImagePipeline()

    person = PersonAttributes(
        height_cm=175,
        weight_kg=70,
        gender="male",
        age=28,
    )

    env = EnvironmentAttributes(
        apparel_type="Street wear",
        inferred_setting="Urban cafe outdoor",
        visual_cues="Natural lighting, city texture background",
    )

    print("\n===== IMAGE GENERATION STAGE =====")
    image_result = image_pipeline.run(
        person=person,
        env=env,
        description="Full body frontal view based on given reference face and full body image.",
        person_reference_image="assets/pranay.png",
        face_reference_image="",
        outfit_reference_images=[
            "assets/top.png",
            "assets/bottom.png",
        ]
    )

    print("Image Stage:", image_result.get("stage"))
    image_files = image_result.get("local_files", [])
    if not image_files:
        print("ERROR: No images generated. Exiting.", file=__import__("sys").stderr)
        return

    generated_image = image_files[0]
    print(f"Generated Image: {generated_image}")
    print(f"Image Latency: {image_result.get('latency_sec'):.2f}s")
    print(f"Image Metadata: {image_result.get('metadata_file')}")

    # ============================================================
    # VIDEO GENERATION
    # ============================================================
    video_pipeline = VideoPipeline(video_model="hunyuan")

    print("\n===== VIDEO GENERATION STAGE =====")
    video_result = video_pipeline.run(
        reference_image=generated_image,
        apparel_description="blue t-shirt and khaki shorts",
        duration_sec=5,
    )

    print("Video Stage:", video_result.get("stage"))
    print("Video Model:", video_result.get("video_model"))
    video_files = video_result.get("local_files", [])
    if video_files:
        print(f"Generated Video: {video_files[0]}")
    else:
        print("No videos generated.")

    print(f"Video Latency: {video_result.get('latency_sec'):.2f}s")
    print(f"Video Metadata: {video_result.get('metadata_file')}")

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n===== PIPELINE SUMMARY =====")
    print(f"Total Image + Video Time: {image_result.get('latency_sec', 0) + video_result.get('latency_sec', 0):.2f}s")
    print(f"Image metadata: {image_result.get('metadata_file')}")
    print(f"Video metadata: {video_result.get('metadata_file')}")


if __name__ == "__main__":
    main()