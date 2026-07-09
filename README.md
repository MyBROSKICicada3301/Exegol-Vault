<div align="center">
  <img src="assets/logo.png" alt="Exegol Vault" width="320">

---

Your passwords are stored as **holocrons** in a PostgreSQL database. The master
password is bcrypt-hashed, and every stored password is encrypted with a key
derived from it, so nothing readable ever touches the database.

## Features

- 🔐 Master password unlock: bcrypt-hashed, unrecoverable by design
- 🗝️ Add, edit, reveal, search, and delete holocrons
- 🎲 "Astromech" strong password generator
- 📋 Copy to clipboard with 20-second self-destruct
- 💀 "Execute Order 66" delete confirmation
- 🔴🟡 Dark side / light side theme toggle

## Translating the Star Wars speak

| In the app | What it actually means |
| --- | --- |
| Holocron | A saved password entry (title, username, password, URL, notes) |
| Master code | Your master password, the only one you must remember |
| Forge Master Code | Create your master password (first launch) |
| Unseal the Archives | Log in |
| Seal Archives 🔒 | Lock the vault / log out |
| Forge Holocron | Add a new entry |
| Modify Holocron | Edit an entry |
| Save to Archives | Save |
| Abort | Cancel |
| 🎲 Astromech | Generate a strong random password |
| 👁 | Reveal a stored password |
| 📋 | Copy password to clipboard (auto-wiped after 20 seconds) |
| ✏️ | Edit the entry |
| 💀 / Execute Order 66 | Delete the entry (Execute = confirm, Spare it = cancel) |
| Search the archives | Filter entries by title, username, or URL |
| Embrace the Dark Side / Return to the Light | Switch between red and yellow themes |
| Hyperspace Link Failed | Could not connect to the PostgreSQL database |

## Security model

| Secret          | Protection                                                                              |
| --------------- | --------------------------------------------------------------------------------------- |
| Master password | bcrypt hash (never stored in plain, cannot be recovered)                                |
| Entry passwords | Fernet (AES-128-CBC + HMAC), key from PBKDF2-HMAC-SHA256 (600k iterations, random salt) |
| DB credentials  | `.env` file, gitignored                                                               |

Entry passwords are encrypted rather than hashed because a password manager must be
able to show them back to you, and hashing is one-way. The master password *is* hashed.
Unlocking with the wrong master password is rejected by bcrypt, and even a tampered
database cannot decrypt entries without the correct master password.

## Setup

1. Install [PostgreSQL](https://www.postgresql.org/download/) and make sure it's running.
2. Create the app role and database: open [setup/setup_database.sql](setup/setup_database.sql),
   change the password, and run it as superuser (pgAdmin Query Tool or
   `psql -U postgres -f setup/setup_database.sql`).
3. Copy `.env.example` to `.env` and fill in the same password.
4. Install dependencies:

   ```powershell
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
5. Run:

   ```powershell
   .venv\Scripts\python main.py
   ```

First launch asks you to forge a master code (min 8 chars). Tables are created
automatically. **The master code cannot be recovered. Losing it means losing the vault.**

## Try it with demo data

Want to explore before trusting it with real secrets? Seed a demo vault:

```powershell
# create the demo database first (as superuser):
#   CREATE DATABASE "Exegol-Vault-Demo" OWNER "Exegol-Vault";
.venv\Scripts\python setup\seed_demo.py Exegol-Vault-Demo
```

Then set `DB_NAME=Exegol-Vault-Demo` in `.env` and log in with master password
`UseTheForce!`. Six sample holocrons included (Death Star plans, Falcon nav
computer, cantina Wi-Fi…). Switch `DB_NAME` back to `Exegol-Vault` for your real vault.

## Building the desktop app (.exe)

```powershell
.venv\Scripts\python -m pip install pyinstaller pillow
.venv\Scripts\pyinstaller --noconfirm --clean --windowed --name ExegolVault --icon assets\icon.ico --add-data "assets;assets" --collect-all customtkinter main.py
Copy-Item .env dist\ExegolVault\.env
```

Result: `dist\ExegolVault\ExegolVault.exe`, standalone, no Python needed to run.
The `.env` must sit next to the exe. Pin it, make a shortcut, live your Sith life.

## Project structure

```
main.py          app entry point & screen controller
security.py      bcrypt, PBKDF2 key derivation, Fernet, password generator
db.py            PostgreSQL layer (schema auto-created on first run)
paths.py         source vs. packaged-exe path resolution
ui/theme.py      dark side / light side palettes
ui/screens.py    setup, login, and vault screens
ui/dialogs.py    holocron editor + Order 66 confirmation
setup/           database bootstrap SQL + demo data seeder
assets/          logo and app icon
```

## Running from VS Code

Open the folder, select the `.venv` interpreter (`Ctrl+Shift+P` → *Python: Select
Interpreter*), then `F5` or run `main.py`.

## Disclaimer

Hobby project, not a security audit target. The crypto primitives are standard
(bcrypt, PBKDF2, Fernet), but for credentials that guard anything important,
use an established password manager. 

May the Force be with you☮️
