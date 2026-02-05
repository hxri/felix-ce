from typing import Optional, List
import time
from pathlib import Path
from datetime import datetime

from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes
from src.schemas.generation import ImageGenerationRequest
from src.services.image_generation.flux_pro_edit_service import FluxProEditService


class ImagePipeline:

    def __init__(self):
        self.edit_service = FluxProEditService()

    def run(
        self,
        person: PersonAttributes,
        env: EnvironmentAttributes,
        description: str,
        person_reference_image: str,
        outfit_reference_images: List[str],
        no_download: bool = False,
    ) -> dict:
        """
        Run the unified image generation pipeline.
        """
        print(f"\n{'='*60}")
        print(f"[ImagePipeline] Starting unified pipeline")
        print(f"{'='*60}\n")

        identity_ref = person_reference_image
        
        # Ultra-aggressive face-locking prompt
        unified_prompt = (
            "Photorealistic full-body portrait. CRITICAL CONSTRAINTS:\n\n"
            
            "FACE & HEAD (ABSOLUTE PRIORITY - ZERO ALTERATIONS):\n"
            "- Image 1 contains the EXACT face to preserve\n"
            "- Extract and lock EVERY facial feature from Image 1:\n"
            "  * Exact facial shape and bone structure (cheekbones, jawline, chin, forehead)\n"
            "  * Exact eye shape, size, spacing, and color (iris, pupil, sclera)\n"
            "  * Exact eyebrow shape, thickness, color, and position\n"
            "  * Exact nose shape, size, nostrils, and bridge\n"
            "  * Exact mouth shape, lip size, lip color, and corners\n"
            "  * Exact facial proportions and symmetry\n"
            "  * Exact skin tone (match RGB values if possible)\n"
            "  * Exact skin texture, pores, freckles, moles, scars, blemishes\n"
            "  * Exact hair color, shade variation, highlights, lowlights\n"
            "  * Exact hair texture (straight, wavy, curly, coarse, fine)\n"
            "  * Exact hair style and cut\n"
            "  * Exact facial hair if present (beard, stubble, sideburns)\n"
            "  * Exact natural skin imperfections (do NOT smooth or airbrush)\n"
            "- Copy the face EXACTLY as-is with zero modification\n"
            "- Do NOT enhance, smooth, beautify, or alter any facial feature\n"
            "- Do NOT apply filters, makeup, or beauty effects\n"
            "- Do NOT change lighting on the face - preserve natural shadows and highlights\n"
            "- Do NOT alter eye color, pupil dilation, or eye shine\n"
            "- Do NOT change expression - preserve the exact expression from Image 1\n"
            "- The face in the output MUST be indistinguishable from Image 1\n"
            "- If the face looks even slightly different from Image 1, that is WRONG\n"
            "- Priority ranking: Face authenticity > Outfit quality > Background detail\n\n"
            
            "BODY & OUTFIT (MATCH REFERENCES):\n"
        )
        
        if outfit_reference_images and len(outfit_reference_images) > 0:
            roles = ["top/shirt", "bottom/pants", "shoes", "accessories"]
            for i, ref in enumerate(outfit_reference_images):
                role = roles[i] if i < len(roles) else "item"
                unified_prompt += f"- {role.capitalize()} (Image {i+2}): Match exact color, style, fit, fabric\n"
            
            unified_prompt += (
                "- Outfit pieces coordinate and harmonize together\n"
                "- Clothing fits naturally on the body\n"
                "- Realistic fabric texture, folds, and draping\n\n"
            )
        else:
            unified_prompt += f"- {env.apparel_type}\n\n"
        
        unified_prompt += (
            "BACKGROUND & ENVIRONMENT (COMPLETELY REPLACE):\n"
            f"- REMOVE any elements from the original image background\n"
            f"- CREATE a completely new background: {env.inferred_setting}\n"
            f"- APPLY lighting style: {env.visual_cues}\n"
            "- Fill entire background area with new environment\n"
            "- Do NOT blend or retain any original background elements\n"
            "- Make background detailed, realistic, and complete\n"
            "- Proper depth, perspective, and atmospheric lighting\n\n"
            
            "FINAL RENDERING:\n"
            "- Photorealistic professional photography\n"
            "- Full-body portrait, person centered\n"
            "- Sharp focus on face\n"
            "- Natural depth-of-field\n"
            "- No AI artifacts\n"
            "- Output Quality: The face MUST look like a real photograph of the person in Image 1"
        )

        # Build references
        all_refs = [identity_ref]
        if outfit_reference_images:
            all_refs.extend(outfit_reference_images)

        stage_req = ImageGenerationRequest(
            prompt=unified_prompt,
            resolution="9:16",
            num_images=1,
            reference_images=all_refs,
        )

        print(f"\n[UNIFIED STAGE] Generating photorealistic person image...")
        print(f"  - Face: ULTRA-LOCKED (zero alterations)")
        print(f"  - Outfit: {len(all_refs)-1} reference pieces")
        print(f"  - Background: COMPLETE REPLACEMENT")
        start_time = time.time()
        
        try:
            result = self.edit_service.generate_image(stage_req, no_download=no_download)
            latency = time.time() - start_time
            
            files = result.get("local_files", [])
            if not files and no_download:
                # If no_download is True, we don't expect local files
                print(f"✓ Complete in {latency:.2f}s (no_download=True)")
            elif not files:
                print(f"✗ Generation failed")
                return {"stage": "generation_failed", **result}
            else:
                image = files[0]
                print(f"✓ Complete in {latency:.2f}s: {image}")
            
            return {
                "stage": "unified_single_stage_complete",
                "local_files": result.get("local_files", []),
                "metadata_file": result.get("metadata_file"),
                "raw_response": result.get("raw_response"),
                "latency_sec": latency,
            }
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "stage": "generation_failed",
                "error": str(e),
                "local_files": [],
            }
