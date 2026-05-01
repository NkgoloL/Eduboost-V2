import sys
import re

# Redmine User ID for NkgoloL
USER_ID = 5

# Issue ID Mapping
ISSUE_MAP = {
    "gamification": 1, "badge": 1, "xp": 1, "streak": 1, "reward": 1,
    "parent": 2, "guardian": 2, "consent": 2, "family": 2, "verification": 2,
    "diagnostic": 3, "irt": 3, "assessment": 3, "item": 3, "test": 3,
    "study plan": 4, "plan": 4, "refresh": 4, "rationale": 4,
    "fourth estate": 5, "estate": 5, "audit_events": 5, "audit_events": 10,
    "judiciary": 6, "compliance": 6, "policy": 6, "constitutional": 8,
    "profiler": 7, "archetype": 7, "profile": 7,
    "schema": 8, "orm": 8, "migration": 8, "table": 8, "db": 8,
    "orchestrator": 9, "operation": 9, "request": 9,
    "audit": 10, "log": 10, "event": 10,
    "lesson": 11, "catalog": 11, "content": 11,
    "learner": 12, "onboarding": 12, "nickname": 12,
}

def get_issue_id(message):
    message = message.lower()
    for kw, issue_id in ISSUE_MAP.items():
        if kw in message:
            return issue_id
    # Default to a general "Architecture" or "Other" issue if possible, 
    # but here we'll just return None or a catch-all if we had one.
    return None

def main():
    log_input = sys.stdin.read()
    lines = log_input.strip().split("\n")
    
    print("USE redmine;")
    
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
            
        hash_id, author, date_str, message = parts[0], parts[1], parts[2], "|".join(parts[3:])
        
        issue_id = get_issue_id(message)
        if not issue_id:
            # If no specific mapping, maybe it's general architecture/docs
            if "docs" in message.lower() or "readme" in message.lower():
                issue_id = 9 # Use Orchestrator/Architecture as catch-all
            else:
                continue
                
        notes = f"Commit {hash_id} by {author} on {date_str}: {message}"
        notes_escaped = notes.replace("'", "''").replace("\\", "\\\\")
        
        # We'll use a subquery check to avoid duplicates in case we run this multiple times
        sql = f"INSERT INTO journals (journalized_id, journalized_type, user_id, notes, created_on) " \
              f"SELECT {issue_id}, 'Issue', {USER_ID}, '{notes_escaped}', '{date_str} 12:00:00' " \
              f"WHERE NOT EXISTS (SELECT 1 FROM journals WHERE notes LIKE 'Commit {hash_id}%');"
        print(sql)

if __name__ == "__main__":
    main()
