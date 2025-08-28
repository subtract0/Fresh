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
