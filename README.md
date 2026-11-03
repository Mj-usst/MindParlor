# MindParlor · 思想会客厅

**Choose a mind. Start a conversation.**

免费开源的中英文人物聊天 skill。选择一个有自己判断、语气和接话方式的人，聊工作、创造、历史、科技、政治或金钱。使用你已有的 AI 工具；项目不运行聊天后端。

当前版本：**0.1.0 preview**。这是依据公开材料的非官方人物模拟，不代表本人意见或授权。打包验证与试聊记录见 [验证说明](docs/mindparlor-evaluation.md)。

简体中文 | [English](README.en.md)

## 十位人物

| 人物 | 可以从这些话题开始 |
|---|---|
| 马斯克 Elon Musk | 工程、产品、太空、未来 |
| 乔布斯 Steve Jobs | 审美、创造、专注、取舍 |
| 巴菲特 Warren Buffett | 商业、时间、长期判断 |
| 纳瓦尔 Naval Ravikant | 工作、自由、财富、幸福 |
| 费曼 Richard Feynman | 好奇、学习、日常疑问 |
| 毛泽东 Mao Zedong | 调查、矛盾、历史、做事方法 |
| 特朗普 Donald Trump | 谈判、领导力、传播、国际局势 |
| 凯文·沃什 Kevin Warsh | 货币、通胀、就业、经济权衡 |
| 山姆·奥特曼 Sam Altman | AI、创业、团队、未来 |
| 迈克尔·塞勒 Michael Saylor | 比特币、数字资本、货币 |

各人物有独立的语言指南、公开来源和原创多轮示范。闲聊可以只接一句，有分歧可以直接说；不会强制把每轮都写成咨询报告。中英文分别编写。

## 最快开始

**ChatGPT、Claude 的普通聊天都可以使用完整指令版。** 无需安装 Codex，也无需运行本仓库代码。当前尚未完成这两个平台账号内的实际安装与表现验证。

1. 打开 [中文完整指令目录](downloads/mindparlor/prompts/zh/) 或 [英文目录](downloads/mindparlor/prompts/en/)。
2. 选择一个人物，例如 [毛泽东](downloads/mindparlor/prompts/zh/mao.md)、[特朗普](downloads/mindparlor/prompts/zh/trump.md)、[山姆·奥特曼](downloads/mindparlor/prompts/zh/altman.md)。
3. 复制该文件全部内容到你的 AI 工具的新聊天，接着直接说你想聊的事。

例如：“我最近很忙，但回头看又没有做成什么。先陪我聊聊，不要给我列计划。”

也可下载 [二十份完整指令合集](downloads/mindparlor/mindparlor-prompts-v0.1.0.zip?raw=true)。单人物文件只装载这一人；换人时另开聊天并粘贴另一份，或使用下方统一 skill。

## 安装统一 skill

下载 [mindparlor-v0.1.0.zip](downloads/mindparlor/mindparlor-v0.1.0.zip?raw=true)，把完整 `mindparlor` 文件夹解压到客户端支持的 skills 目录。在识别 `~/.agents/skills` 的客户端中，检查 `~/.agents/skills/mindparlor/SKILL.md` 位于正确层级，开启新聊天后输入：

```text
$mindparlor 给我看看可以选哪些人
$mindparlor 和毛泽东聊聊：我做了很久，今天突然不想继续了
$mindparlor 换成巴菲特，接着聊
```

实际安装位置取决于客户端。普通粘贴聊天不自动获得本机文件读取能力。Claude 官方也支持通过 `Customize → Skills` 上传 ZIP，需开启代码执行与文件创建；安装入口和组织权限以账号实际提供为准。参见 [Claude 官方说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude) 和本项目 [使用说明](docs/mindparlor-usage.md)。

## 自己构建与检查

Python 3.10+，标准库，无第三方依赖。

```sh
python scripts/mindparlor.py list
python scripts/mindparlor.py prompt mao --lang zh
python scripts/mindparlor.py prompt "Sam Altman" --lang en
python scripts/mindparlor.py check
python scripts/mindparlor.py build
python -m unittest discover -s tests -v
```

生成物位于 `dist/mindparlor/`：安装包、二十份单人物完整指令、指令 ZIP、带 SHA256 的清单。安装包使用明确文件白名单，不打包私有聊天与凭据。维护者发布前将生成物同步至 `downloads/mindparlor/`。

## 资料与验证

[人物原始包](skills/mindparlor/personas/)里的 `sources.md` 记录日期、定位、原创摘要与资料局限；`persona.zh.md` / `persona.en.md` 记录有依据的表达设计；示范均为原创模拟，不是历史引语。

毛泽东采用历史文本重建，不承诺复刻其日常口语或口音。凯文·沃什的现任美联储主席身份核查于2026-11-03；人格按具体姓名固定。塞勒是比特币倡导者和企业家，不是比特币创始人。资料不会自动更新。

本项目免费；你自己的 AI 账号、订阅或 API 可能收费。模型、上下文和平台设置影响实际表现与内容保存。当前 preview 不声称完成跨模型、人类双语盲测或量化相似度验证。

## 许可

原创代码、人物指南与示范使用 [MIT License](LICENSE)。原访谈、著作、第三方材料和人物相关权利不因本项目开源而转移；资料以链接与原创摘要提供。
