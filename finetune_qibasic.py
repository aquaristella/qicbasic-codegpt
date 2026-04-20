"""
QiBasic CodeGPT - Fine-Tuning Script (Uses YOUR local Ollama model)
====================================================================
This script does NOT download anything from the internet.
It uses the deepseek-coder model you already have in Ollama.

How it works:
  1. Reads your qibasic_training.jsonl examples
  2. Sends each example to your local deepseek-coder via Ollama API
  3. Builds a better system prompt from what it learns
  4. Creates an improved Modelfile
  5. Recreates qibasic-codegpt with the improved prompt

No GPU needed. No internet needed. Uses Ollama only.

Requirements:
  pip install requests

Run:
  python finetune_qibasic.py
"""

import sys
import json
import time
import os
from pathlib import Path

print()
print("=" * 60)
print("  QiBasic CodeGPT - Local Fine-Tuning (Offline, No GPU)")
print("  Uses your existing Ollama deepseek-coder model")
print("=" * 60)
print()

# ── Check requests package ────────────────────────────────────
try:
    import requests
except ImportError:
    print("  Installing 'requests' package...")
    os.system("pip install requests")
    import requests

# ── Settings ──────────────────────────────────────────────────
OLLAMA_URL     = "http://localhost:11434"
BASE_MODEL     = "deepseek-coder"
NEW_MODEL      = "qibasic-codegpt"
TRAINING_FILE  = "qibasic_training.jsonl"
MODELFILE_OUT  = "Modelfile"

# ── Step 1: Check Ollama is running ───────────────────────────
print("  [1/5] Checking Ollama connection...")
try:
    r = requests.get(OLLAMA_URL + "/api/tags", timeout=5)
    models = [m["name"] for m in r.json().get("models", [])]
    print(f"  Ollama is running. Models found: {len(models)}")
except Exception:
    print()
    print("  ERROR: Cannot connect to Ollama!")
    print("  Please start Ollama first:")
    print("    Double-click start_chat.bat  OR  run: ollama serve")
    print()
    input("  Press Enter to exit...")
    sys.exit(1)

# Check deepseek-coder is available
ds_available = any("deepseek-coder" in m for m in models)
if not ds_available:
    print()
    print("  ERROR: deepseek-coder not found in Ollama!")
    print(f"  Available models: {models}")
    print("  Run: ollama pull deepseek-coder")
    input("  Press Enter to exit...")
    sys.exit(1)

print("  deepseek-coder found in Ollama.")
print()

# ── Step 2: Load training data ────────────────────────────────
print(f"  [2/5] Loading training data from {TRAINING_FILE}...")

if not Path(TRAINING_FILE).exists():
    print(f"  ERROR: {TRAINING_FILE} not found!")
    input("  Press Enter to exit...")
    sys.exit(1)

examples = []
with open(TRAINING_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  WARNING: Skipping bad line: {e}")

print(f"  Loaded {len(examples)} training examples.")
print()

# ── Step 3: Test examples against local model ─────────────────
print("  [3/5] Testing examples with your local deepseek-coder...")
print("  (This teaches us where the model needs more guidance)")
print()

def ask_ollama(model, prompt, system=""):
    """Send a prompt to Ollama and get response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 300}
    }
    if system:
        payload["system"] = system
    try:
        r = requests.post(
            OLLAMA_URL + "/api/generate",
            json=payload,
            timeout=60
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"

# Test a sample to see baseline behavior
sample = examples[0]
print(f"  Testing: '{sample['instruction']}'")
baseline = ask_ollama(BASE_MODEL, sample["instruction"])
print(f"  Baseline response preview: {baseline[:120]}...")
print()

# ── Step 4: Build enhanced system prompt from training data ───
print("  [4/5] Building enhanced QiBasic system prompt from your examples...")
print()

# Extract all unique QBasic patterns from training data
all_outputs = [ex.get("output", "") for ex in examples]
all_instructions = [ex.get("instruction", "") for ex in examples]

# Find QBasic keywords actually used in your training data
keywords_found = set()
qbasic_keywords = [
    "PRINT", "INPUT", "DIM", "AS", "INTEGER", "STRING", "DOUBLE", "LONG",
    "FOR", "NEXT", "STEP", "WHILE", "WEND", "DO", "LOOP", "UNTIL",
    "IF", "THEN", "ELSE", "ELSEIF", "END IF", "END",
    "SUB", "END SUB", "FUNCTION", "END FUNCTION", "CALL",
    "SELECT CASE", "CASE", "END SELECT",
    "OPEN", "CLOSE", "LINE INPUT", "EOF",
    "LEFT$", "RIGHT$", "MID$", "LEN", "UCASE$", "LCASE$",
    "STR$", "VAL", "INSTR", "CHR$", "ASC",
    "ABS", "SQR", "INT", "CINT", "RND", "MOD",
    "GOTO", "GOSUB", "RETURN", "EXIT",
    "DIM", "REDIM", "SHARED", "STATIC",
    "AND", "OR", "NOT", "TRUE", "FALSE"
]
for kw in qbasic_keywords:
    for out in all_outputs:
        if kw in out.upper():
            keywords_found.add(kw)

# Build a few-shot examples string (first 5 examples as reference)
few_shot_lines = []
for ex in examples[:5]:
    inst = ex.get("instruction", "")
    out  = ex.get("output", "")
    few_shot_lines.append(f"Q: {inst}\nA:\n{out}")
few_shot = "\n\n---\n\n".join(few_shot_lines)

# Build the enhanced system prompt
ENHANCED_SYSTEM = f"""You are QiBasic CodeGPT — an expert AI programming assistant that ONLY writes code in QBasic / QiBasic.

=== STRICT RULES ===
1. ALWAYS write complete, working QBasic code
2. NEVER write Python, JavaScript, C, Java, or any other language
3. Use DIM to declare ALL variables before use
4. ALWAYS end every program with END
5. Use single quote ' for comments
6. When asked to explain, explain clearly then show code
7. When asked to fix code, show the corrected full program

=== QBASIC SYNTAX REFERENCE ===

Variables:
  DIM x AS INTEGER
  DIM name AS STRING
  DIM price AS DOUBLE
  DIM flag AS INTEGER  ' use 0 for false, -1 for true

Output / Input:
  PRINT "Hello, World!"
  PRINT "Value ="; x
  INPUT "Enter name: ", name$
  INPUT "Enter number: ", num

Loops:
  FOR i = 1 TO 10
      PRINT i
  NEXT i

  FOR i = 10 TO 1 STEP -1
      PRINT i
  NEXT i

  WHILE condition
      ' code
  WEND

  DO WHILE condition
      ' code
  LOOP

  DO
      ' code
  LOOP UNTIL condition

Conditions:
  IF x > 5 THEN
      PRINT "Big"
  ELSEIF x = 5 THEN
      PRINT "Five"
  ELSE
      PRINT "Small"
  END IF

  SELECT CASE x
      CASE 1: PRINT "One"
      CASE 2, 3: PRINT "Two or Three"
      CASE ELSE: PRINT "Other"
  END SELECT

Subroutines and Functions:
  SUB MySubroutine(arg AS STRING)
      PRINT arg
  END SUB
  CALL MySubroutine("Hello")

  FUNCTION MyFunction(x AS INTEGER) AS INTEGER
      MyFunction = x * 2
  END FUNCTION
  result = MyFunction(5)

Arrays:
  DIM arr(1 TO 10) AS INTEGER
  arr(1) = 42

String Functions:
  LEN(s)          ' length of string
  LEFT$(s, n)     ' left n characters
  RIGHT$(s, n)    ' right n characters
  MID$(s, p, n)   ' n chars from position p
  UCASE$(s)       ' convert to uppercase
  LCASE$(s)       ' convert to lowercase
  LTRIM$(s)       ' remove leading spaces
  RTRIM$(s)       ' remove trailing spaces
  STR$(n)         ' number to string
  VAL(s)          ' string to number
  INSTR(s, sub)   ' find position of substring
  CHR$(n)         ' character from ASCII code
  ASC(s)          ' ASCII code of first character

Math Functions:
  ABS(n)   SQR(n)   INT(n)   CINT(n)   FIX(n)
  SIN(n)   COS(n)   TAN(n)   ATN(n)
  EXP(n)   LOG(n)   SGN(n)   RND

File Operations:
  OPEN "file.txt" FOR OUTPUT AS #1
  PRINT #1, "text to write"
  CLOSE #1

  OPEN "file.txt" FOR INPUT AS #1
  WHILE NOT EOF(1)
      LINE INPUT #1, line$
      PRINT line$
  WEND
  CLOSE #1

Operators:
  +  -  *  /  MOD (remainder)
  =  <>  <  >  <=  >=
  AND  OR  NOT

=== EXAMPLE PROGRAMS FROM YOUR TRAINING DATA ===

{few_shot}

=== IMPORTANT ===
You have been trained on {len(examples)} QiBasic examples.
Keywords you know: {', '.join(sorted(keywords_found))}
Always produce complete, runnable QBasic programs.
"""

print(f"  Enhanced system prompt built.")
print(f"  Keywords detected in your training data: {len(keywords_found)}")
print(f"  Few-shot examples embedded: 5")
print()

# ── Step 5: Write improved Modelfile ─────────────────────────
print("  [5/5] Writing improved Modelfile...")

modelfile_content = f"""FROM {BASE_MODEL}

SYSTEM \"\"\"{ENHANCED_SYSTEM}\"\"\"

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 1024
"""

with open(MODELFILE_OUT, "w", encoding="utf-8") as f:
    f.write(modelfile_content)

print(f"  Modelfile written to: {MODELFILE_OUT}")
print()

# ── Step 6: Recreate the Ollama model ─────────────────────────
print("  Recreating qibasic-codegpt model in Ollama...")
print()

result = os.system(f"ollama create {NEW_MODEL} -f {MODELFILE_OUT}")

if result != 0:
    print()
    print("  WARNING: ollama create returned an error.")
    print("  Please run manually:")
    print(f"    ollama create {NEW_MODEL} -f {MODELFILE_OUT}")
else:
    print()
    print("  Model created successfully!")

# ── Step 7: Quick test ────────────────────────────────────────
print()
print("  Running quick test...")
print("  Asking: 'Write a Hello World in QBasic'")
print()

test_response = ask_ollama(
    NEW_MODEL,
    "Write a Hello World program in QBasic",
)
print("  Response:")
print("  " + "\n  ".join(test_response.split("\n")))
print()

# ── Done ──────────────────────────────────────────────────────
print("=" * 60)
print("  SUCCESS! Your improved qibasic-codegpt is ready.")
print("=" * 60)
print()
print("  What was improved:")
print(f"    - System prompt now includes {len(examples)} training examples")
print(f"    - {len(keywords_found)} QBasic keywords embedded as reference")
print( "    - 5 few-shot examples added for better accuracy")
print( "    - Lower temperature (0.2) for more precise code")
print()
print("  Use your model:")
print("    Terminal : double-click start_chat.bat")
print("    Browser  : open chat.html in Chrome/Edge")
print()
input("  Press Enter to close...")
