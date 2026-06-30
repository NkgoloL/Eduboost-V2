#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
script_path = ROOT / 'scripts' / 'ensure_irt_seed.py'
# Load module from file
spec = importlib.util.spec_from_file_location('ensure_irt_seed', script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Use its _generate_items
rows = mod._generate_items(target=int(sys.argv[1]) if len(sys.argv) > 1 else 1600)

OUT = ROOT / 'scripts' / 'irt_seed_1600.sql'

def escape_sql(s: str) -> str:
    return s.replace("'", "''")

with OUT.open('w', encoding='utf-8') as f:
    f.write('BEGIN;\n')
    for r in rows:
        options = r['options']
        options_sql = "'" + escape_sql(options) + "'::jsonb"
        q = (
            "INSERT INTO irt_items (id, grade, subject, topic, language, question_text, options, correct_option, a_param, b_param, created_at) VALUES ("
            f"'{escape_sql(r['id'])}', {r['grade']}, '{escape_sql(r['subject'])}', '{escape_sql(r['topic'])}', '{escape_sql(r['language'])}', '")
        q += escape_sql(r['question_text']) + "', " + options_sql + ", '" + r['correct_option'] + "', " + str(r['a_param']) + ", " + str(r['b_param']) + ", now());\n"
        f.write(q)
    f.write('COMMIT;\n')
print(f'Wrote {len(rows)} INSERTs to {OUT}')
