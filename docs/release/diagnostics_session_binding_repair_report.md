# Diagnostics Session Binding Repair Report

Generated at: `2026-05-19T19:36:16Z`

**Status:** implemented at route-runtime level

- diagnostics router patched: `False`
- evidence registry patched: `False`
- adaptive next-item rejects mismatched query caps_ref against recovered session caps_ref
- adaptive respond rejects item IDs not recorded in recovered session served_item_ids
- adaptive respond rejects mismatched response caps_ref when supplied
