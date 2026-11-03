# MindParlor implementation record — 2026-11-03

## Current scope and cleanup

- The user's latest instruction is to keep only MindParlor's bilingual ten-person conversations. It supersedes the initial preserve-legacy and local-only delivery constraints. Git history is retained; unrelated skills, tools, tests, examples, documents and downloads are removed from the current tree.
- Canonical roster: musk, jobs, buffett, naval, feynman, mao, trump, warsh, altman, saylor. The user approved Mao Zedong in place of Marcus Aurelius during design.
- The repository rename has been verified as `Mj-usst/mindparlor` using the same repository ID, 1443111824. The public description and local origin URL now use MindParlor.
- Required release helpers now live in `scripts/release_support.py`; the retained runtime is independent of deleted tools. Both the implementer and integrator ran the current MindParlor-only suite: **25 tests passed, 0 skipped**, including real Windows junction checks. The integrator also passed the catalog check for ten people and twenty prompts.
- The integrator rebuilt and synchronized all 23 public download files, verified their SHA256 manifest, extracted all 65 installation files into a fresh temporary directory, and recompiled all twenty prompts from that copy. Standalone files match the prompt ZIP, a repeat build is byte-identical, and current Markdown links resolve. Only MindParlor remains under `skills/` and `downloads/`.
- Release label remains **0.1.0 preview**. Automated packaging and agent observations are distinct from external human validation.

## Initial implementation evidence

- Development began from a fresh task-owned checkout. The original distribution baseline was 26 passing tests. The first twelve MindParlor tests failed because the runtime did not yet exist, then passed after implementation.
- A byte-level regression reproduced Windows GBK output in captured Chinese menus; CLI streams were corrected to UTF-8. Source files were already UTF-8.
- Ten personas were integrated with 70 registered source records and 160 original four-turn scenarios, eight per language per person. Alias gaps for 山姆·奥特曼 and 美联储主席 were fixed.
- Independent review reproduced export-over-input and Chinese-adjacent source-ID defects. Regressions failed before fixes and passed afterward. Standalone prompts also gained an explicit selected-person availability boundary.
- Before the MindParlor-only cleanup, the combined suite passed **41 tests, 0 skipped**: 26 tests for now-removed functionality and 15 MindParlor tests. This is historical evidence, not the current suite count.
- Initial packaging checks covered a 65-file install ZIP, twenty complete prompts, their ZIP and SHA256 manifest; 23 public download files. Clean extraction, recompilation, installed bytes and hashes matched at that stage. Current artifacts have also been rebuilt and verified after the cleanup, as recorded above.

## Behavioral evidence and limits

- Fresh-context English and Chinese single-person checks, router checks, a scripted 20-user-turn conversation and limited source spot checks are recorded in [the evaluation](mindparlor-evaluation.md) and its linked reports.
- Emotional and casual voices can converge; some polished jokes and mild scene inferences remain. Jobs corporate copy provides weaker evidence of personal conversational style.
- No external bilingual human blind test, cross-host validation, exhaustive 20-turn-per-person evaluation or measured likeness claim is made.
