# Independent content review register

The content generation and seeding tools must not create or modify this register. It is read-only input to the item-bank seeder and must be maintained outside the generation pipeline by the project owner after external educator review.

Approved item or lesson records must match an entry by exact item_id (or lesson_id for lessons) and reviewer_id. Each entry requires decision=approved and independent=true. Independence means the reviewer authored neither the item template nor generated output and is currently teaching Grade 4 or intermediate-phase mathematics. The register is intentionally absent until an eligible external educator has completed review; without it, the seeder refuses approved rows.

Expected JSON shape:

    {
      "entries": [
        {
          "item_id": "item UUID (or lesson_id for a lesson)",
          "reviewer_id": "reviewer UUID",
          "decision": "approved",
          "independent": true,
          "reviewed_at": "ISO-8601 timestamp",
          "review_scope": "CAPS objective reference and item version"
        }
      ]
    }

Store the register as a protected review artifact. Do not place synthetic reviewer identities, self-review, or unreviewed records in it. Approval is version-specific: changing an item invalidates its prior entry and requires a new review.
