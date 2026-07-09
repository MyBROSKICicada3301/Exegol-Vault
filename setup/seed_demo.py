import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import security
from db import Database

DEMO_MASTER = "UseTheForce!"

SAMPLE_ENTRIES = [
    ("Death Star Plans", "galen.erso", "St4rdust-Sc4rif!", "https://imperial-archives.example", "Stolen by Rogue One. Exhaust port: thermal, two meters wide."),
    ("Millennium Falcon Nav Computer", "han.solo", "KesselRun<12parsecs", "https://falcon.example", "Never tell me the odds."),
    ("Jedi Temple Archives", "master.yoda", "DoOrDoNot_900yrs", "https://jedi-temple.example", "Judge me by my size, do you?"),
    ("Mos Eisley Cantina Wi-Fi", "obiwan", "TheseArentTheDroids#77", "", "A more wretched hive of scum and villainy you will never find."),
    ("Imperial Payroll Portal", "d.vader", "IFindYourLackOfF@ith", "https://payroll.empire.example", "Apology accepted, Captain Needa."),
    ("Rebel Alliance Comms", "leia.organa", "HelpMeObiWan_1977", "https://rebellion.example", "You're my only hope."),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv
    if args:
        os.environ["DB_NAME"] = args[0]

    db = Database()
    db.connect()

    if db.get_master() is not None and not force:
        print("This vault already has a master password. Re-run with --force to")
        print("REPLACE it with the demo master (existing entries become undecryptable).")
        sys.exit(1)

    salt = security.new_kdf_salt()
    db.set_master(security.hash_master_password(DEMO_MASTER), salt)
    cipher = security.VaultCipher(DEMO_MASTER, salt)

    for title, username, password, url, notes in SAMPLE_ENTRIES:
        db.add_holocron(title, username, cipher.encrypt(password), url, notes)

    count = len(db.list_holocrons())
    db.close()
    print(f"Seeded {count} holocrons into '{os.getenv('DB_NAME', 'Exegol-Vault')}'.")
    print(f"Demo master password: {DEMO_MASTER}")


if __name__ == "__main__":
    main()
