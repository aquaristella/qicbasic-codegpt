Here is your **Windows version** — ready to run immediately! Follow these exact steps:

---

**Step 1 — Extract the zip**
Right-click the downloaded zip → **Extract All** → choose a folder (e.g. `C:\qibasic-codegpt`)

**Step 2 — Double-click `setup.bat`**
It will automatically:
- Check Ollama is installed
- Download DeepSeek-Coder (~776MB, takes a few minutes)
- Create your `qibasic-codegpt` model
- Run a quick test to confirm it works

**Step 3 — Start using it**
- Double-click **`start_chat.bat`** → terminal chat opens immediately
- Or open **`chat.html`** in Chrome/Edge → full web UI with 12 quick-prompt buttons

---

**What's inside the zip:**

| File | What it does |
|---|---|
| `setup.bat` | Double-click this first — sets everything up |
| `start_chat.bat` | Opens terminal chat anytime |
| `chat.html` | Web chat UI — open in browser |
| `Modelfile` | QiBasic AI rules and personality |
| `qibasic_training.jsonl` | 30 QiBasic examples (add your own!) |
| `README.txt` | Instructions + troubleshooting |
| `finetune_qibasic.py` | Optional GPU fine-tuning for better results |

> **If Ollama is not installed yet:** Go to [ollama.com/download](https://ollama.com/download), install for Windows, then double-click `setup.bat`.
Let me give you a very detailed, easy-to-understand explanation with visuals.Now let me build the full detailed interactive explainer:Here is a complete interactive explanation of your `qibasic-codegpt` model across 6 tabs — click each tab to explore:

**What is it?** — Shows the three ingredients (Ollama, DeepSeek-Coder, Modelfile) and what role each plays. Think of Ollama as the office, DeepSeek-Coder as the programmer's brain, and your Modelfile as the job description.

**Inside the model** — Shows the 3 layers stacked on top of each other. Click each layer to expand and read exactly what it does. Also shows the flow of what happens every time you type a question.

**The Modelfile** — Breaks down every section of your `Modelfile` line by line — the `FROM` line, the `SYSTEM` block (your QBasic rules and syntax reference), and the `PARAMETER` settings like temperature.

**How it was built** — A step-by-step walkthrough of exactly what `setup.bat` did behind the scenes — from pulling DeepSeek-Coder to creating the model manifest.

**Project files** — Every file in your project explained. Click any file card to ask a follow-up question about it.

**FAQ** — Answers to the most common questions: why it might answer in Python, how to add your own unique QiBasic keywords, how to update or delete the model, and the difference between Modelfile customization vs fine-tuning.

The most important thing to understand: **the `Modelfile` is your custom model**. It wraps DeepSeek-Coder with a full QBasic identity. Every time you ask a question, your QBasic rules are invisibly prepended — the AI always "remembers" it is a QBasic expert.

The error is clear — **Unsloth requires a GPU** and your PC has none detected. Let me give you the fix: a CPU-only fine-tuning script that works without any GPU.Here is exactly what the error meant and how to fix it — 3 options from easiest to best:

---

## The problem

`Unsloth` only works with an **NVIDIA GPU**. Your PC has no GPU (or it can't be detected), so Unsloth crashes immediately. The fix is to **replace Unsloth with standard packages** that run on CPU.

---

## Option 1 — CPU training (updated zip above)

Run these commands in your `gpt_env` virtual environment:

```
# Step 1: Remove Unsloth
pip uninstall unsloth unsloth_zoo -y

# Step 2: Install CPU packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers peft datasets accelerate
```

Or just **double-click `install_requirements.bat`** from the new zip — it does all of that automatically. Then run `python finetune_qibasic.py` again.

**Downside:** CPU training is slow — 30 minutes to 3 hours depending on your PC.

---

## Option 2 — Skip fine-tuning entirely (recommended for now)

Your `qibasic-codegpt` model **already works perfectly** using just the `Modelfile`. Fine-tuning is optional — it only makes the model slightly better. You can:

```
ollama run qibasic-codegpt
```

and start using it right now. Add fine-tuning later if you want.

---

## Option 3 — Free GPU on Google Colab (best quality, fastest)

The new zip includes `colab_finetune.ipynb`. Upload it to [colab.research.google.com](https://colab.research.google.com), select a free T4 GPU, and run all cells. Training takes about 10 minutes instead of hours, and you download the `.gguf` file at the end to use with Ollama on your PC.