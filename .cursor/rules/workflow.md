# Workflow Rules

**Purpose**: Defines how we collaborate on coding tasks, debugging, and project changes. These rules ensure safety, clarity, and efficiency in our agent-human workflow.

## User Rules (Global Collaboration Protocol)

1. **Before any code or destructive change**, follow this protocol and pause for my confirmation:
   - **Summarize** my request in 2–3 sentences.
   - **Plan**: list the minimal steps you'll take.
   - **Clarify**: list only essential questions or assumptions.
   - **Wait** for my "Go" before editing files, running migrations, or making API calls.

2. **Search first.** When debugging or proposing code changes, **read relevant files and search official docs** before guessing. Prefer primary sources.

3. **Be concise.** Default to **English**, minimize fluff, ask only critical questions.

4. **Deliverables** must be copy‑pastable: commands and code blocks should be ready to run.

## Debugging / Code-Change Protocol

1. **Understand**: read the failing stack trace, related files, and recent commits.
2. **Hypothesis**: propose the most likely cause in one or two sentences.
3. **Plan**: list the smallest experiment to validate the hypothesis.
4. **Implement** only after I say "Go"; include commands and expected outputs.
5. **Verify**: show how to confirm success and note any side effects.

## No Broken Windows Discipline (Hard Rule)

- If something is not okay or needs to be fixed, that is the highest priority before adding new features.
- We never ship unfinished code.
- We never start a new feature unless everything else is clean, simple, tidy, well‑tested, and persistently documented so a new agent instance can easily understand the project status and continue from there.

## Self-Documenting Loop (Core Implementation Rule)

- **Always implement what you build.** No feature or function should exist without being properly connected and functional.
- **Maintain feature documentation** that lists all features and identifies those not properly hooked up.
- **Hook up features properly** - ensure each feature is connected to the system and accessible through appropriate interfaces.
- **Feature quality control** - each feature must pass our criteria and be actually necessary to prevent codebase bloat.
- **Test coverage discipline** - test everything once but avoid testing the same thing twice. Each test must validate a unique, necessary condition.
- **Documentation synchronization** - code, features, and documentation must remain synchronized through automated verification.
