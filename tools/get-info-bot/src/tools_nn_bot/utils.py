"""Utility functions for Tools_NNBot."""

import re


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2.

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for MarkdownV2
    """
    # Characters that need to be escaped in MarkdownV2
    # except for * and _ which are used for formatting
    escape_chars = r"\.()>#+\-=|{}\[\]!"

    # Escape each special character
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")

    return text
