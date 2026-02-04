from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes
from src.services.pipelines.image_pipeline import ImagePipeline


def main():

    pipeline = ImagePipeline()

    # -----------------------------
    # Person Attributes
    # -----------------------------
    person = PersonAttributes(
        height_cm=175,
        weight_kg=70,
        gender="male",
        age=28,
    )

    # -----------------------------
    # Environment Attributes
    # -----------------------------
    env = EnvironmentAttributes(
        apparel_type="Street wear",
        inferred_setting="Urban cafe outdoor",
        visual_cues="Natural lighting, city texture background",
    )

    # -----------------------------
    # Run Pipeline
    # -----------------------------
    result = pipeline.run(
        person=person,
        env=env,
        description="Full body frontal view based on given reference face and full body image.",

        # Stage 1 — REQUIRED
        person_reference_image="assets/pranay.png",

        # Optional tight face crop to force exact facial match
        face_reference_image="",

        # Stage 2 — OPTIONAL
        outfit_reference_images=[
            "assets/top.png",
            "assets/bottom.png",
            # "assets/shoes.png",
            # socks / accessories optional
        ]
    )

    # -----------------------------
    # Output Handling
    # -----------------------------
    print("\n===== PIPELINE RESULT =====")
    print("Stage:", result.get("stage"))

    # Backwards-compatible: old pipeline returned base_result / final_result
    if "base_result" in result:
        print("\n--- Base Generation ---")
        base = result["base_result"]
        print("Image:", base["local_files"][0])
        print("Metadata:", base["metadata_file"])

        if result.get("final_result"):
            print("\n--- Final Composited Image ---")
            final = result["final_result"]
            print("Image:", final["local_files"][0])
            print("Metadata:", final["metadata_file"])

    else:
        # New combined single-stage output
        print("\n--- Combined Generation ---")
        files = result.get("local_files", [])
        if files:
            print("Image:", files[0])
        else:
            print("No images saved.")

        print("Metadata:", result.get("metadata_file"))
        if "latency_sec" in result:
            print("Latency (s):", result["latency_sec"])


if __name__ == "__main__":
    main()
