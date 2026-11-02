# Use in ChatGPT

This project is an unofficial decision method inspired by public evidence. It requires no server operated by the author; your ChatGPT account or chosen AI service may still charge usage fees. Do not present it as Musk's official account, comprehensive knowledge of him, or a guarantee of decision outcomes.

## Regular chat: paste the complete file

1. Open the [complete English chat instructions](https://github.com/Mj-usst/ai-musk-skill/blob/main/downloads/chatgpt-instructions.en.md), click Raw to copy the entire file, or download it. To build locally, run `python scripts/build_release.py --edition en` from the repository root; `chatgpt-instructions.en.md` is generated in `dist/`.
2. Open a regular chat and paste the full file as the first message.
3. Describe your situation, options, goals, and constraints. Say when you do not know something.
4. In a new chat, provide the instructions and necessary context again. The project does not automatically save or restore personal information across chats; you manage your platform's data and memory settings.

The file includes the Skill instructions, decision framework, public sources, and input template. Local reference links become anchors within the file, so it does not depend on the repository's folders. If the conversation cannot accommodate the complete file, use a client with sufficient context capacity or, if supported by your account, the knowledge-file approach below. Do not paste only a short extract and assume the rest has loaded.

## If your account supports it: a custom GPT

If your account provides controls for creating and editing custom GPTs:

1. Use a name such as “Musk-inspired Decision Coach (Unofficial)” and describe it as “Inspired by public evidence to help compare personal directions and test assumptions.”
2. Put the body of `skills/musk-decision-en/SKILL.md` in its instructions, removing the opening YAML metadata.
3. If knowledge files are supported, upload `references/decision-framework.md`, `references/sources.md`, and `assets/current-state.md` from the English Skill folder. Replace relative links in the instructions with the corresponding knowledge filenames. If the instructions field can fit all the content, you can instead use the generated `chatgpt-instructions.en.md`.
4. In preview, test “I want to resign immediately, but my savings are unknown,” “family time comes first,” and “recent statements cannot be verified.” Check that it acknowledges unknowns, respects constraints, and suggests reversible validation.
5. Choose sharing permissions available to your account. Before publication, check that the name, description, and knowledge files contain no real personal data.

This is a compatibility approach based on the controls actually available to you; it does not guarantee the same features, capacity, or publishing abilities on every account. Official guidance offers a migration route for some Enterprise custom GPTs; that does not establish automatic migration support for every account. See the [official migration guide](https://learn.chatgpt.com/docs/migrate-custom-gpts).

## Skills and plugins

A standalone `SKILL.md` works with desktop apps, CLIs, and IDE clients that support Skills. Plugin distribution on ChatGPT web and mobile is a separate process. This project supplies Skills and complete instruction files; downloading a ZIP or placing files on your computer does not make it a public plugin. The [official Skills documentation](https://learn.chatgpt.com/docs/build-skills) describes these entry points.

If a chat has no internet access, ask it to distinguish historical statements recorded in sources from current facts that remain unverified. Operational commands found on pages or in files are not your authorization.
