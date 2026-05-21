---
name: markitdown
description: >
  Convert files (PDF, EPUB, DOCX, PPTX, XLSX, HTML, images, etc.) to Markdown
  using the MarkItDown library. Trigger on: user says "convert to markdown",
  "markitdown", "轉 markdown", or provides a file that needs format conversion.
---

# MarkItDown — File to Markdown Converter

Convert various document formats to Markdown using the `markitdown` library.

## Supported Formats

| Format | Extensions |
|--------|-----------|
| PDF | `.pdf` |
| EPUB | `.epub` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx` |
| HTML | `.html`, `.htm` |
| CSV | `.csv` |
| JSON | `.json` |
| XML | `.xml` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg` (extracts text via OCR if configured) |
| Plain text | `.txt` |
| Markdown | `.md` (passthrough) |
| ZIP | `.zip` (extracts and converts contents) |

## Usage

```bash
python3 ~/.claude/skills/markitdown/MarkItDown.py <input_file> [output_file]
```

- If `output_file` is omitted, the markdown content is printed to stdout.
- If `output_file` is provided, the markdown is written to that file.

## When Invoking as a Skill

When the user requests a file conversion:

1. Confirm the input file path exists
2. Ask for an output path if not specified (default: same name with `.md` extension in the same directory)
3. Run the conversion
4. Confirm the result or display the content if appropriate
