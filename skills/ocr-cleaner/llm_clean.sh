#!/bin/bash
# Phase 3: per-chunk LLM extraction → JSON → merge → questions.json
#
# Usage:
#   bash llm_clean.sh input.md --source wangdao-ds --subject data-structure
#         [--chunks-dir chunks] [--output-dir output] [--output questions.json]
#
# Each chunk is sent to claude -p with the JSON-extraction prompt.
# Output JSON files are then merged via validate.py into questions.json.
#
# --output: final questions.json path (default: {input_basename}_questions.json)
#           if path ends with /, treated as directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_FILE="${1:?Usage: $0 input.md --source <source> --subject <subject>}"
shift

CHUNKS_DIR="chunks"
OUTPUT_DIR="output"
FINAL_OUTPUT=""
SOURCE=""
SUBJECT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --chunks-dir) CHUNKS_DIR="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --output) FINAL_OUTPUT="$2"; shift 2 ;;
        --source) SOURCE="$2"; shift 2 ;;
        --subject) SUBJECT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$SOURCE" || -z "$SUBJECT" ]]; then
    echo "Error: --source and --subject are required"
    exit 1
fi

if [[ ! -d "$CHUNKS_DIR" ]]; then
    echo "Error: chunks directory '$CHUNKS_DIR' not found. Run chunk.py first."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Determine final output path
INPUT_BASENAME="$(basename "${INPUT_FILE%.*}")"
if [[ -z "$FINAL_OUTPUT" ]]; then
    FINAL_OUTPUT="${INPUT_BASENAME}_questions.json"
elif [[ "$FINAL_OUTPUT" == */ ]]; then
    # Trailing slash → treat as directory
    mkdir -p "$FINAL_OUTPUT"
    FINAL_OUTPUT="${FINAL_OUTPUT}${INPUT_BASENAME}_questions.json"
fi

# Build the prompt template by substituting source/subject
PROMPT=$(cat "$SCRIPT_DIR/prompt.md")
PROMPT="${PROMPT//\{source\}/$SOURCE}"
PROMPT="${PROMPT//\{subject\}/$SUBJECT}"

# Get chunk files sorted by name
chunks=("$CHUNKS_DIR"/*.md)
if [[ ${#chunks[@]} -eq 0 ]]; then
    echo "Error: no .md files in $CHUNKS_DIR/"
    exit 1
fi

echo "Processing ${#chunks[@]} chunks via claude -p..."
echo ""

for chunk in "${chunks[@]}"; do
    basename=$(basename "$chunk" .md)
    output="$OUTPUT_DIR/$basename.json"
    echo "  Extracting $basename..."
    claude -p "$PROMPT" < "$chunk" > "$output"
    echo "    → $output"
done

echo ""
echo "All chunks processed. Merging via validate.py..."

python3 "$SCRIPT_DIR/validate.py" "$OUTPUT_DIR" "$FINAL_OUTPUT"

echo "Done."
