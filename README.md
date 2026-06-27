# Dank Butler 🤵‍♂️

A Telegram bot that acts as your personal meme concierge. Describe a meme to have him fetch it, or send a meme and he will explain its context, origin, and humor.

## How it works

```
You: "that dog in a burning room saying this is fine"
  → Dank Butler converts to search query: "this is fine dog fire meme"
  → Searches Tenor → Giphy → Google Images (fallback chain)
  → Gemini Vision verifies each candidate result matches your description
  → Sends you the exact meme (GIF/image)
```

---

## Setup (One-time)

### 1. Get a Telegram Bot Token
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the instructions to name it (e.g., `DankButlerBot`).
3. Copy the HTTP API token it provides.

### 2. Get a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click "Create API Key" and copy the key (the free tier is perfectly fine).

### 3. Get a Tenor API Key (Free)
1. Go to the [Google Cloud Console / Tenor API Quickstart](https://developers.google.com/tenor/guides/quickstart).
2. Set up a project and copy your API key.

### 4. Get Giphy & SerpAPI Keys (Optional)
*   **Giphy API Key**: Obtain a free developer key at [Giphy Developers](https://developers.giphy.com).
*   **SerpAPI Key**: Obtain a key at [SerpAPI](https://serpapi.com) for Google Images fallback (100 free searches/month).

---

## Project Structure
```
dank-buttler/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── main.py (Root entry point)
└── src/
    └── dank_butler/
        ├── __init__.py
        ├── bot.py
        ├── config.py
        └── meme_engine.py
```

---

## Installation

1. Clone or download this project.
2. Navigate to the repository:
   ```bash
   cd dank-buttler
   ```
3. Create a virtual environment:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up your environment variables:
   *   Copy `env.example` to `.env` (or rename it).
   *   Open `.env` and fill in your keys.

---

## Running

Start the bot by running the entry point:
```bash
python main.py
```

Open Telegram, find your bot, click **Start** or send `/start`, and begin interacting!

---

## Usage

| What you do | What Dank Butler does |
|---|---|
| Send text: *"distracted boyfriend meme"* | Finds, verifies, and sends the meme GIF/image |
| Send text: *"two spidermans pointing at each other"* | Converts description to query, searches, verifies, sends |
| Send a meme image/photo | Explains its name, origin, meaning, and why it's funny |
