from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes


# class ImagePromptService:

#     def build_prompt(
#         self,
#         person: PersonAttributes,
#         env: EnvironmentAttributes,
#         base_description: str,
#     ) -> str:

#         prompt = f"""
#         High quality professional full body portrait photo.

#         Subject:
#         {base_description}

#         Physical attributes:
#         Height: {person.height_cm} cm
#         Weight: {person.weight_kg} kg
#         Gender: {person.gender}
#         Age: {person.age}

#         Outfit:
#         {env.apparel_type}

#         Setting:
#         {env.inferred_setting}

#         Visual cues:
#         {env.visual_cues}

#         Ultra realistic, sharp focus, cinematic lighting,
#         studio photography quality, 85mm lens.
#         """

#         return " ".join(prompt.split())

class ImagePromptService:

    def build_base_identity_prompt(self, person, env, description: str):
        prompt = f"{description}. "
        prompt += f"Height: {person.height_cm} cm, Weight: {person.weight_kg} kg, Age: {person.age}, Gender: {person.gender}. "
        prompt += f"Apparel: {env.apparel_type}, Setting: {env.inferred_setting}, Visual cues: {env.visual_cues}."
        prompt += " Identity must match reference image. "
        return prompt

    def build_outfit_edit_prompt(self, outfit_refs: list[str]):
        prompt = "Without changing the face of the person and body shape, edit the image using reference images to apply clothing and accessories:\n"
        roles = ["top wear", "bottom wear", "shoes", "accessories"]
        for i, ref in enumerate(outfit_refs):
            if i >= len(roles):
                break
            prompt += f"- Image {i+2}: {roles[i]} reference image.\n"
        prompt += "Preserve face, body shape, background, and lighting from base image."
        return prompt
