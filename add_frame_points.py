import sqlite3
import shutil
from pathlib import Path
import datetime as dt
import traceback

DB_PATH = Path("./SCUM.db")


def create_backup(db_path: Path) -> Path:
    ts = dt.datetime.now().isoformat().replace(":", "-")
    backup_path = db_path.with_name(f"SCUM-bak-{ts}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def list_users(cur):
    cur.execute("""
        SELECT user_id, name, fame_points
        FROM user_profile
        WHERE fame_points > 0
        ORDER BY fame_points DESC
    """)
    rows = cur.fetchall()

    print("\nПользователи с fame_points > 0:")
    print("-" * 80)
    for uid, name, fp in rows:
        nickname = name if name else "<без имени>"
        print(f"{uid} | {nickname} | {fp}")
    print("-" * 80)

    return {uid: (name, fp) for uid, name, fp in rows}


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"База не найдена: {DB_PATH.resolve()}")

    print("Создание резервной копии базы...")
    backup = create_backup(DB_PATH)
    print(f"Бэкап создан: {backup}")

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()

        users = list_users(cur)

        if not users:
            print("Нет пользователей с fame_points > 0")
            return

        user_id = input("\nВведите user_id: ").strip()

        if user_id not in users:
            print("❌ Пользователь не найден.")
            return

        name, old_fp = users[user_id]
        nickname = name if name else "<без имени>"

        try:
            add_value = float(
                input("Сколько fame_points добавить: ").replace(",", ".")
            )
        except ValueError:
            print("❌ Введено не число.")
            return

        new_fp = old_fp + add_value

        print("\nПодтверждение:")
        print(f"user_id        : {user_id}")
        print(f"Никнейм        : {nickname}")
        print(f"Было fame_pts  : {old_fp}")
        print(f"Добавляем      : {add_value}")
        print(f"Станет fame_pts: {new_fp}")

        confirm = input("\nПрименить? (y/n): ").lower()
        if confirm != "y":
            print("Отменено.")
            return

        cur.execute("""
            UPDATE user_profile
            SET fame_points = ?
            WHERE user_id = ?
        """, (new_fp, user_id))

        con.commit()

        cur.execute("""
            SELECT fame_points
            FROM user_profile
            WHERE user_id = ?
        """, (user_id,))

        print("\n✅ Успешно обновлено.")
        print(f"Новое значение fame_points: {cur.fetchone()[0]}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    except Exception:
        print("\nОшибка:\n")
        traceback.print_exc()
        input("\nНажмите Enter для выхода.")
