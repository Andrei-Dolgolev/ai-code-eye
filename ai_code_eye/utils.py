import re
from typing import List

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    This is a simple approximation - it splits on whitespace and punctuation.
    While not as accurate as tiktoken, it's sufficient for basic chunking.
    """
    # Split on whitespace and punctuation
    tokens: List[str] = re.findall(r'\b\w+\b|[^\w\s]', text)
    
    # Add extra tokens for newlines (as they're significant in code)
    newline_count = text.count('\n')
    
    # GPT models typically treat most tokens as ~4 characters
    # We'll count long words as multiple tokens
    extra_tokens = sum(len(word) // 4 for word in tokens if len(word) > 4)
    
    return len(tokens) + newline_count + extra_tokens 