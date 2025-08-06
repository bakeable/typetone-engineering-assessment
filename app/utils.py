import random
import string
import re
from urllib.parse import urlparse


def generate_shortcode(length: int = 6) -> str:
    """
    Generate a random shortcode with specified length.
    Contains only alphanumeric characters and underscores.
    """
    characters = string.ascii_letters + string.digits + "_"
    return "".join(random.choice(characters) for _ in range(length))


def is_valid_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_shortcode(shortcode: str) -> bool:
    """
    Validate if a shortcode meets the basic requirements.
    For user-provided shortcodes, any format is allowed.
    """
    if not shortcode or len(shortcode) == 0:
        return False
    return True


def is_auto_generated_shortcode_valid(shortcode: str) -> bool:
    """
    Validate if an auto-generated shortcode meets the strict requirements:
    - Length of 6 characters
    - Only alphanumeric characters and underscores
    """
    if len(shortcode) != 6:
        return False
    pattern = re.compile(r"^[a-zA-Z0-9_]+$")
    return bool(pattern.match(shortcode))
