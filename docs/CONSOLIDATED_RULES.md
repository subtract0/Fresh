# Fresh AI Agent System - Consolidated Rules

> **Precedence**: Rules are listed in order of precedence (earlier = higher priority)  
> **Source**: Consolidated from 27 original rules, eliminating 18 duplicates  
> **Coverage**: All unique requirements preserved

---

## 1. 📚 Project Documentation & Truth Source *(Highest Priority)*

**1.1** Use `WARP.md` as the authoritative project guide for Fresh AI Agent System
- Reference: `/Users/am/Code/Fresh/WARP.md`
- Contains verified features, implementation status, and working examples
- See `docs/FEATURE_STATUS.md` for actual implementation truth matrix

**1.2** Before integration work, always check the most recent reference to ensure everything is state-of-the-art
- Must be documented as an architectural decision
- Include MCP reference: `688cf28d-e69c-4624-b7cb-0725f36f9518` when applicable
- *Original: aEaYmc0Wa0la6ORpSe0yD8, rDFn3SorYOYZDb77Bk0Nfv*

---

## 2. 🚧 Development Workflow & Quality Standards

**2.1** No Broken Windows Policy *(CRITICAL)*
- Always prioritize urgent/critical tasks first ("as long as this house is on fire, we won't go fishing")
- Fix issues before adding new features - never ship unfinished code
- Keep codebase clean, simple, tidy, well-tested, and well-documented
- *Original: 4XkBfuiZeaaxuUdUSIuI9C, B1GTGWAZ9NBjgwCHXyhb02*

**2.2** Git & Branch Management
- Always use a branch when building features
- Commit and push changes to GitHub safely following professional best practices
- *Original: GkRy7VAnM5HsW9C0JZdqPI (7 duplicates consolidated)*

**2.3** End-to-End Task Completion
- Take tasks end-to-end without interruption until all is done:
  - All broken windows fixed
  - All tests running
  - All changes committed and pushed to GitHub
- *Original: I5FebVXCYbUMudUOrGTgom*

**2.4** Test-First Development & Documentation
- AI agents should always start by creating tests before building features
- Document all key architectural decisions in `.cursor/rules/ADR.md`
- *Original: SLqHxGNVsR9lBWtddMuFVs*

**2.5** Test Requirements
- Tests must be necessary for the system to work
- Each test designed to always pass when condition is met, never pass when not met
- The condition tested must be necessary for program to function correctly
- *Original: D5IkgGIOXrnIx2btm2IoXQ (4 duplicates consolidated)*

---

## 3. 🛡️ Security & Safety Practices

**3.1** Environment & Secrets Management
- Keep .env files safe and local
- Never commit actual sensitive information to version control
- Follow best security practices for all integrations
- *Original: r7hQsRtnuHnuA6Nt5JWZAc*

**3.2** Database Safety
- Agents should never connect to production databases
- Must always use a staging environment during development
- Ensures safety and prevents unintended data changes
- *Original: vJvfCo2HFG5hIbFDbeiu8r*

---

## 4. 🎯 Mission & Architecture Guidance

**4.1** Core Mission
- Create a persistent-memory and learning mother-agent that spawns agents
- Expected agent arguments: name, instructions, model, output_type
- *Original: JXWXHObstS3LSFlAlppgCH (3 duplicates consolidated)*

**4.2** Self-Documenting System Loop
- Install self-documenting loop in core codebase ensuring:
  - Always implementing what is built
  - Maintaining feature documentation listing all features
  - Hooking up any features not yet integrated
  - Validating each feature meets necessity and uniqueness criteria
  - Ensuring all features are tested once and only once
- Avoids codebase bloat and redundant tests
- *Original: 810PrY6gGHKOCAY6TzRMcS (2 duplicates consolidated)*

---

## 5. 📢 Communication & Workflow Preferences

**5.1** Structured Global Workflow
- Follow summarize-plan-clarify-confirm workflow before code/destructive changes
- Search-first approach for debugging
- Concise English communication with copy-pastable deliverables
- Short, practical, bullet-pointed output with one sharp follow-up question only when essential
- *Original: uWO9aFcmI9KPxQDxFLau7S*

**5.2** Notification Management
- Reduce/solve excessive GitHub notification emails autonomously
- Contributes to 'broken windows' problem and must be addressed
- Solution should prevent notification overload
- *Original: s01GqEvqdOoCeZXzoX6UUH*

---

## 📋 Rule Mapping & Auditability

**Duplicates Eliminated (18 rules)**:
- No Broken Windows: U2dqezKfogNUufjKalYp6k, ZAZm8fdJxYZMbM2BSLybb3, djEQZicOOMEVHBVCvotbGJ
- Git Practices: PEsDplSiDuXYpzEA6qAKjz, ka8M869ySub8uH7TLMWM6I, lwgkkCifMIebRQdGGUzJTb, o5fvdwyOC4sQR8VIwneHxm, sHKjqC5SZSw6NIHKTGTZBT, thmI1mt9PELi5OML1m6tvo
- Mission Statement: SJeJGdMF6y9AoCkGfCJMSs, iwcuudAXfhp2DleHlaHwP5
- Test Requirements: ZTGXECngBm5OQ9zqfYhk5z, juAS8J7azW6mlVoywakLrn, tsiNoKx78yv5Inxv2QL06p
- Self-Documenting: K76Q5BrxNsN6VtgFkM65to
- State-of-Art: rDFn3SorYOYZDb77Bk0Nfv

**Unique Rules Preserved (9 rules)**:
- All functional requirements maintained
- All unique constraints preserved
- Precedence order respected

---

*Generated: 2025-01-04 | Consolidation reduced 27 rules to 12 statements | Zero requirements lost*
