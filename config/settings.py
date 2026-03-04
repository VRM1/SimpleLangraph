"""
Configuration loader for Simple LangGraph.

Loads settings from config.yml and provides easy access to configuration values.
"""

import yaml
from pathlib import Path
from typing import Any


class Settings:
    """Configuration settings loaded from config.yml"""

    def __init__(self):
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

    # LLM Settings
    @property
    def llm_provider(self) -> str:
        """LLM provider: 'ollama' or 'openai'"""
        return self._config["llm"]["provider"]

    @property
    def ollama_model(self) -> str:
        return self._config["llm"]["ollama"]["model"]

    @property
    def ollama_base_url(self) -> str:
        return self._config["llm"]["ollama"]["base_url"]

    @property
    def ollama_temperature(self) -> float:
        return self._config["llm"]["ollama"]["temperature"]

    @property
    def openai_model(self) -> str:
        return self._config["llm"]["openai"]["model"]

    @property
    def openai_temperature(self) -> float:
        return self._config["llm"]["openai"]["temperature"]

    @property
    def openai_api_key_env(self) -> str:
        return self._config["llm"]["openai"]["api_key_env"]

    # Logging Settings
    @property
    def log_level(self) -> str:
        return self._config["logging"]["level"]

    @property
    def show_routing(self) -> bool:
        return self._config["logging"]["show_routing"]

    @property
    def show_node_completion(self) -> bool:
        return self._config["logging"]["show_node_completion"]

    @property
    def show_llm_responses(self) -> bool:
        return self._config["logging"]["show_llm_responses"]


# Global settings instance
settings = Settings()
