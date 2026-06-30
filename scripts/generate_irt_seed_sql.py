#!/usr/bin/env python3
import os
from pathlib import Path
from scripts.ensure_irt_seed import _generate_items

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts/irt_seed_1600.sql"


def escape_sql(s: str) -> str:
    return s.replace("'", "''")


def main():
    target = int(os.environ.get('SEED_TARGET', '1600'))
    rows = _generate_items(target=target)
    with OUT.open('w', encoding='utf-8') as f:
        f.write("BEGIN;\n")
        for r in rows:
            options = r['options']
            # ensure JSON is properly escaped
            options_sql = "'" + escape_sql(options) + "'::jsonb"
            q = (
                "INSERT INTO irt_items (id, grade, subject, topic, language, question_text, options, correct_option, a_param, b_param, created_at) VALUES ("
                f"'{escape_sql(r['id'])}', {r['grade']}, '{escape_sql(r['subject'])}', '{escape_sql(r['topic'])}', '{escape_sql(r['language'])}', '")
            q += escape_sql(r['question_text']) + "', " + options_sql + ", '" + r['correct_option'] + "', " + str(r['a_param']) + ", " + str(r['b_param']) + ", now());\n"
            f.write(q)
        f.write("COMMIT;\n")
    print(f"Wrote {len(rows)} INSERTs to {OUT}")


if __name__ == '__main__':
    main()
