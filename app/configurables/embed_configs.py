from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()
from utils.initialize import cohere_embedding_model, openai_embed_model

def get_embedding_model(model_name: str):
    env = load_env_variables()
    if model_name == 'openai':
        return openai_embed_model(api_key=config[env].OPENAI_API_KEY)
    elif model_name == 'cohere':
        return cohere_embedding_model(config[env].COHERE_API_KEY)
    else:
        # Default to Cohere if unknown name is passed
        return cohere_embedding_model(config[env].COHERE_API_KEY)