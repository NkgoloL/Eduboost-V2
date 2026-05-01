import re

# Redmine Issue ID Mapping
SECTION_MAP = {
    "Architecture": 9,
    "Backend Quality": 11,
    "Frontend Quality": 12,
    "Privacy and Security": 8,
    "Infra and DevOps": 13,
    "Test Coverage and Quality Assurance": 14,
    "Data and AI Governance": 9,
    "Product and Accessibility Readiness": 12,
    "Documentation and Team Enablement": 9,
}

def main():
    with open("/home/nkgolol/Dev/SandBox/edo-boost-main/edo-boost-main/Production_Roadmap_Issue_Tracker.md", "r") as f:
        content = f.read()

    # Split by ## <Section>
    sections = re.split(r"## (\d+\. )?(.*?)\n", content)
    
    print("USE redmine;")
    
    # sections list looks like [preamble, "1. ", "Architecture", body, "2. ", "Backend Quality", body, ...]
    for i in range(2, len(sections), 3):
        title = sections[i].strip()
        body = sections[i+1].strip() if i+1 < len(sections) else ""
        
        issue_id = SECTION_MAP.get(title)
        if not issue_id:
            continue
            
        # Append to existing description or replace?
        # We'll replace with the full roadmap section for clarity.
        description = f"### Roadmap Section: {title}\n\n{body}"
        description_escaped = description.replace("'", "''").replace("\\", "\\\\")
        
        sql = f"UPDATE issues SET description = '{description_escaped}', updated_on = NOW() WHERE id = {issue_id};"
        print(sql)

if __name__ == "__main__":
    main()
