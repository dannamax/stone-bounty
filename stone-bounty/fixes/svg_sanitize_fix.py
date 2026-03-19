"""
SVG Security Sanitization Fix for grazer-skill

This fix adds proper SVG sanitization to prevent XSS vulnerabilities
when user-controlled input is interpolated into SVG templates.
"""

def sanitize_svg_text(text: str) -> str:
    """
    Sanitize text for safe insertion into SVG context.
    
    This function handles both XML entity escaping and SVG-specific
    XSS vectors that could be exploited in SVG contexts.
    
    Args:
        text: User-controlled input string
        
    Returns:
        Sanitized string safe for SVG interpolation
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Basic XML entity escaping (already partially done in _truncate)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    
    # Remove or neutralize SVG-specific XSS vectors
    # Remove script tags completely
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove dangerous attributes that could execute JavaScript
    dangerous_patterns = [
        r'on\w+\s*=',  # onload, onclick, onmouseover, etc.
        r'xlink:href\s*=\s*["\']?javascript:',  # xlink:href with javascript
        r'href\s*=\s*["\']?javascript:',  # href with javascript  
        r'style\s*=\s*["\'][^"\']*expression\([^"\']*\)',  # CSS expressions
        r'<\s*iframe[^>]*>',  # iframe tags
        r'<\s*embed[^>]*>',  # embed tags
        r'<\s*object[^>]*>',  # object tags
        r'javascript\s*:',  # javascript: protocol
        r'data\s*:',  # data: protocol (can be dangerous in some contexts)
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove any remaining HTML/XML tags (since we only want text content)
    text = re.sub(r'<[^>]+>', '', text)
    
    return text


# Integration points in the existing code:
# 1. Replace the current _truncate function with enhanced version
# 2. Apply sanitize_svg_text before passing user input to templates
# 3. Ensure all user-controlled strings are sanitized

def enhanced_truncate(text: str, maxlen: int) -> str:
    """Enhanced XML-safe truncation with full SVG sanitization."""
    # First apply full SVG sanitization
    sanitized_text = sanitize_svg_text(text)
    
    # Then apply length truncation
    if len(sanitized_text) > maxlen:
        return sanitized_text[:maxlen - 1] + "~"
    return sanitized_text