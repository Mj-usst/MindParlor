# MindParlor

**Choose a mind. Start a conversation.**

An open-source conversation skill with ten distinctive public-figure simulations, independently written in English and Chinese. Use your existing AI tool: no author-hosted chat service or model API account is required.

**Version 0.1.0 preview.** Unofficial simulations based on public material; no affiliation, authorization or claim that a new answer is a real statement by that person. See the [evaluation record](docs/mindparlor-evaluation.md) for the checks actually performed.

[简体中文](README.md) | English

## Choose someone

| Person | Starting points |
|---|---|
| Elon Musk | Engineering, products, space, future |
| Steve Jobs | Taste, creativity, focus, choices |
| Warren Buffett | Business, time, long-term judgment |
| Naval Ravikant | Autonomy, work, wealth, happiness |
| Richard Feynman | Curiosity, learning, everyday puzzles |
| Mao Zedong | Investigation, contradictions, history |
| Donald Trump | Negotiation, leadership, media |
| Kevin Warsh | Money, inflation, employment, policy trade-offs |
| Sam Altman | AI, startups, teams, future |
| Michael Saylor | Bitcoin, money, digital capital |

Each person has a separate conversational guide, source registry and original multi-turn examples. There is no fixed empathy–analysis–action-plan template. Casual chat can stay casual, and a character can disagree.

## Start by copying one file

**The self-contained prompts are intended for ordinary ChatGPT and Claude chats.** No Codex installation or local code execution is needed for this route. Native account installations and behavior on those two platforms have not yet been tested.

Open the [English prompt directory](downloads/mindparlor/prompts/en/), choose a person, and paste the complete file into a fresh AI chat. Then talk normally. Try [Feynman](downloads/mindparlor/prompts/en/feynman.md), [Sam Altman](downloads/mindparlor/prompts/en/altman.md), or [Mao Zedong](downloads/mindparlor/prompts/en/mao.md).

For example: “I've been busy all week, but I can't point to anything I finished. Just talk with me for a bit; don't give me a checklist.”

The [prompt collection ZIP](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/mindparlor/mindparlor-prompts-v0.1.0.zip) contains twenty self-contained files. Copy/paste prompts contain one person only. Start another chat with another full prompt to switch; the complete skill below supports switching in file-reading hosts.

## Install the full skill

Extract [mindparlor-v0.1.0.zip](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/mindparlor/mindparlor-v0.1.0.zip) into your client's supported skills directory, preserving the entire `mindparlor` folder. For hosts recognizing `~/.agents/skills`, the entrypoint is `~/.agents/skills/mindparlor/SKILL.md`. Open a new chat and try:

```text
$mindparlor Show me the ten people
$mindparlor Talk with Feynman about why learning feels like memorizing names
$mindparlor Switch to Buffett and continue
```

Client support and installation directories vary. Claude also supports uploading a skill ZIP through `Customize → Skills`, with code execution and file creation enabled; account and organization controls still apply. See [Claude's official guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) and the project [usage guide](docs/mindparlor-usage.md). Copy/paste alone does not grant local file access or cross-chat memory.

## Build and verify

Python 3.10+; standard library only.

```sh
python scripts/mindparlor.py list --lang en
python scripts/mindparlor.py prompt "Sam Altman" --lang en
python scripts/mindparlor.py check
python scripts/mindparlor.py build
python -m unittest discover -s tests -v
```

`dist/mindparlor/` receives the installation ZIP, twenty prompts, prompt ZIP and SHA256 manifest. Validation checks the whole roster before release writes, and archives contain only approved files. Source registries live in [the persona folders](skills/mindparlor/personas/).

The project is free. Your own AI subscription or API can cost money. Model behavior, context and host settings affect results and privacy. This preview does not claim measured human likeness, human bilingual blind-test success or stability across every model.

Mao is a text-grounded historical reconstruction. Kevin Warsh's role as Fed Chair was checked on 2026-11-03; the persona remains that specific person if the office changes. Saylor is a Bitcoin advocate and entrepreneur, not Bitcoin's creator. Source files do not automatically update.

## Existing skills

The original [Chinese Musk decision advisor](skills/musk-decision/SKILL.md), [English edition](skills/musk-decision-en/SKILL.md), and [Mao-method advisor](skills/mao-practice/SKILL.md) remain available. Their method-advice workflows are separate from the new character conversations. The legacy builder remains `python scripts/build_release.py --all`.

## License

Original project code, guides and example conversations use the [MIT License](LICENSE). Third-party sources and rights associated with the people are not relicensed. Registries provide links and short original summaries, not copied books or transcripts.
