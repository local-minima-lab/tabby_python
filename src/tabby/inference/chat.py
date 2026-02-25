import logging
from typing import Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ExtendedOpenAIConfig(BaseModel):
    kind: str = "openai/chat"
    model_name: str
    supported_models: Optional[list[str]] = None

    def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Ports the logic from chat.rs: ExtendedOpenAIConfig::process_request
        """
        # 1. Handle Model Fallback
        req_model = request.get("model")
        if not req_model:
            request["model"] = self.model_name
        elif self.supported_models and req_model not in self.supported_models:
            logger.warning(
                f"Model {req_model} is not supported, falling back to {self.model_name}"
            )
            request["model"] = self.model_name

        # 2. Strip parameters based on model 'kind'
        kind = self.kind.lower()
        
        # Mistral specific stripping
        if "mistral" in kind:
            request.pop("presence_penalty", None)
            request.pop("user", None)
            
        # OpenAI O-Series specific stripping
        elif "openai" in kind:
            model = request.get("model", "")
            if model.startswith("o1") or model.startswith("o3-mini"):
                request.pop("presence_penalty", None)
                request.pop("frequency_penalty", None)

        return request