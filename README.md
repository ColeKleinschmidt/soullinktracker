# Soul Link Tracker

This repository contains utilities for reading Pokémon party data from DeSmuME and sharing it with a partner.

* `team_export.lua` – Lua script that exports the player's party information from a running game every two seconds. When started, the script asks which game you are playing (Diamond/Pearl, HeartGold/SoulSilver, Black/White, or Black2/White2) and uses the appropriate memory offsets. The data is written to `team_data.json`.
* `soul_link.py` – Python script that reads `team_data.json`, connects to a WebSocket server, and exchanges team information with your partner. It now opens a small window where you enter a five digit connection code and choose your game from a drop-down list including every DS title (Diamond, Pearl, Platinum, HeartGold, SoulSilver, Black, White, Black 2 and White 2). After starting, the console displays both teams, applies the soul link fainting rule, and logs updates to `soul_link_log.json`.

Run `team_export.lua` through DeSmuME's Lua scripting interface and execute `soul_link.py` while playing to sync your party with your partner.

## Building a Windows executable

To distribute the tracker as a standalone `.exe`, install [PyInstaller] (`pip install pyinstaller`) and run:

```bash
pyinstaller --onefile soul_link.py
```

The generated executable will be placed in the `dist/` folder as `soul_link.exe`. Players should still load `team_export.lua` in DeSmuME to select the game and export party data.
