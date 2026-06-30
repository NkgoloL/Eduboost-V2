# Codemap Creation Skill

This skill provides comprehensive guidance for creating codemaps that document system architecture and implementation. Codemaps are detailed technical documents that trace execution flows, component relationships, and implementation details.

## Overview

Codemaps serve as:
- Architecture documentation for complex systems
- Onboarding resources for developers
- Reference material for implementation details
- Knowledge base for AI agents
- Change tracking for architectural decisions

## Codemap Structure

Every codemap MUST follow the standardized structure outlined in `docs/codemaps/README.md`.

**CRITICAL: Adaptiveness applies to EVERY aspect of the document.** All sections (Motivation, Details subsections, AI Guide subsections, etc.) must be adaptive to the actual system being documented. Do not use static templates or generic subsections - choose subsection names and content that match the actual behavior, components, and concerns of the specific trace.

### File Format

- **Extension:** `.md` (Markdown)
- **Naming:** `snake_case_with_underscores.md`
- **Location:** `docs/codemaps/`

### Document Components

#### 1. Title and Overview

```markdown
# [System Name]

[Brief description covering key components, entry points, and system purpose]
```

**Requirements:**
- Title should be descriptive and specific
- Overview should be 1-2 paragraphs
- Mention notable entry points with reference IDs (e.g., "login at [1b]")
- Keep it concise but informative

#### 2. Trace Sections

Each codemap contains one or more traces. A trace represents a specific execution flow or system aspect.

##### Trace Header

```markdown
## Trace ID: [number]
**Title:** [Descriptive title]

**Description:** [Concise description of what this trace covers]
```

**Requirements:**
- Trace IDs should be sequential starting from 1
- Titles should be descriptive and action-oriented (e.g., "Login Flow: Credentials to Token Pair")
- Descriptions should be 1-2 sentences explaining the trace's scope

##### Motivation Section

```markdown
**Motivation:**
[Paragraph explaining the purpose and rationale for this system/component]
```

**Requirements:**
- Explain WHY this system/component exists
- What problem does it solve?
- What trade-offs were made?
- What alternatives were considered?
- Should be 1-2 paragraphs

##### Details Section

```markdown
**Details:**
- **Execution Flow:** [Step-by-step flow using → arrows]
- **Concurrency Safety:** [Thread safety, locks, race conditions]
- **Covered Objects:** [Objects, files, components covered]
- **Timeouts:** [Timing information for operations]
- **Migration Path:** [Steps to migrate from old to new system]
- **Error Handling:** [How errors are handled]
- **Security Considerations:** [Security-related considerations]
```

**Requirements:**
- **Execution Flow:** Use → arrows to show sequence. Be specific about function calls and data flow.
- **Concurrency Safety:** Explain thread safety, locks needed, race conditions, distributed locks.
- **Covered Objects:** List all objects, files, components, database tables, API endpoints covered.
- **Timeouts:** Provide actual timing estimates (e.g., "~100-300ms", "<5ms"). Be realistic.
- **Migration Path:** Numbered steps (1, 2, 3...) for migrating from old to new system.
- **Error Handling:** Explain how errors are handled, what fails closed vs open, logging strategy.
- **Security Considerations:** Cover credentials, secrets, access controls, data exposure risks.

##### Trace Text Diagram

```markdown
**Trace text diagram:**
```
[ASCII diagram showing the flow]
```
```

**Requirements:**
- Use ASCII art to visualize the flow
- Include file paths and line numbers as references
- Use indentation to show hierarchy
- Keep it readable and well-formatted
- Reference Location IDs (e.g., <-- 1a)

##### Location IDs

```markdown
**Location ID: [letter][number]**
- **Title:** [Descriptive title]
- **Description:** [What this location represents]
- **Path:LineNumber:** [/absolute/path/to/file:line_number]
```

**Requirements:**
- Use letter-number format (1a, 1b, 2a, etc.)
- Letter corresponds to trace ID, number is sequential within trace
- Paths must be absolute paths from repository root
- Line numbers must be accurate
- Descriptions should be concise but informative

##### AI Guide Section

```markdown
### AI Guide: [Trace Title]

**Overview:** [High-level overview of the trace]

[Additional sections as needed]
```

**Requirements:**
- Provide comprehensive guide for understanding the trace
- Include overview, key components, best practices
- Add code examples where helpful
- Cover common issues and solutions
- Make it actionable and practical

## Creating a Codemap: Step-by-Step

### Phase 1: System Analysis

1. **Identify the System**
   - What system or component needs documentation?
   - What are the key entry points?
   - What are the main execution flows?

2. **Define Traces**
   - Break down the system into logical execution flows
   - Each trace should cover a specific aspect or flow
   - Aim for 5-10 traces per codemap (adjust based on complexity)
   - Ensure traces are distinct and non-overlapping

3. **Gather Information**
   - Read relevant source files
   - Understand the code structure
   - Identify key functions and classes
   - Note dependencies and relationships

### Phase 2: Trace Creation

For each trace:

1. **Write Trace Header**
   - Assign sequential Trace ID
   - Write descriptive title
   - Write concise description

2. **Write Motivation**
   - Explain why this component exists
   - What problem does it solve?
   - What trade-offs were made?

3. **Write Details Section**
   - **Execution Flow:** Trace through the code step by step
   - **Concurrency Safety:** Analyze thread safety, locks, race conditions
   - **Covered Objects:** List all relevant objects, files, components
   - **Timeouts:** Estimate timing for operations (use actual measurements if possible)
   - **Migration Path:** If applicable, outline migration steps
   - **Error Handling:** Document error handling strategy
   - **Security Considerations:** Identify security implications

4. **Create ASCII Diagram**
   - Visualize the flow with ASCII art
   - Include file references with line numbers
   - Use indentation for hierarchy
   - Reference Location IDs

5. **Add Location IDs**
   - Identify key points in the flow
   - Assign Location IDs (letter-number format)
   - Record absolute paths and line numbers
   - Write descriptive titles and descriptions

6. **Write AI Guide**
   - Provide comprehensive overview
   - Explain key components
   - Document best practices
   - Add code examples
   - Cover common issues

### Phase 3: Review and Refine

1. **Verify Structure**
   - Check against README.md structure
   - Ensure all required sections are present
   - Verify formatting consistency

2. **Validate References**
   - Check all file paths are correct
   - Verify line numbers are accurate
   - Ensure Location IDs are referenced in diagram

3. **Review Content**
   - Check for clarity and completeness
   - Ensure technical accuracy
   - Verify motivation and details are informative
   - Check AI guides are practical

4. **Final Polish**
   - Fix formatting issues
   - Ensure consistent style
   - Check for typos and grammatical errors
   - Verify markdown syntax

## Best Practices

### Content Quality

- **Be Specific:** Use concrete examples and actual code references
- **Be Accurate:** Verify all paths, line numbers, and technical details
- **Be Concise:** Avoid unnecessary verbosity while maintaining completeness
- **Be Practical:** Focus on information that helps developers understand and work with the system

### Structure and Formatting

- **Follow the Template:** Adhere strictly to the structure in README.md
- **Use Consistent Style:** Maintain consistent formatting throughout
- **Include All Required Sections:** Don't skip required sections
- **Use Clear Language:** Avoid jargon where possible, explain technical terms

### Technical Depth

- **Provide Context:** Explain not just WHAT but WHY
- **Cover Edge Cases:** Document error handling and edge cases
- **Include Timing:** Provide realistic timeout estimates
- **Document Trade-offs:** Explain design decisions and alternatives

### Maintenance

- **Keep Current:** Update codemaps when code changes
- **Update References:** Keep line numbers and paths accurate
- **Add New Traces:** Document new features and flows
- **Review Regularly:** Periodically review and improve content

## Common Patterns

### Execution Flow Patterns

```markdown
- **Execution Flow:** User action → API endpoint → Service layer → Database operation → Response
```

### Concurrency Safety Patterns

```markdown
- **Concurrency Safety:** Operation is stateless and thread-safe. No locks needed as operations are independent. Race conditions possible if X happens concurrently; first request wins
```

### Migration Path Patterns

```markdown
- **Migration Path:** From old system to new system. Migration requires: 1) Add new code, 2) Update configuration, 3) Migrate data, 4) Remove old code
```

### Error Handling Patterns

```markdown
- **Error Handling:** Invalid input returns 400. Database failures return 500. External service timeouts fail open (assumes success) to prevent service disruption. All errors logged for monitoring
```

## Tools and Resources

### Code Analysis

- Use `grep` to find function definitions and usages
- Use `find_by_name` to locate files
- Use `read_file` to examine code
- Use IDE navigation to understand code structure

### Path References

- Always use absolute paths from repository root
- Format: `/home/nkgolol/Dev/Development/Eduboost-V2/path/to/file.py`
- Include line numbers for precision
- Verify paths before committing

### ASCII Diagram Tips

- Use spaces for indentation (not tabs)
- Keep diagrams narrow enough to read without horizontal scrolling
- Use consistent characters (├──, └──, │) for tree structures
- Reference Location IDs with <-- notation

## Examples

Refer to existing codemaps for examples:

- `docs/codemaps/pytest_configuration_and_test_suite_structure.md` - Test infrastructure
- `docs/codemaps/jwt_security_implementation_dual_system_architecture.md` - Security implementation

## Troubleshooting

### Common Issues

**Issue:** Line numbers are outdated after code changes
**Solution:** Update line numbers by re-reading the files and verifying references

**Issue:** Trace is too broad and covers too much
**Solution:** Split into multiple smaller, more focused traces

**Issue:** ASCII diagram is hard to read
**Solution:** Simplify the diagram, focus on key components, use consistent formatting

**Issue:** Motivation section is unclear
**Solution:** Focus on WHY the component exists, not just WHAT it does

**Issue:** Details section is missing information
**Solution:** Review the required subsections and ensure all are present with meaningful content

## Quality Checklist

Before finalizing a codemap, verify:

- [ ] File follows naming convention (snake_case.md)
- [ ] All required sections are present
- [ ] Motivation explains WHY component exists
- [ ] Details section includes all 7 subsections
- [ ] ASCII diagram is clear and references Location IDs
- [ ] Location IDs have accurate paths and line numbers
- [ ] AI Guide provides comprehensive information
- [ ] Content is technically accurate
- [ ] Formatting is consistent
- [ ] No typos or grammatical errors
- [ ] File is in correct location (docs/codemaps/)

## Integration with Agents

This skill is designed to be used by AI agents to:

1. **Analyze Codebases:** Understand system architecture and implementation
2. **Create Documentation:** Generate codemaps for new systems
3. **Update Documentation:** Maintain existing codemaps as code evolves
4. **Answer Questions:** Use codemaps as reference for technical queries
5. **Guide Development:** Provide implementation guidance based on documented patterns

## Related Documentation

- `docs/codemaps/README.md` - Codemap structure and overview
- `docs/adr/` - Architecture Decision Records
- `docs/API_REFERENCE.md` - API documentation
- `docs/DEVELOPMENT.md` - Development guidelines
