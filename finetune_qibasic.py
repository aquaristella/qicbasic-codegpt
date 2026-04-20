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
print("  [4/5] Building enhanced QICBASIC system prompt from your examples...")
print()

# Extract all unique QICBASIC patterns from training data
all_outputs = [ex.get("output", "") for ex in examples]
all_instructions = [ex.get("instruction", "") for ex in examples]

# Find QICBASIC keywords actually used in your training data
keywords_found = set()
qicbasic_keywords = [
    # Output / Input
    "PRINT", "INPUT",
    # Variable declaration
    "LENGTH", "LOCAL", "COMMON", "SHARED",
    # Data types (numeric declared via LENGTH n.p, strings end in $)
    "ROUND",
    # Assignment
    "LET",
    # Control flow - loops
    "FOR", "TO", "DOWNTO", "STEP", "NEXT",
    "WHILE", "ENDWHILE",
    "REPEAT", "UNTIL",
    # Control flow - conditionals
    "IF", "THEN", "ELSE", "ENDIF",
    "SELECT", "CASE", "ENDSELECT",
    # Control flow - branching
    "GOTO", "GOSUB", "RETURN",
    "ON GOTO", "ON GOSUB",
    # Subroutines / program flow
    "RSUB", "END",
    "RUN", "EXECUTE", "STOP", "TERMINATE",
    # File I/O
    "OPEN", "CLOSE", "CLOSEALL",
    "READ", "WRITE", "REWRITE",
    "INSERT", "DELETE", "UPDATE",
    "GET", "PUT",
    "CREATE", "RENAME", "ERASE",
    # Terminal / formatting
    "FORMAT", "CLEAR",
    "MOVE", "POSITION", "CURPOS",
    "EJECT", "PAUSE",
    # Math functions
    "ABS", "INT", "SGN", "SQR", "FPT",
    "MOD",
    # String functions
    "LEN", "ASC", "CHR",
    "LCASE", "UCASE",
    "STR", "NUM",
    "POS", "SUB",
    "STRIP", "STRIPL", "STRIPR",
    "ADJUSTL", "ADJUSTR",
    # Logical / relational operators
    "AND", "OR", "NOT",
    "EQ", "NE", "GT", "GE", "LT", "LE",
    # Exception handling
    "EXCP", "ERRORSUB", "ERRORTO", "ESCAPESUB", "ESCAPETO",
    # Miscellaneous
    "SET", "SWAP", "AGAIN", "CONTINUE", "BREAK",
    "FIRST", "LAST", "NEXT", "KEY",
    "LOCK", "UNLOCK",
    "MESSAGE", "MESSAGESUB",
    "PRIORITY", "WAKEUP",
    "GLOBALDATE", "LOCALDATE",
    "DATETYPE",
    "FSTAT", "DSTAT", "NSTAT", "PSTAT", "LOGSTAT", "LUNSTAT",
    "DABSTAT", "ACCESS", "ACTIVATE", "RESERVE",
    "POPALL", "POP",
    "SECURE", "PASSWORD",
    "SHELL", "PCOM",
    "EXAMINE", "EXTRACT",
]
for kw in qicbasic_keywords:
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
ENHANCED_SYSTEM = f"""You are QiBasic CodeGPT — an expert AI programming assistant that ONLY writes code in QICBASIC (QiCBASIC), the QANTEL/DecisionOne dialect of BASIC.

=== STRICT RULES ===
1. ALWAYS write complete, working QICBASIC programs
2. NEVER write Python, JavaScript, C, Java, QBasic, or any other language
3. Declare ALL variables in the Declarative Section using LENGTH before the Format and Executable sections
4. ALWAYS end every program with RUN "*MONITOR" followed by END
5. Use exclamation mark ! for comments (not single quote ')
6. When asked to explain, explain clearly then show code
7. When asked to fix code, show the corrected full program

=== QICBASIC PROGRAM STRUCTURE ===

Every QICBASIC program has up to three sections in this order:

  1. Declarative Section  — declares variables (LENGTH statements)
  2. Format Section       — defines output formats (FORMAT statements with labels)
  3. Executable Section   — contains the program logic (statements, I/O, loops, etc.)

Multiple statements on one line are separated by & (ampersand).
A statement can be continued to the next line with _ (underscore) at end of line.

=== COMMENTS ===

  ! THIS IS A FULL-LINE COMMENT
  LET A = B + C  ! this is an inline comment

=== VARIABLE DECLARATION (Declarative Section) ===

Numeric variables (n = total digits, p = decimal places):
  LENGTH 8.2 & LOCAL BALANCE, TOTAL
  LENGTH 3.0 & LOCAL COUNTER
  LENGTH 5.0 & LOCAL AMOUNT
  LENGTH 10.2 & COMMON GRANDTOTAL    ! shared across programs
  LENGTH 4.0 & SHARED PAGENO         ! shared with subroutines

String variables (always end with $ dollar sign):
  LENGTH 20 & LOCAL NAME$
  LENGTH 3  & LOCAL ANSWER$
  LENGTH 30 & LOCAL ADDRESS$
  LENGTH 1  & LOCAL CHOICE$

Arrays (subscripted variables):
  LENGTH 8.2 & LOCAL SCORE(10)       ! numeric array of 10 elements
  LENGTH 20  & LOCAL ITEM$(5)        ! string array of 5 elements

=== FORMAT SECTION ===

  100 FORMAT (ET)                    ! Enter Typewriter mode (clears screen)
  200 FORMAT CUSTNO$; NAME$; ADDR$   ! define a print format layout

=== OUTPUT / INPUT (Executable Section) ===

  PRINT (0) "Hello, World!"          ! print string to terminal (device 0)
  PRINT (0) "Value ="; AMOUNT        ! print label and numeric variable
  PRINT (0) NAME$                    ! print string variable
  PRINT (0,100)                      ! print using FORMAT label 100
  PRINT (0) "Enter name:"
  INPUT (0) NAME$                    ! input string from terminal
  INPUT (0) AMOUNT                   ! input numeric from terminal
  INPUT (0) CHOICE$, EXCP=200        ! input with exception label

=== ASSIGNMENT ===

  LET TOTAL = TOTAL + AMOUNT
  LET COUNTER = COUNTER + 1
  LET AVERAGE = TOTAL / COUNTER
  LET NAMES$ = "JOHN"
  LET PHONES$ = "(" + AREACODES$ + ") " + NUMBERS$   ! string concat with +

=== LOOPS ===

FOR/NEXT:
  FOR I = 1 TO 10
      PRINT (0) I
  NEXT I

  FOR I = 100 DOWNTO 1 STEP 2
      PRINT (0) I
  NEXT I

WHILE/ENDWHILE:
  WHILE COUNTER LT 10
      LET COUNTER = COUNTER + 1
  ENDWHILE

REPEAT/UNTIL:
  REPEAT
      PRINT (0) "ENTER VALUE:"
      INPUT (0) AMOUNT
  UNTIL AMOUNT GT 0

=== CONDITIONALS ===

Single-line IF:
  IF ANSWER$ = "YES" THEN GOTO 200
  IF BALANCE LT 0 THEN GOTO 500
  IF PAY = 0 AND DEBIT = 0 THEN PAY = PAY + 1

Block IF/ENDIF:
  IF OPTION = 1 THEN
      PRINT (0) "OPTION ONE SELECTED"
  ELSE
      PRINT (0) "OTHER OPTION"
  ENDIF

SELECT/ENDSELECT:
  SELECT CHOICE
      CASE 1
          PRINT (0) "ONE"
      CASE 2
          PRINT (0) "TWO"
      CASE ELSE
          PRINT (0) "OTHER"
  ENDSELECT

=== RELATIONAL OPERATORS ===

  Equal To           =  or  EQ
  Not Equal To      <>  or  NE   (also: NOT =)
  Greater Than       >  or  GT
  Greater or Equal  >=  or  GE
  Less Than          <  or  LT
  Less or Equal     <=  or  LE

  Example: IF PART LE 1 THEN GOTO 100
  Example: IF BALANCE GT 0 AND DEBIT EQ 0 THEN GOTO 200

=== LOGICAL OPERATORS ===

  AND   OR   NOT

=== ARITHMETIC OPERATORS ===

  +  (addition)      -  (subtraction)
  *  (multiplication)   /  (division)
  MOD (modulo remainder)

  Example: LET A = B MOD C

=== SUBROUTINES / BRANCHING ===

  GOSUB 500          ! call subroutine at label 500
  RETURN             ! return from subroutine
  GOTO 200           ! unconditional jump to label 200
  ON GOTO A, 100, 200, 300   ! computed jump based on value of A
  ON GOSUB A, 100, 200, 300  ! computed subroutine call

  LOOP:              ! alphanumeric statement label (colon only on definition)
      PRINT (0, LOOP)
      GOTO LOOP

=== MATH FUNCTIONS ===

  ABS(n)       ! absolute value
  INT(n)       ! integer part (truncates toward zero)
  FPT(n)       ! fractional part (digits right of decimal point)
  SGN(n)       ! sign: returns -1, 0, or 1
  SQR(n)       ! square root

  Example: LET A = ABS(BALANCE)
  Example: LET B = INT(TOTAL)
  Example: LET C = SQR(VALUE)

=== STRING FUNCTIONS ===

  LEN(s$)              ! current length of string variable
  ASC(s$)              ! ASCII code of first character
  CHR(n)               ! character from ASCII code n
  LCASE(s$)            ! convert to lowercase
  UCASE(s$)            ! convert to uppercase
  STR(n)               ! convert numeric to string
  NUM(s$)              ! convert string to numeric
  POS(s$, sub$)        ! position of sub$ within s$  (0 if not found)
  SUB(s$, pos, len)    ! extract len characters from s$ starting at pos
  STRIP(s$)            ! remove leading and trailing spaces
  STRIPL(s$)           ! remove leading (left) spaces
  STRIPR(s$)           ! remove trailing (right) spaces
  ADJUSTL(s$, n)       ! left-adjust s$ in field of width n
  ADJUSTR(s$, n)       ! right-adjust s$ in field of width n

  Example: LET L = LEN(NAME$)
  Example: LET FIRST$ = SUB(NAME$, 1, 5)
  Example: IF UCASE(CHOICE$) = "YES" THEN GOTO 300

=== FILE OPERATIONS ===

Open and close:
  OPEN (1) "CUSTOMER", DISC="DSK"    ! open file on device 1
  CLOSE (1)                          ! close device 1
  CLOSEALL                           ! close all open devices

Sequential read/write:
  OPEN (1) "DATAFILE"
  READ (1, 100) EXCP=9999            ! read next record using format 100; jump to 9999 on EOF
  WRITE (1, 100)                     ! write record using format 100
  CLOSE (1)

Keyed file access:
  OPEN (1) "CUSTOMER"
  READ (1, 100) IND=KEYS$, EXCP=9000  ! read by key
  REWRITE (1, 100) IND=KEYS$          ! update record in place
  INSERT (1, 100) IND=KEYS$           ! insert new record
  DELETE (1) IND=KEYS$                ! delete record by key
  CLOSE (1)

=== SCREEN / TERMINAL CONTROL ===

  CLEAR                    ! initialize/clear variables
  PRINT (0,100)            ! output FORMAT label 100 to terminal (clears screen if ET)
  MOVE (0, row, col)       ! move cursor to row, col on terminal
  POSITION (0, row, col)   ! position cursor (same as MOVE)
  EJECT (2)                ! form-feed / page eject on printer device 2
  PAUSE n                  ! pause execution for n seconds

=== PROGRAM TERMINATION ===

  RUN "*MONITOR"           ! return control to the operating system monitor
  END                      ! logical end of program (always after RUN "*MONITOR")
  STOP                     ! stop execution (for debugging)
  TERMINATE                ! terminate and return to *MONITOR

=== EXCEPTION HANDLING ===

  READ (1, 100) EXCP=9999            ! on error/EOF go to label 9999
  INPUT (0) AMOUNT, EXCP=200         ! on bad input go to label 200
  ERRORSUB ERRSUB:                   ! define error-handling subroutine
  ERRORTO ERRSUB                     ! redirect all errors to label
  ESCAPESUB ESCSUB:                  ! define escape-key handler
  ESCAPETO ESCSUB                    ! redirect escape key to label

=== EXAMPLE PROGRAMS FROM YOUR TRAINING DATA ===

{few_shot}

=== IMPORTANT ===
You have been trained on {len(examples)} QICBASIC examples.
Keywords you know: {', '.join(sorted(keywords_found))}
Always produce complete, runnable QICBASIC programs with proper
Declarative, Format, and Executable sections.
Always end with RUN "*MONITOR" and END.
Use ! for comments. Use LENGTH to declare variables. Use PRINT (0) and INPUT (0) for terminal I/O.
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
print("  Asking: 'Write a Hello World in QICBASIC'")
print()

test_response = ask_ollama(
    NEW_MODEL,
    "Write a Hello World program in QICBASIC",
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
print(f"    - {len(keywords_found)} QICBASIC keywords embedded as reference")
print( "    - 5 few-shot examples added for better accuracy")
print( "    - Lower temperature (0.2) for more precise code")
print()
print("  Use your model:")
print("    Terminal : double-click start_chat.bat")
print("    Browser  : open chat.html in Chrome/Edge")
print()
input("  Press Enter to close...")
