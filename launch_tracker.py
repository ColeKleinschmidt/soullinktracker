#!/usr/bin/env python3
"""Simple GUI to select a Pokémon game and launch DeSmuME."""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

GAMES = [
    "Black/White",
    "Black2/White2",
    "Diamond/Pearl",
    "HeartGold/SoulSilver",
]


def launch_tracker() -> None:
    """Write game selection to config.txt and launch DeSmuME."""
    game = game_var.get()
    config_path = os.path.join(BASE_DIR, "config.txt")
    try:
        with open(config_path, "w", encoding="utf-8") as cfg:
            cfg.write(game)
    except OSError as exc:  # pragma: no cover - best effort
        messagebox.showerror("Error", f"Failed to write config.txt: {exc}")
        return

    desmume = os.path.join(BASE_DIR, "desmume.exe")
    lua_script = os.path.join(BASE_DIR, "team_export.lua")

    try:
        subprocess.Popen([desmume, f"--lua={lua_script}"], cwd=BASE_DIR)
    except OSError as exc:
        messagebox.showerror("Error", f"Failed to launch DeSmuME: {exc}")
        return
    root.destroy()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    root = tk.Tk()
    root.title("Pokémon Game Selector")

    ttk.Label(root, text="Select a Pokémon game:").pack(padx=10, pady=10)

    game_var = tk.StringVar(value=GAMES[0])
    ttk.Combobox(
        root, textvariable=game_var, values=GAMES, state="readonly"
    ).pack(padx=10, pady=10)

    ttk.Button(root, text="Launch Tracker", command=launch_tracker).pack(
        padx=10, pady=10
    )

    root.mainloop()
