#  import markdown
import requests
from utils.initialize import load_env_variables
from utils.config_settings import config


# 'COHERE_API_KEY'="pmbYREh3ZBIpvKRxO8R54bRr4xQt4MmJXh7gnNsr"
env_name = load_env_variables()

source = config[env_name].COHERE_API_KEY

import cohere
TOKENIZERS = {
    "command-r": "https://storage.googleapis.com/cohere-public/tokenizers/command-r.json",
    "command-r-plus": "https://storage.googleapis.com/cohere-public/tokenizers/command-r-plus.json",
}



def get_special_tokens_set(tokenizer_url=TOKENIZERS["command-r"]):
    """
    Fetches the special tokens set from the given tokenizer URL.

    Args:
        tokenizer_url (str): The URL to fetch the tokenizer from.

    Returns:
        set: A set of special tokens.
    """
    # https://docs.cohere.com/docs/tokens-and-tokenizers
    response = requests.get(tokenizer_url)
    return set([tok["content"] for tok in response.json()["added_tokens"]])


def make_text_tokenization_safe(
    content: str, special_tokens_set: set = get_special_tokens_set()
) -> str:
    """
    Makes the text safe for tokenization by removing special tokens.

    Args:
        content: A string containing the text to be processed.
        special_tokens_set: A set of special tokens to be removed from the text.

    Returns:
        A string with the special tokens removed.
    """

    def remove_special_tokens(text: str) -> str:
        """
        Removes special tokens from the given text.

        Args:
            text: A string representing the text.

        Returns:
            The text with special tokens removed.
        """
        for token in special_tokens_set:
            text = text.replace(token, "")
        return text

    cleaned_content = remove_special_tokens(content)
    return cleaned_content