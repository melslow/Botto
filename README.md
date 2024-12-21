# botto

A basic Discord bot project in Python using **discord.py** and **cogs** for modular development.

## Setup

1. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure** your bot token in the `.env` file.
3. **Run** the bot:
   ```bash
   python bot.py
   ```

## Project Structure

```
botto/
├── bot.py
├── cogs
│   ├── __init__.py
│   └── sample_cog.py
├── utils
│   └── helpers.py
├── .env
├── requirements.txt
└── README.md
```

- **bot.py**: Main entry point of your bot.
- **cogs**: Folder for all your cog modules.
- **utils**: Folder for helper/utility modules.
- **.env**: Where you store your secret token.
- **requirements.txt**: Python dependencies.

## Adding More Cogs

1. Create a new file in `cogs` (e.g., `music_cog.py`).
2. Add the file name (without `.py`) to the `COGS` list in `bot.py`.
3. Write your commands or event listeners in the new cog.

**Happy coding!**
