"""
=============================================================================
MARKDOWN SERVICE
=============================================================================
Purpose: Convert Markdown content to HTML for display.

Markdown is used throughout the portfolio for:
- Blog post content
- Project descriptions
- Rich text formatting

This service provides a simple, secure Markdown-to-HTML converter.
=============================================================================
"""

import markdown
from markupsafe import Markup


# Configure the Markdown converter
# Extensions add features beyond basic Markdown
MARKDOWN_EXTENSIONS = [
    "fenced_code",      # ```code blocks```
    "tables",           # | Tables | Like | This |
    "nl2br",            # Convert newlines to <br>
    "smarty",           # Smart quotes and dashes
    "toc",              # Table of contents generation
    "codehilite",       # Syntax highlighting hooks
]

# Configuration for extensions
EXTENSION_CONFIGS = {
    "codehilite": {
        # Use CSS classes instead of inline styles
        "css_class": "highlight",
        # Don't guess language if not specified
        "guess_lang": False,
    },
}


def render_markdown(content: str) -> Markup:
    """
    Convert Markdown text to HTML.
    
    Uses Python-Markdown with safe extensions.
    Returns a Markup object that Jinja2 won't escape.
    
    Args:
        content: Markdown text to convert
    
    Returns:
        Markup: HTML string (safe for template rendering)
    
    Example:
        html = render_markdown("# Hello\n\nThis is **bold**.")
        # Returns: <h1>Hello</h1>\n<p>This is <strong>bold</strong>.</p>
    
    In templates:
        {{ content | markdown }}  (using as filter)
        {{ render_markdown(post.content) }}  (direct call)
    """
    if not content:
        return Markup("")
    
    # Create Markdown converter
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=EXTENSION_CONFIGS,
        # Output format
        output_format="html5",
    )
    
    # Convert to HTML
    html = md.convert(content)
    
    # Return as Markup (tells Jinja2 it's safe HTML)
    return Markup(html)


def markdown_filter(content: str) -> Markup:
    """
    Jinja2 filter wrapper for render_markdown.
    
    This is registered as a template filter in main.py.
    
    Usage in templates:
        {{ post.content | markdown }}
    """
    return render_markdown(content)


def extract_excerpt(content: str, max_length: int = 200) -> str:
    """
    Extract plain text excerpt from Markdown content.
    
    Removes Markdown formatting and truncates.
    Useful for previews and meta descriptions.
    
    Args:
        content: Markdown text
        max_length: Maximum excerpt length
    
    Returns:
        str: Plain text excerpt
    
    Example:
        excerpt = extract_excerpt("# Title\n\nSome **bold** text here.")
        # Returns: "Title Some bold text here."
    """
    if not content:
        return ""
    
    # Simple Markdown stripping (covers common cases)
    # Remove headers
    text = content.replace("#", "")
    # Remove bold/italic markers
    text = text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
    # Remove code blocks
    text = text.replace("`", "")
    # Remove links (basic)
    import re
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    # Truncate
    if len(text) > max_length:
        # Find last word boundary
        text = text[:max_length]
        last_space = text.rfind(" ")
        if last_space > max_length // 2:
            text = text[:last_space]
        text += "..."
    
    return text.strip()


def estimate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for content.
    
    Based on average reading speed.
    
    Args:
        content: Text content (Markdown or plain)
        words_per_minute: Reading speed (default 200)
    
    Returns:
        int: Estimated minutes to read
    
    Example:
        minutes = estimate_reading_time(post.content)
        # Returns: 5 (for ~1000 word article)
    """
    if not content:
        return 0
    
    # Count words (split on whitespace)
    word_count = len(content.split())
    
    # Calculate minutes, minimum 1
    minutes = max(1, round(word_count / words_per_minute))
    
    return minutes
