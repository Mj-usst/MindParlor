# Musk-inspired Decision Coach

[中文](README.md) | English

An English AI decision Skill for understanding your current situation, career choices, and startup direction. It draws inspiration from first principles and engineering methods in Musk's public material, then combines them with this project's cash-flow, option-comparison, and small-experiment tools to help you form testable judgments. The [Chinese edition](README.md) is available separately.

This is an **unofficial simulation of a method**, unaffiliated with Elon Musk or his companies and not his personal advice. It uses selected public sources, does not contain comprehensive knowledge of him, guarantees no outcomes, and does not assume long-term memory across chats.

## Easiest way to use it

1. Open the [complete English chat instructions](https://github.com/Mj-usst/ai-musk-skill/blob/main/downloads/chatgpt-instructions.en.md), click Raw and copy the entire file, or download it.
2. Open a regular ChatGPT chat and paste the complete contents.
3. Describe your situation and question, for example:

   > I have worked in manufacturing for five years and want to compare staying employed, changing careers, and starting a side business. Monthly essential expenses are about RMB 8,000, savings about RMB 100,000, and I have family responsibilities and six hours a week available. Separate facts from assumptions, suggest a reversible next step, and explain what evidence would change your advice.

You can also install the Skill in a client that supports Skills. The project runs no server and makes no calls to the author's model API, so **the author has no backend or model-call costs; users' own AI accounts, subscriptions, or APIs may charge fees**.

## Install in Codex

Repository: [Mj-usst/ai-musk-skill](https://github.com/Mj-usst/ai-musk-skill).

In a Codex session supporting `$skill-installer`, send:

```text
$skill-installer Install musk-decision-en from https://github.com/Mj-usst/ai-musk-skill/tree/main/skills/musk-decision-en
```

For manual installation, [download `musk-decision-en-v0.2.0.zip`](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/musk-decision-en-v0.2.0.zip) and extract the entire `musk-decision-en` folder into:

```text
~/.agents/skills/musk-decision-en/
```

On Windows, use `%USERPROFILE%\.agents\skills\musk-decision-en\`. Confirm that `SKILL.md` is directly inside that folder, then start a new Codex session and send:

```text
$musk-decision-en Help me compare my current job, a career change, and a side business. Start with the information I have already provided.
```

Standalone Skills are for desktop apps, CLIs, or IDE clients that support them. Plugin distribution on ChatGPT web and mobile is a separate publishing process. Downloading this ZIP does not install a ChatGPT plugin or enable a web chat to read a local `SKILL.md`. See the [official Skills guide](https://learn.chatgpt.com/docs/build-skills).

## Use in ChatGPT

For a regular chat, paste the complete instructions as described above. If your account supports custom GPT creation, follow the [English ChatGPT setup guide](docs/chatgpt-setup.en.md). Available controls, knowledge files, and sharing permissions depend on your account.

The [fictional example conversation](examples/career-direction.en.md) shows how facts, unknowns, assumptions, recommendations, contrary evidence, validation, and review fit together.

## How it helps

It identifies constraints and key unknowns, compares the status quo with candidate directions and transition paths, and gives a conditional recommendation, tradeoffs, validation action, and review conditions. Amounts, deadlines, and success thresholds are adjustable suggestions to adapt to your responsibilities and tolerance for risk. Intense work and entrepreneurship are not default goals for everyone.

Public evidence about Musk, general decision tools, and model judgment are identified separately. Current information requires online verification; without access, the assistant should state what is unknown rather than invent quotations or verification results. Original sources appear in [sources.md](skills/musk-decision-en/references/sources.md).

## Privacy and authorization

Share only information relevant to the decision. The Skill provides no independent storage, upload, or external execution service; your AI platform's data and memory settings still govern chat content. Keep irrelevant identity numbers, passwords, and customer information out of your input.

Personal inputs and exported results can go in local `private/` or `decisions/` folders, which Git ignores and the build script excludes. Still review changes before committing, especially so real personal details do not enter public templates. Actual actions such as sending messages, transactions, resignation, or submitting documents require your separate decision and authorization.

## Build it yourself

Python 3.10 or later is required, with no third-party dependencies. From the repository root, run:

```sh
python -m unittest discover -s tests -v
python scripts/build_release.py --all
```

Outputs in `dist/`:

Omit `--all` for Chinese only, or use `--edition en` for English only. `release.json` declares the editions and references; the builder validates all configured editions before creating output.

- `musk-decision-v0.2.0.zip`: installable Chinese Skill folder and license.
- `musk-decision-en-v0.2.0.zip`: installable English Skill folder and license.
- `ai-musk-skill-v0.2.0.zip`: public repository text sources.
- `chatgpt-instructions.md`: standalone Chinese instructions with framework, sources, and input template included.
- `chatgpt-instructions.en.md`: standalone English instructions with framework, sources, and input template included.

Published files live in [downloads/](https://github.com/Mj-usst/ai-musk-skill/tree/main/downloads). After changing a Skill or sources, rebuild and copy these files from `dist/` to `downloads/` before committing. The source ZIP's public-path allowlist excludes `downloads/` to avoid recursively packaging old distributions.

Packaging uses public-path and text-extension allowlists, excluding dot-hidden paths at any depth (except root `.gitignore`), private folders, caches, symbolic links, Windows junctions and other reparse points, generated files, and binaries. Traversal skips these directories directly. The input root, output directory and their ancestors, and existing output targets must not pass through links or reparse points. Missing versions or Skill references cause an error before the output directory is created. Use `--root` and `--output-dir` for other input and output locations.

## License

Original project content, including this English translation, uses the [MIT License](LICENSE). Linked third-party material remains the property of its rights holders and is not relicensed by this project.

## Additional Chinese Skill

This repository also distributes [Mao Selected Works methods for practice](docs/mao-practice.md), a separate Chinese-language Skill invoked as `$mao-practice`. Its source notes distinguish historical texts from the author's modern applications. Installation packages and complete chat instructions are in [downloads/mao/](downloads/mao/).
