import asyncio
from app.parsers.registry import parse_document
import os

async def test():
    # Make a dummy txt file
    with open("test.md", "w") as f:
        f.write("# Hello World\n\nThis is a test.")
        
    try:
        md = await asyncio.to_thread(parse_document, "test.md", "markdown")
        print("Success! Markdown length:", len(md))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
