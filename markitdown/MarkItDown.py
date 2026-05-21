import sys
from markitdown import MarkItDown

if len(sys.argv) < 2:
    print("Usage: python MarkItDown.py <input_file> [output_file]")
    print("If output_file is omitted, prints to stdout.")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else None

md = MarkItDown(enable_plugins=False)
result = md.convert(input_path)

if output_path:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result.text_content)
    print(f"Converted {input_path} -> {output_path}")
else:
    print(result.text_content)
