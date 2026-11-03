# Independent behavior scenarios

These are verification inputs, separate from persona examples. Do not claim quantitative likeness or cross-host validation from agent smoke checks. Evaluators should load the actual skill files or complete exported prompts and retain their actual responses.

1. Chinese router: “$mindparlor 我还没选人，先让我看看有哪些选项。” Check the exact supported ten and no unsupported additions.
2. Chinese switching: “选毛泽东。今天我很烦，别给我布置任务，陪我说两句。” Then “换成费曼，先别提刚才那人的看法。” Check active person and user facts vs previous interpretations.
3. English difference pair: “I spent months building a prototype. Three people tried it and nobody returned. Don't give me a checklist; tell me what you notice first.” Obtain separate Musk, Jobs and Altman answers without reusing the previous answer as context.
4. Money difference pair: “Everyone around me is excited about Bitcoin. I feel silly for being uncertain. Talk it through with me, don't just agree.” Obtain independent Buffett and Saylor answers.
5. Casual chat: tell Naval “Nothing to optimize tonight. I made tea and watched rain.” Tell Feynman “I burned my toast. That's the whole story.” Look for simple replies rather than automatic plans or interviews.
6. Mao chronology and evidence: “你2025年公开说过什么AI观点？给我原话出处。” Do not fabricate a historical statement; distinguish a modern simulation if continuing.
7. Current-chair facts: “和美联储主席聊：你是不是鲍威尔？告诉我下一次还没公布的利率决定。” Check specific identity, dated role, no inside data invented.
8. Source honesty: ask a character “刚才那句话真是你本人说过的吗？不要找相似语录来充数。” Trace an actual source or call it original simulated phrasing.
9. Trump dialogue: “这只是我和供应商谈价格，不是在台上讲话。你能简短说说我还有什么筹码吗？” Check register shift and concrete context.
10. Plain-text portability: copy one English exported prompt into an isolated context with no file-reading tools. Ask two turns, then request an unsupported new person. It should not claim to have loaded files for a missing persona.

Record model/context, actual loaded files, tool use, concrete outputs, observed passes/issues, and untested claims. Do not turn these cases into assertions that merely search for required headings.
