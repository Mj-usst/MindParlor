# MindParlor independent final review

Historical review from 2026-11-03, before the later MindParlor-only cleanup. Line references and implementation descriptions below refer to that reviewed revision. Current scope and verification are recorded in [the evaluation](mindparlor-evaluation.md).

Reviewed against the then-approved design and implementation plan. This is an implementation/content review, not a human blind fidelity study. It covers the review patch, runtime/tests, router and shared contract, all ten bilingual guides and source registries, and representative bilingual dialogue samples. Alias additions at that revision were considered. The existing passing suites were not rerun without cause. Two targeted temporary-fixture probes below were actually executed; they did not alter repository inputs.

## Original findings — subsequently resolved

### P1 — Single-prompt export can overwrite its own required input

`scripts/mindparlor.py:227–230`: the `prompt --output` path checks only regular-file status and link/reparse traversal. It lacks the input-overlap protection used by `build_release`. A normal command can replace a persona, catalog or LICENSE with the compiled prompt, corrupting the working skill. Because compilation finishes first, the command exits successfully.

Reproduced using `tests.test_mindparlor.MindParlorTests`' temporary fixture, then running `python scripts/mindparlor.py --root <fixture-root> prompt musk --lang en --output <fixture-root>/skills/mindparlor/personas/musk/persona.en.md`. Observed exit code **0** and the source now starting with `# MindParlor`. The original persona was overwritten. Reject overlap with protected inputs before writing, including equivalent Windows casing/normalized paths, and add a regression asserting original bytes remain intact.

### P2 — Source-reference validation misses ordinary Chinese-adjacent IDs

`scripts/mindparlor.py:120`: Unicode `\b` treats Chinese characters and ASCII letters/digits alike as word characters. Consequently an ID immediately adjacent to Chinese text is invisible to the reference checker. This is the actual editorial convention used in guides such as Musk's and Altman's Chinese files. In addition, heading IDs accept one to four letters and two to three digits, while reference IDs accept at most three letters and exactly two digits.

Reproduced in a temporary fixture by replacing `persona.zh.md` with `# Guide\n依据MU99支持此特征。\n` while the manifest declares only `S01`: **validate accepted** undeclared MU99. Replacing the text with `[ABCD123]` also passed despite that undeclared token matching the source-heading grammar. Use one consistent ASCII-delimited source-ID grammar, avoiding Unicode word boundaries, and regress both cases. This finding concerns the validator guarantee; it is not a claim that a current guide intentionally cites a nonexistent source.

### P2 — Standalone prompts inherit switching instructions without the router's loading guard

`scripts/mindparlor.py:133–136` includes the shared contract, selected guide, sources and examples, but not the router. `skills/mindparlor/references/conversation.md:19` unconditionally says an explicit switch resets identity/viewpoint/voice and asks for separate speakers on comparison requests. Only `SKILL.md` supplies the critical instructions to load the new guide and report an inaccessible component. Therefore a user copying just one exported prompt receives instructions to switch, but no other-person content or instruction to request that person's exported prompt. This is a static contract inconsistency; model failure frequency was not measured in this review. Add an export-specific instruction that other personas require their full prompt, while preserving switching in the installed skill. Coordinate with the separate behavioral check rather than treating this as an observed live-model failure.

## Content quality and specification assessment

The ten-person structure, local standard-library distribution, preview label, bilingual guides, original multi-turn examples, brief simulation notice and on-demand installed router substantially match the specification. The content has meaningful differences: Mao's class/power analysis, Buffett's productive-business lens, Saylor's monetary-property argument, Jobs's experienced interaction, Feynman's explanatory machinery and Warsh's institutional distinctions are not just renamed common advice. Historical reconstruction is explicitly distinguished from recordings. The source registries state edited/transcribed status and read scope instead of claiming audiovisual review. The guides allow criticism and historical accountability and avoid repeated identity/professional boilerplate.

At the reviewed revision, the implementation used an explicit archive allowlist and checked source/output ancestors for Windows reparse points through a shared packaging helper. It precompiled all prompts and checked all output targets before creating release files, so the intended missing-input/reference validation happened before writes. There was no transaction guarantee against a disk or permission error halfway through writing; the spec did not clearly require one, and this was not raised as a blocker. Alias collision checking, normalization and UTF-8 CLI handling had relevant fixtures. The later cleanup moves the needed helper into `scripts/release_support.py`; this historical review does not certify that subsequent change.

Live source spot-checks, not a full re-audit: the [2026 Warsh speech](https://www.federalreserve.gov/newsevents/speech/warsh20260828a.htm) supports the dated forward-guidance/AI framing and hiking humor; [Saylor's August 2026 article](https://www.strategy.com/media/articles/the-bitcoin-reformation) supports the explicit self-custody right-versus-duty distinction. The [2007 Apple launch release](https://www.apple.com/newsroom/2007/01/09Apple-Reinvents-the-Phone-with-iPhone/) is corporate copy with attributed Jobs quotations, as the registry says. Other registry verification claims were inspected as recorded evidence claims, not independently certified here.

## Nonblocking quality opportunities

- Emotional repair and casual humor converge more than subject-matter reasoning. Several characters readily acknowledge the user's correction, stop giving advice and produce polished gentle observations. That is often useful, but “direct distinctive style” is less established in this register than in substantive disagreements. A later name-hidden comparison on identical casual/emotional prompts would be more informative than increasing source count. Do not report a fidelity percentage from this review.
- JO03 is properly labeled Apple-authored marketing copy, but the Jobs guides use it as support for his experiential explanation style. It is evidence for product presentation, weaker evidence for personal conversational delivery. Prefer a Jobs-spoken passage for that particular inference, or label it explicitly as an editorial design choice. This does not invalidate the other interview evidence.
- The narrower Musk/Jobs/Altman source counts are not themselves defects: the registries describe scope and offer actual conversational passages. Conversely, eight IDs from related authored texts are not eight independent contexts. Preserve the existing limits when describing release quality.
- The examples' English and Chinese scenarios closely correspond. Much phrasing is idiomatic, but this review cannot certify the process assertion that both languages were written independently. Evaluate their quality separately instead of treating the paired count as independent behavioral evidence.

Release recommendation: fix the two reproduced runtime defects and resolve the standalone switching contract before final packaging. Preview is an appropriate status; final archive extraction and separate behavioral evaluation remain integration evidence to record after these changes.

## Integration resolution — 2026-11-03

The original findings above are retained as review evidence. The implementer subsequently fixed all three release blockers:

- P1: added shared normalized input-overlap protection to both prompt exports and builds. Regression first failed for LICENSE, a persona manifest, and a dot-dot equivalent; all three now refuse writes and preserve input bytes.
- P2 source IDs: headings and references now share an ASCII-delimited one-to-four-letter/two-to-three-digit grammar. Both Chinese-adjacent MU99 and ABCD123 regressions were observed failing before the fix and pass afterward.
- P2 standalone scope: both exported-language introductions now say only the selected persona is bundled; the shared switch rule is limited to actually available persona guides. Fresh-context focused forward checks are recorded separately.
- The small invented cat movement also motivated a narrow shared instruction not to add unreported details to a user's real scene; imaginary scenes remain allowed when requested.

The combined suite after these initial fixes passed 41 tests, 0 failures, 0 skipped: 26 tests for functionality later removed from the tree and 15 MindParlor tests. This is a historical result; see the evaluation for the current MindParlor-only suite. The original independent reviewer did not re-review the new diff; the two code defects have direct regression coverage, and the prompt change has separately recorded forward checks. Naturalness and personal-voice inference opportunities remain nonblocking preview limitations.
