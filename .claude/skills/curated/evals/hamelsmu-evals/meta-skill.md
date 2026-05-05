# How to Write Good Skills

Guidelines for creating and maintaining skills in this directory. Follow these when writing new skills or revising existing ones.

## Who Reads Skills

Skills are instructions for a **coding agent** (an AI assistant helping a user with a task). The agent is smart, has broad general knowledge, and doesn't need to be convinced or motivated. It needs domain-specific directives it wouldn't otherwise know. Some skills guide the agent to build an artifact (an app, a script). Others guide the agent to help the user through a process (error analysis, data labeling).

## Writing Principles

### Write directives, not wisdom

The agent needs to be told what to do, not why.

Bad: "Do not force domain experts to read raw JSON. This is the single most common annotation bottleneck. Domain experts are not engineers."

Good: "Format all data in the most human-readable representation for the domain."

Bad: "It's worth noting that using ROUGE scores as primary evaluation metrics is problematic because they measure surface-level textual overlap..."

Good: "Use binary pass/fail evaluators grounded in specific failure modes. Do not use ROUGE, BERTScore, or cosine similarity as primary evaluation metrics."

### Cut general knowledge

Only include information the agent wouldn't already know. The agent knows what JSON is, how Python imports work, what a spreadsheet is, and what frameworks exist. It does not know your domain-specific eval methodology, the specific steps in your annotation workflow, or the formulas for bias correction.

Cut:
- What things are ("A trace is the complete record of...")
- Why things matter ("Error analysis is the highest-ROI activity...")
- Framework lists ("You can use FastHTML, Streamlit, Gradio, or...")
- Motivation ("Spreadsheets fail because...")
- Academic citations

Keep:
- Domain-specific procedures the agent wouldn't know
- Templates with concrete examples
- Formulas and thresholds
- Anti-patterns specific to the domain

### Scope to the build task

If the skill is about building an annotation app, every sentence should help the agent build that app. Process advice ("schedule weekly review sessions"), organizational guidance ("assemble a team of 3-5 annotators"), and general project management ("budget 60-80% of development time for error analysis") belong elsewhere.

Ask: "Does this sentence help the agent do its job — build something or guide the user through the process?" If not, cut it.

### Start with good defaults

Present the simplest correct approach first. If an advanced technique requires something the user might not have yet, state the prerequisite explicitly.

Bad: Listing random sampling, uncertainty sampling, and failure-driven sampling as equivalent options.

Good: "Start with a random sample. If you have automated evaluators, add uncertainty sampling (traces where evaluators disagree). If you have production monitoring, add failure-driven sampling (traces that triggered guardrails or user complaints)."

### Be concrete

Vague directives are useless. Show what good looks like.

Bad: "Write clear pass/fail criteria."

Good:
```
Pass: The email addresses the client by name and references
at least one property from their saved search.
Fail: The email uses a generic greeting ("Dear customer") or
mentions no properties from the client's saved search.
```

### Convert warnings into directives or anti-patterns

Instead of a "What NOT to Do" section full of wisdom-style warnings with paragraph explanations, use one of two approaches:

**Integrate as directives** in the main instructions:
- "Use binary labels, not Likert scales" (in the feedback collection section)
- "Show the full trace, not just the final output" (in the data display section)

**List as concise anti-patterns** at the end:
- Using ROUGE or cosine similarity as primary evaluation metrics
- Building evaluators for failures you haven't observed in traces
- Rating outputs on a 1-5 scale instead of binary pass/fail

Anti-patterns should be one line each. If it takes a paragraph to explain, it's wisdom — convert it to a directive and put it in the main instructions.

### No quotes or citations

The skill is not a textbook. Remove instructor quotes, paper references, and "according to..." framing. If the information is correct, state it directly.

## Skill Structure

```yaml
---
name: skill-name
description: >
  What this skill does. Use when [triggers]. Do NOT use when [exclusions].
---
```

```markdown
# Skill Title

One-line summary of what the agent will build or do.

## Overview
[High-level summary of the procedure]

## Prerequisites
[What must exist before using this skill — only if applicable]

## Core Instructions
[The actual directives, organized by topic]

## Anti-Patterns
[Concise list of domain-specific mistakes — one line each]
```

Sections are flexible. Use what fits the skill. Not every skill needs Prerequisites or Anti-Patterns. The only required elements are the YAML frontmatter, an Overview, and the core directives.

### Keep files under 500 lines.

If a skill exceeds this, split reference material into separate files one level deep. Do not nest references (skill.md -> ref.md -> detail.md).

## Naming

- Lowercase with hyphens: `write-judge-prompt`, `error-analysis`
- Action-oriented: describes what the agent will do
- Specific: `validate-evaluator` not `evaluation-helpers`

## Testing Skills

After writing or revising a skill, test it by using it with a fresh agent instance on a realistic task. The author knows too much context.

For skills that produce a UI or application, include a testing section that instructs the agent to verify its work with Playwright (screenshots for visual review, scripted interactions for functional testing).
