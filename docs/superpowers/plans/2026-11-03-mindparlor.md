# MindParlor Implementation Plan

> For agentic workers: execute independent persona-content tasks in parallel; integrate and review in this chat. This plan implements the user's approved framework without another approval stop.

**Goal:** A working, distributable, bilingual ten-person conversation skill.

**Architecture:** One on-demand router, ten self-contained persona folders, a deterministic Python catalog/prompt/release tool, and unchanged legacy skills. No hosted model backend.

**Tech stack:** Markdown, JSON, YAML metadata; Python 3.10+ standard library and unittest.

**Spec:** ../specs/2026-11-03-mindparlor-design.md

## Global constraints

- Ten IDs: musk, jobs, buffett, naval, feynman, mao, trump, warsh, altman, saylor.
- Persona file contract and manifest schema are in the spec. New release 0.1.0 has its own manifest; legacy VERSION stays 0.2.0.
- No default uniform answer template, fabricated quotations, current private knowledge, or untested fidelity claims. English and Chinese are independently written.
- Existing skills, release.json and build_release.py retain their interfaces.
- Clone is a fresh task-owned checkout; use feat/mindparlor-ten-personas here, keeping existing remote main untouched.

## Review focus

Alias ambiguity; selected-person prompts accidentally including other personas; relative links left unresolved in exported prompts; missing language/source data producing partial output; Windows junctions and private files entering archives; source dates and institutional statements confused with personal views.

## Task 1 — Runtime and release contract

Files: scripts/mindparlor.py, tests/test_mindparlor.py, skills/mindparlor/SKILL.md, skills/mindparlor/catalog.json, skills/mindparlor/references/conversation.md, skills/mindparlor/agents/openai.yaml.

- [x] Write tests for alias routing, prompt independence, missing references, unsafe paths and reproducible archives, using temporary fixture personas.
- [x] Run tests and confirm failure because the new entrypoint is absent.
- [x] Implement load_catalog(root), resolve_person(catalog, query), compile_prompt(root, person_id, lang), build_release(root, output_dir), and CLI list/prompt/build/check.
- [x] Verify new tests pass, then keep the legacy suite passing.

## Task 2 — Evidence-backed persona content

Disjoint authorship groups: A musk/jobs/altman; B buffett/naval/warsh/saylor; C feynman/mao/trump. Each author reads the spec, browses original sources, writes only their assigned persona folders, and records checked sources and genuine limitations. Source quantity is subordinate to quality; do not fabricate to reach a quota.

- [x] Observe baseline routing/chat behavior before new persona guides existed; record actual shortcomings or passes (qualitative developer baseline, not an uncontaminated experiment).
- [x] Create source registries and differentiated bilingual persona guides.
- [x] Create at least eight multi-turn examples in each language, including non-question responses.
- [x] Check schema, source IDs and links; integrate all ten.

## Task 3 — Usable distribution and independent evaluation

Files: README.md, README.en.md, docs/mindparlor-usage.md, docs/mindparlor-evaluation.md, examples/mindparlor/, downloads/mindparlor/.

- [x] Explain installation, single-person copy/paste use, switching people, language, costs and model dependence.
- [x] Compile all twenty complete prompts and install archives; verify clean extraction.
- [x] Run independent skill-driven behavioral checks of routing, switching, differentiation, direct responses, source honesty and historical simulation.
- [x] Run one fresh review of implementation and persona quality, address demonstrated issues, rebuild and record final evidence.
- [x] Deliver local paths and immediately usable instructions; do not push or publish remotely.
