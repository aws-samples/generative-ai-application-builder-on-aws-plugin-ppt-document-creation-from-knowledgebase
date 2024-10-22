from typing import Optional

from bisheng.prompting.templates.base_prompt_template import BasePromptTemplate


class OneShotWithContextPromptTemplate(BasePromptTemplate):

    generate_prompt: str = Optional[str]
    shot_text: str = Optional[str]
    context: str = Optional[str]
    output_filter: str = Optional[str]

    @classmethod
    def get_required_params(cls):
        return {"generate_prompt", "shot_text", "context", "output_filter"}

    @staticmethod
    def create_instruction(**input_data) -> str:
        generate_prompt = input_data.get("generate_prompt")
        shot_text = input_data.get("shot_text")
        context = input_data.get("context")
        output_filter = input_data.get("output_filter")
        return (f"INPUT DATA:{generate_prompt}\n"
                f"EXAMPLES:{shot_text}\n"
                f"CONTEXT:{context}\n"
                f"OUTPUT FORMAT:{output_filter}")


class GaabWithKnowledgeBasePromptTemplate(BasePromptTemplate):

    generate_prompt: str = Optional[str]
    shot_text: str = Optional[str]
    output_filter: str = Optional[str]

    @classmethod
    def get_required_params(cls):
        return {"generate_prompt", "shot_text", "output_filter"}

    @staticmethod
    def create_instruction(**input_data) -> str:
        generate_prompt = input_data.get("generate_prompt")
        shot_text = input_data.get("shot_text")
        output_filter = input_data.get("output_filter")
        return (f"INPUT DATA:{generate_prompt}\n"
                f"EXAMPLES:{shot_text}\n"
                f"OUTPUT FORMAT:{output_filter}")

    # def to_json(self):
    #     return {
    #         "generate_prompt": self.generate_prompt,
    #         "shot_text": self.shot_text,
    #         "output_filter": self.output_filter
    #     }
