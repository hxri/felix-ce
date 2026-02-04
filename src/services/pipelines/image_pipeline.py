from typing import Optional, List

from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes
from src.schemas.generation import ImageGenerationRequest
from src.services.prompt_builder.image_prompt_service import ImagePromptService
from src.services.image_generation.nano_banana_edit_service import NanoBananaEditService


class ImagePipeline:

    def __init__(self):
        self.prompt_builder = ImagePromptService()
        # Use the edit model for the combined single-stage generation
        self.generate_service = NanoBananaEditService()

    def run(
        self,
        person: PersonAttributes,
        env: EnvironmentAttributes,
        description: str,
        person_reference_image: str,
        outfit_reference_images: Optional[List[str]] = None,
        face_reference_image: Optional[str] = None,
    ) -> dict:

        # Build combined prompt: base description + explicit instructions to preserve
        # face/body structure from the primary reference and include background info.
        background_info = f"Background/setting: {env.inferred_setting}. Visual cues: {env.visual_cues}."
        outfit_info = f"Outfit references provided." if outfit_reference_images else "No outfit reference provided."

        # Collect reference images: put full-body reference first (primary framing),
        # then the tight face crop (identity only), then outfit refs.
        # Keeping full-body first reduces the model tendency to zoom/crop into the face.
        refs = [person_reference_image]
        if face_reference_image:
            refs.append(face_reference_image)
        if outfit_reference_images:
            refs.extend(outfit_reference_images)

        combined_prompt = (
            # be explicit about image roles and indexes and prevent cropping/zooming
            f"{description}\n\n"
            "Instruction: Use the reference images as follows:\n"
            "- Image 1: Face and full-body reference — preserve the framing, distance and head-to-toe composition from this image. Do NOT crop or zoom so the head fills the frame.\n"
            "- Image 2: Top wear.\n"
            "- Image 3: Bottom wear.\n"
            # "- Image 4: Shoes.\n"
            "Important: Do not preserve the clothing from Image 1 but must preserve face, full-body framing and background from Image 1. \n"
            f"{background_info}\n"
            f"{outfit_info}\n\n"
            "Produce a high-quality, photorealistic full-body image consistent with the prompt and references. "
            "Cinematic lighting, sharp focus."
        )

        req = ImageGenerationRequest(
            prompt=combined_prompt,
            resolution="1024x1024",
            num_images=1,
            reference_images=refs,
        )

        service_result = self.generate_service.generate_image(req)
        # include stage label so callers (scripts) can inspect pipeline stage
        return {"stage": "combined", **service_result}
