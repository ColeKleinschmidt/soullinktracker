#!/usr/bin/env python3
"""GUI utility to select a ROM and launch DeSmuME with nicer visuals."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


def available_roms(rom_dir: str) -> dict[str, str]:
    """Return mapping of display names to ROM file paths."""
    try:
        files = [
            f
            for f in os.listdir(rom_dir)
            if os.path.isfile(os.path.join(rom_dir, f))
        ]
    except OSError:
        return {}

    roms: dict[str, str] = {}
    for file in files:
        name, _ = os.path.splitext(file)
        display = name.replace("_", " ")
        roms[display] = os.path.join(rom_dir, file)
    return roms


def launch_tracker() -> None:
    """Write selection to config.txt and launch DeSmuME with ROM."""
    game = game_var.get()
    rom_path = ROMS.get(game)
    if not rom_path:
        messagebox.showerror("Error", "Selected ROM not found.")
        return

    config_path = os.path.join(BASE_DIR, "config.txt")
    try:
        with open(config_path, "w", encoding="utf-8") as cfg:
            cfg.write(game)
    except OSError as exc:  # pragma: no cover - best effort
        messagebox.showerror("Error", f"Failed to write config.txt: {exc}")
        return

    desmume = os.path.normpath(os.path.join(ROOT_DIR, "desmume.exe"))
    lua_script = os.path.normpath(os.path.join("SoulLinkTracker", "team_export.lua"))
    rom_path = os.path.normpath(os.path.relpath(rom_path, ROOT_DIR))

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        subprocess.Popen(
            [desmume, f"--lua={lua_script}", rom_path],
            cwd=ROOT_DIR,
            creationflags=creationflags,
        )
    except OSError as exc:
        messagebox.showerror("Error", f"Failed to launch DeSmuME: {exc}")
        return
    root.destroy()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    ROM_DIR = os.path.join(ROOT_DIR, "Roms")
    ROMS = available_roms(ROM_DIR)

    if os.name == "nt":  # best effort to hide console window
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except Exception:  # pragma: no cover - shouldn't fail hard
            pass

    root = tk.Tk()
    root.title("Pokémon Game Selector")
    root.resizable(False, False)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:  # pragma: no cover
        pass
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 10))

    frame = ttk.Frame(root, padding=20)
    frame.pack()

    ttk.Label(frame, text="Select a Pokémon ROM:").grid(row=0, column=0, pady=(0, 10))

    game_var = tk.StringVar()
    game_combo = ttk.Combobox(
        frame, textvariable=game_var, values=sorted(ROMS.keys()), state="readonly"
    )
    game_combo.grid(row=1, column=0, pady=(0, 10))
    if ROMS:
        game_var.set(sorted(ROMS.keys())[0])

    ttk.Button(frame, text="Launch Tracker", command=launch_tracker).grid(
        row=2, column=0, pady=(0, 10)
    )

    root.mainloop()
