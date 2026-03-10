#!/usr/bin/env python3
"""Fix Chinese double quotes in JSON file to make it valid JSON."""
import re, json, sys

filepath = "data/daily-content-2026-03-10.json"
text = open(filepath, "r", encoding="utf-8").read()

LEFT_QUOTE = "\u201c"   # "
RIGHT_QUOTE = "\u201d"  # "

def fix_chinese_quotes(text):
    """Replace ASCII double quotes used as Chinese quotation marks with Unicode curly quotes."""
    # Opening quote: preceded by CJK char or CJK punctuation, followed by non-JSON-structural char
    pattern_open = re.compile(r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2014])"([^",\n\r:{}])')
    text = pattern_open.sub(r'\g<1>' + LEFT_QUOTE + r'\g<2>', text)
    
    # Closing quote: preceded by non-structural char, followed by CJK char/punctuation or common endings
    pattern_close = re.compile(r'([^\\",\n\r:{}\[\]])"\s*([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2014;,.——。、])')
    text = pattern_close.sub(r'\g<1>' + RIGHT_QUOTE + r'\g<2>', text)
    
    # Also handle: >" pattern (after HTML tag closing)
    text = re.sub(r'(>)"([^",\n\r:{}])', r'\g<1>' + LEFT_QUOTE + r'\g<2>', text)
    
    # Handle closing quote before period, semicolon etc
    text = re.sub(r'([^\\",\n\r:{}\[\]])"(\s*[。；;,.])', r'\g<1>' + RIGHT_QUOTE + r'\g<2>', text)
    
    return text

# Run multiple passes
for i in range(10):
    new_text = fix_chinese_quotes(text)
    if new_text == text:
        break
    text = new_text

try:
    data = json.loads(text)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK: JSON fixed and validated!")
    sys.exit(0)
except json.JSONDecodeError as e:
    print(f"FAIL: {e}")
    lines = text.split("\n")
    ln = e.lineno
    col = e.colno
    line = lines[ln-1]
    start = max(0, col-40)
    end = min(len(line), col+40)
    print(f"  Context: ...{line[start:end]}...")
    for i in range(max(0,col-3), min(len(line), col+3)):
        print(f"    [{i}] = {repr(line[i])} ord={ord(line[i])}")
    sys.exit(1)
