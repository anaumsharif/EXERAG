from utils.initialize import cohere_llm_model, openai_llm_model

from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()

COHERE_API_KEY = config[env_name].COHERE_API_KEY

def get_llm_model(model_name: str, temperature: float = 0.7):
    env = load_env_variables()
    if model_name == 'openai':
        return openai_llm_model(api_key=config[env].OPENAI_API_KEY, temperature=temperature)
    elif model_name == 'cohere':
        return cohere_llm_model(config[env].COHERE_API_KEY, temperature=temperature)
    else:
        raise ValueError(f"Unknown LLM model: {model_name}")