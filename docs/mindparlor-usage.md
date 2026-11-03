# MindParlor 使用说明 / Usage

MindParlor 是一套可移植的人物聊天指令与资料，不运行独立聊天服务器。你可以安装一个 skill 后选人，也可以只复制某个人物的完整指令。十个人都属于非官方 AI 模拟；内容版本目前标为 preview。

## 路线一：复制单人物完整指令

1. 在 `downloads/mindparlor/prompts/zh/` 或 `en/` 选择人物。例如 `mao.md`、`trump.md`、`altman.md`。
2. 复制整个文件到你使用的 AI 工具的新聊天。
3. 接着直接开始聊，例如：“这周一直很忙，但回头看又没做成什么。先陪我聊聊，不要给我列计划。”

完整文件已内联该人物的语言设定、公开来源与原创示范，普通聊天不需要访问你的电脑文件。英文文件在 `en/`，中文在 `zh/`。这些文档的原始来源栏目可能保留原文标题与双语摘要。

单人物粘贴文件只装载所选的人物。要换到另一位，请另开聊天并粘贴另一份完整文件；能够读取完整 skill 文件的客户端则可以在同一聊天中切换。

## 路线二：安装统一 skill

解压 `downloads/mindparlor/mindparlor-v0.1.0.zip`，把完整 `mindparlor` 目录放进你所用客户端支持的 skills 目录。包内第一层应包含 `SKILL.md`、`catalog.json`、`references/`、`personas/` 和 `agents/`。

在识别 `~/.agents/skills` 的客户端中，Windows 路径通常为 `%USERPROFILE%\.agents\skills\mindparlor\SKILL.md`。开启新聊天后发送：

```text
$mindparlor 给我看看可以选哪些人
$mindparlor 和毛泽东聊聊：我做了很久，今天突然不想继续了
$mindparlor 和特朗普聊谈判，我不想听一套通用分析
```

也可以说“换成巴菲特，接着聊”“同一个问题，山姆怎么看”“切换英文”。编号只在刚显示人物菜单后有效。它不自动获取长期记忆；如果宿主没有保留历史，可以要求输出简短交接摘要供下次粘贴。

## 从源码构建

只需 Python 3.10+，无需安装第三方包。

```sh
python scripts/mindparlor.py list
python scripts/mindparlor.py list --lang en
python scripts/mindparlor.py prompt mao --lang zh
python scripts/mindparlor.py prompt "Sam Altman" --lang en --output private/altman.md
python scripts/mindparlor.py check
python scripts/mindparlor.py build
python -m unittest discover -s tests -v
```

默认构建到 `dist/mindparlor/`：安装 ZIP、二十份完整指令、指令合集 ZIP，以及内容 SHA256 清单。验证所有十人的文件、资料引用和输出目标后才开始写入。构建不联网，不调用模型，不采集聊天。

## 人物与使用方式

首次进入时只有一句简短模拟说明。其后自然聊天、有观点、能反驳，也能承认具体的不确定；不要求每轮输出固定格式。人物表达参考公开材料，新问题上的回答属于模拟推演。资料不是全量收录，也不自动更新。

毛泽东是依据历史文本重建的角色，不承诺口语、口音或意识复刻。凯文·沃什是具体人物，“美联储主席”只是在2026-11-03核查时的任职信息，不会因换届自动变成另一个人。塞勒是企业家与比特币倡导者，不是比特币创始人。

本项目免费，使用者已有的模型、订阅或 API 可能收费。实际效果受宿主模型和上下文影响；打包测试和独立代理试聊不能替代双语人类盲测。输入与聊天的保存方式由所用平台设置决定。

## English quick start

Copy a full file from `downloads/mindparlor/prompts/en/` into a fresh AI chat, then start talking. A selected-person prompt contains its own guide, sources and original examples; it cannot load another character's missing files. To switch with copy/paste, start another chat with the other full prompt. A file-reading skill host can use the full installation and switch characters in one chat.

Install the entire `mindparlor/` folder from the installation ZIP into the skills directory supported by your host, reopen a chat, then try `$mindparlor Show me the people` or `$mindparlor Talk with Feynman about why learning feels like memorizing names`. The project supplies no model backend; your own AI account's costs and settings still apply.

Commands above support both languages. `prompt PERSON --lang en` exports one self-contained persona; `build` validates and produces the complete package. The release is a preview with recorded checks, not a claim of measured human likeness on every host.
