import json

from paths import app_dir

PREFS_PATH = str(app_dir() / "prefs.json")

DARK_SIDE = {
    "name": "dark_side",
    "accent": "#e3242b",
    "accent_hover": "#ff4d54",
    "accent_dim": "#7a1518",
    "bg": "#0b0b10",
    "panel": "#15151d",
    "panel_hover": "#1e1e29",
    "text": "#e8e6e3",
    "text_dim": "#8a8894",
    "on_accent": "#ffffff",
    "danger": "#e3242b",
    "toggle_label": "Return to the Light",
    "tagline": "Peace is a lie. There is only passion.",
}

LIGHT_SIDE = {
    "name": "light_side",
    "accent": "#FFE81F",
    "accent_hover": "#fff36b",
    "accent_dim": "#8a7d11",
    "bg": "#0b0b10",
    "panel": "#15151d",
    "panel_hover": "#1e1e29",
    "text": "#e8e6e3",
    "text_dim": "#8a8894",
    "on_accent": "#0b0b10",
    "danger": "#e3242b",
    "toggle_label": "Embrace the Dark Side",
    "tagline": "The Force will be with you. Always.",
}

TITLE_FONT = ("Segoe UI", 30, "bold")
SUBTITLE_FONT = ("Segoe UI", 13)
BODY_FONT = ("Segoe UI", 13)
BODY_BOLD = ("Segoe UI", 13, "bold")
MONO_FONT = ("Consolas", 13)


def load_theme():
    try:
        with open(PREFS_PATH, encoding="utf-8") as fh:
            if json.load(fh).get("theme") == "light_side":
                return LIGHT_SIDE
    except (OSError, ValueError):
        pass
    return DARK_SIDE


def save_theme(theme):
    try:
        with open(PREFS_PATH, "w", encoding="utf-8") as fh:
            json.dump({"theme": theme["name"]}, fh)
    except OSError:
        pass


def other_side(theme):
    return LIGHT_SIDE if theme["name"] == "dark_side" else DARK_SIDE
