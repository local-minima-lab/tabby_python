import time

def default_seed() -> int:
    """Matches Rust's default_seed() using milliseconds since epoch."""
    return int(time.time() * 1000)

def clip_prompt(prompt: str, max_length: int) -> str:
    """
    Retains only the latter part of the prompt, limiting content to max_length.
    Python slicing respects character boundaries by default.
    """
    if len(prompt) <= max_length:
        return prompt
    return prompt[-max_length:]