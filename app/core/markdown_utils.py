def clean_whitespace(markdown_content: str) -> str:
    """Clean up extra empty lines in markdown content."""
    lines = markdown_content.split("\n")
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty
    return "\n".join(cleaned_lines).strip()
