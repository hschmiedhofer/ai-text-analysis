import re


class TextSanitizer:
    """Service for sanitizing and validating text input."""

    # Control characters to remove (keep \n, \r, \t)
    CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

    # Zero-width and other problematic Unicode
    ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200D\uFEFF]")

    # Multiple whitespace normalization
    WHITESPACE_NORMALIZE = re.compile(r"\s+")

    @classmethod
    def sanitize(cls, text: str, max_length: int | None = None) -> str:
        """Sanitize input text for safe processing."""
        if not text:
            return text

        original_length = len(text)

        # Apply sanitization steps
        text = cls.CONTROL_CHARS.sub("", text)
        text = cls.ZERO_WIDTH_CHARS.sub("", text)
        text = cls.WHITESPACE_NORMALIZE.sub(" ", text)
        text = text.strip()

        # Validation checks
        if original_length > 100 and len(text) < (original_length * 0.5):
            raise ValueError("Text contains too many invalid characters")

        if max_length and len(text) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length}")

        return text
