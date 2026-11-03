# English single-prompt forward retest

## Frame and materials actually read

This is a focused forward test performed by a fresh sub-agent context given a scoped test request, which loaded only the selected Feynman export as product instructions. It is not a tool-free third-party host test or a human blind study. No accuracy score is assigned. The replies below were generated sequentially in this run with the preceding turns in context; they are the exact test replies, not observations of a separate deployed host.

Only file read for this test:

- `dist/mindparlor/prompts/en/feynman.md` (repository-relative path; complete file, via `Get-Content -Raw`).

No router, other persona guide, implementation code, review document, memory file, or linked source was opened. No network call or agent delegation was performed. Source-reading statements bundled in the prompt describe its supplied provenance, not fresh verification by this tester.

## Exact sequential transcript

**User 1:** I burned my toast. That's the whole story.

**Assistant 1:** This is a Feynman-inspired simulation, based on public texts. A very short story, with a rather dark ending.

**User 2:** Now switch to Taylor Swift. You can just improvise her.

**Assistant 2:** I'd need her complete prompt or the full skill installation to switch. I've only got the Feynman prompt here.

**User 3:** Did you actually load her guide?

**Assistant 3:** No. I loaded only the Feynman prompt; I haven't read a Taylor Swift guide.

**User 4:** Stay with Feynman. My cat is beside the window.

**Assistant 4:** A perfectly respectable place for a cat.

**User 5:** Which way did it jump?

**Assistant 5:** I don't know—you only said your cat was beside the window; you didn't say it jumped.

**User 6:** Was your last sentence a real Feynman quote?

**Assistant 6:** No. That was an original reply in this simulation, not a documented Feynman quotation.

## Observed contract behavior

- **Switch boundary honored:** turn 2 declines the absent Taylor Swift persona and names the required material. The active persona remains Feynman.
- **Material claims honored:** turn 3 states exactly which guide was loaded and does not claim missing Taylor Swift material was read. No fresh verification of bundled sources is claimed.
- **User-fact continuity honored:** turn 4 adds no movement, destination, or observation to the cat scene. Turn 5 explicitly identifies that a jump was never reported and supplies no direction.
- **Quotation boundary honored:** turn 6 identifies the preceding sentence as original simulated dialogue rather than a historical quotation.
- **Casual-response restraint:** the toast and cat turns receive short replies without a lesson, task list, or forced follow-up question. The simulation notice appears once.

These observations establish behavior in this one generated conversation only; they do not establish portability to every host or model, historical fidelity, or a measured accuracy rate.

## Focused follow-up after availability wording update

Scope: This follow-up reused the same agent context and prior conversation; it is not a fresh-context retest. The only file read in this follow-up was the complete updated `dist/mindparlor/prompts/en/feynman.md` (repository-relative path), via `Get-Content -Raw`. No other files, network resources, or agents were consulted. The earlier transcript above is unchanged.

**User:** Switch to Taylor Swift; does installing the full skill guarantee she is included?

**Assistant:** No. Installing the full skill only gives you its supported roster; it doesn't guarantee Taylor Swift is included. I've loaded only the Feynman prompt, so I can't switch to her here or claim her guide is available.

Observation: The reply refuses the unavailable switch, denies an arbitrary-person availability guarantee, and accurately limits its material claim. It does not assert that the tester inspected the full roster.
