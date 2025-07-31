# Soul Link Tracker

This repository contains utilities for reading Pokémon party data from
DeSmuME and sharing it with a partner.

* `team_export.lua` – Lua script that exports the player's party information
  from a running game every two seconds. When started, the script asks which
  game you are playing (Diamond/Pearl, HeartGold/SoulSilver, Black/White, or
  Black2/White2) and uses the appropriate memory offsets. The data is written to
  `team_data.json`.

* `soul_link.py` – Python script that reads `team_data.json`, connects to a
  WebSocket server, and exchanges team information with your partner. It prints
  both teams to the terminal, applies the soul link fainting rule, and logs
  updates to `soul_link_log.json`.

Run `team_export.lua` through DeSmuME's Lua scripting interface and execute
`soul_link.py` while playing to sync your party with your partner.
