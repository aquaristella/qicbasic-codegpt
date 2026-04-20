=======================================================
  QiBasic CodeGPT - Windows
  Your Local AI Assistant for QBasic Programming
=======================================================

QUICK START (3 steps)
─────────────────────
1. Make sure Ollama is installed
   Download: https://ollama.com/download

2. Double-click:  setup.bat
   (Wait for it to finish — about 2-5 minutes)

3. Then choose how to use it:
   - Double-click  start_chat.bat   (terminal chat)
   - Open          chat.html        (browser chat UI)


FILES IN THIS FOLDER
─────────────────────
  setup.bat              ← RUN THIS FIRST
  start_chat.bat         ← Opens terminal chat
  chat.html              ← Opens web chat UI in browser
  Modelfile              ← QiBasic AI settings
  qibasic_training.jsonl ← Training examples (add more!)
  finetune_qibasic.py    ← Optional: GPU fine-tuning
  README.txt             ← This file


EXAMPLE QUESTIONS TO ASK
──────────────────────────
  "Write a Hello World program"
  "Write a FOR loop from 1 to 100"
  "Explain what DIM means"
  "Fix this code: FOR i 1 TO 10 PRINT i"
  "Write a function to check if a number is prime"
  "Show me how to read a file in QBasic"
  "Write a bubble sort"
  "What string functions are available?"


TROUBLESHOOTING
────────────────
Problem: "Ollama not found"
Fix: Install Ollama from https://ollama.com/download
     Restart your computer, then run setup.bat again

Problem: Chat says "Cannot connect to Ollama"
Fix: Open Command Prompt and run:
       ollama serve
     Then refresh chat.html or re-open start_chat.bat

Problem: Model gives Python/C++ code
Fix: Add to your question: "Only use QBasic code."

Problem: setup.bat closes immediately
Fix: Right-click setup.bat → "Run as Administrator"


ADD YOUR OWN QBASIC EXAMPLES
──────────────────────────────
Open qibasic_training.jsonl in Notepad and add lines like:
  {"instruction": "Your question", "input": "", "output": "QBasic code"}

The more examples, the smarter it gets!


OPTIONAL: GPU FINE-TUNING (Better Results)
────────────────────────────────────────────
If you have an NVIDIA GPU (8GB+ VRAM):
  1. pip install unsloth torch transformers datasets trl
  2. python finetune_qibasic.py
  3. Edit Modelfile line 1 to:
       FROM ./qibasic_gguf/unsloth.Q4_K_M.gguf
  4. Run setup.bat again

=======================================================
