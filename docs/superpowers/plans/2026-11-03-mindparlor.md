# MindParlor Implementation Plan

> For agentic workers: execute independent persona-content tasks in parallel; integrate and review in this chat. This plan implements the user's approved framework without another approval stop.

**Goal:** Keep only the working, distributable, bilingual ten-person conversation skill in the renamed `Mj-usst/mindparlor` repository. This updated plan incorporates the user's later cleanup instruction and supersedes earlier preserve-legacy constraints. Retain Git history.

**Architecture:** One on-demand router, ten self-contained persona folders, and a deterministic Python catalog/prompt/release tool with its own small release-support module. No hosted model backend.

**Tech stack:** Markdown, JSON, YAML metadata; Python 3.10+ standard library and unittest.

**Spec:** [MindParlor specification](../specs/2026-11-03-mindparlor-design.md)

## Global constraints

- Ten IDs: musk, jobs, buffett, naval, feynman, mao, trump, warsh, altman, saylor.
- Persona file contract and manifest schema are in the spec. MindParlor release version is 0.1.0 preview.
- No default uniform answer template, fabricated quotations, current private knowledge, or untested fidelity claims. English and Chinese are independently written.
- Remove all unrelated functionality and its distribution artifacts from the current tree; keep only MindParlor source, tests, examples, documentation and downloads, plus repository metadata.
- The user authorized publication and repository renaming after the initial local implementation. The renamed repository has been verified as `Mj-usst/mindparlor`; publish the cleanup after final verification.

## Review focus

Alias ambiguity; selected-person prompts accidentally including other personas; relative links left unresolved in exported prompts; missing language/source data producing partial output; Windows junctions and private files entering archives; source dates and institutional statements confused with personal views.

## Task 1 — Runtime and release contract

Files: scripts/mindparlor.py, scripts/release_support.py, tests/test_mindparlor.py, skills/mindparlor/SKILL.md, skills/mindparlor/catalog.json, skills/mindparlor/references/conversation.md, skills/mindparlor/agents/openai.yaml.

- [x] Write tests for alias routing, prompt independence, missing references, unsafe paths and reproducible archives, using temporary fixture personas.
- [x] Run tests and confirm failure because the new entrypoint is absent.
- [x] Implement load_catalog(root), resolve_person(catalog, query), compile_prompt(root, person_id, lang), build_release(root, output_dir), and CLI list/prompt/build/check.
- [x] Verify MindParlor tests pass. The initial combined-suite result is historical evidence; the current suite covers only the retained product.

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
- [x] Deliver local paths and immediately usable instructions. The initial local-only delivery has been superseded by the user's later publication request.

## Task 4 — MindParlor-only repository

- [x] Extract the required text/link/ZIP helpers into `scripts/release_support.py`; remove dependency on deleted tools.
- [x] Remove unrelated functionality and artifacts from the current tree while retaining Git history.
- [x] Add boundary regressions for the retained release workflow; implementer and integrator each ran 25 tests, all passed, 0 skipped, including real Windows junction checks. The integrator also passed the ten-person/twenty-prompt catalog check.
- [x] Reconcile active documentation and verify the repository rename to `Mj-usst/mindparlor`.
- [x] Rebuild and verify all 23 public downloads, clean extraction of 65 install files, twenty prompt equivalents, SHA256 values and repeat-build equality; prepare the cleanup for authorized publication to the renamed repository.
