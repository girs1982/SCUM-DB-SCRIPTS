import shutil
import sqlite3
from pathlib import Path
import datetime as dt
import traceback

DB_PATH = Path("./SCUM.db")


def add_elevated_user(steam_id: str):
    """
    Adds a SteamID64 to the elevated_users list.
    """

    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()

        cursor.execute(
            """
            INSERT INTO elevated_users (user_id)
            VALUES (?)
            """,
            (steam_id,),
        )

        con.commit()
        print(f"SteamID64 {steam_id} successfully added to elevated_users.")


def create_backup(db_path: Path) -> Path:
    """Creates a backup of the database."""
    filename_safe_iso = dt.datetime.now().isoformat().replace(":", "-")
    backup_path = db_path.with_name(f"SCUM-bak-{filename_safe_iso}.db")
    shutil.copy(db_path, backup_path)
    return backup_path


def main():
    print("Creating backup...")

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH.resolve()}")

    backup_path = create_backup(DB_PATH)
    print(f"Backed up to: {backup_path}")

    steam_id = input("Enter the SteamID64 to elevate: ").strip()

    if len(steam_id) == 17 and steam_id.isdigit():
        add_elevated_user(steam_id)
    else:
        print("Invalid SteamID64. Please ensure it is a 17-digit numeric ID.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception:
        print("\n\nSomething went wrong...\n\n")
        traceback.print_exc()
        input("\n\nPress enter to exit.")
