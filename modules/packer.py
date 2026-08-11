from pathlib import Path

def pack_context(results: list[dict], query: str, output_path: str = "packed_context.txt"):
    """Formats retrieved full files into an LLM-friendly context structure."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("<context>\n")
        
        for item in results:
            file_path = item["file_path"]
            content = item["content"]
            
            f.write(f'  <file path="{file_path}">\n')
            f.write('    <![CDATA[\n')
            f.write(f'{content}\n')
            f.write(']]>\n')
            f.write("  </file>\n\n")
            
        f.write("</context>\n\n")
        f.write(f"<user_query>\n{query}\n</user_query>\n")