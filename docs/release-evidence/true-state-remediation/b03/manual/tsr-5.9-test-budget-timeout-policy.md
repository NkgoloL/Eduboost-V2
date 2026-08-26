# TSR-5.9 Test Budget and Timeout Policy

## Policy Definition
1. **Per-Test Budget**:
   - `product_unit`: Maximum 0.5 seconds per test.
   - `product_integration`: Maximum 5.0 seconds per test.
   - `runtime_stack`: Maximum 15.0 seconds per test.
2. **Suite-Level Budget**:
   - Fast PR Core test suite budget: Maximum 3 minutes total execution.
   - Integration test suite budget: Maximum 10 minutes total execution.
3. **Fail-Closed Timeout**: Any test exceeding budget must be flagged as slow and refactored into an asynchronous or background integration test.
