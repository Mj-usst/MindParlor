# 马斯克式决策顾问

一个中文 AI 决策 Skill，用来梳理个人现状、职业选择和创业方向。它从马斯克公开资料中的第一性原理与工程方法获得启发，再结合项目编写的现金流、选项比较和小规模验证工具，帮助你形成可检验的判断。

这是**非官方的方法模拟**，与埃隆·马斯克及其公司无关联，也不代表本人意见。它使用精选公开来源，没有收录人物的全量知识，不保证任何结果，也不默认拥有跨聊天的长期记忆。

## 最简单的用法

1. 打开[完整聊天指令](https://github.com/Mj-usst/ai-musk-skill/blob/main/downloads/chatgpt-instructions.md)，点击 Raw 后复制全文，或下载该文件。
2. 打开 ChatGPT 普通聊天，粘贴完整内容。
3. 接着描述你的现状和问题，例如：

   > 我在制造业做了五年，想比较继续上班、转行和业余创业。每月必要支出约8000元，存款约10万元，需要顾及家庭，每周可拿出6小时。请区分事实和假设，给出一个可逆的下一步，以及什么证据会改变你的建议。

也可以用支持 Skills 的客户端安装下方 Skill。项目自身不运行服务器、不调用作者的模型 API，**作者无需承担后端或模型调用费用；使用者自己的 AI 账号、订阅或 API 可能收费**。

## 安装到 Codex

项目仓库：[Mj-usst/ai-musk-skill](https://github.com/Mj-usst/ai-musk-skill)。

在支持 `$skill-installer` 的 Codex 会话中发送：

```text
$skill-installer 请从 https://github.com/Mj-usst/ai-musk-skill/tree/main/skills/musk-decision 安装 musk-decision
```

手动安装时，[下载 `musk-decision-v0.1.0.zip`](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/musk-decision-v0.1.0.zip)，将其中整个 `musk-decision` 文件夹解压到：

```text
~/.agents/skills/musk-decision/
```

Windows 对应 `%USERPROFILE%\.agents\skills\musk-decision\`。检查 `SKILL.md` 位于该目录的第一层，随后开启新的 Codex 会话，发送：

```text
$musk-decision 帮我比较当前工作、转行和业余创业，先分析已有信息。
```

独立 Skills 面向支持它的桌面应用、CLI 或 IDE 客户端；ChatGPT 网页和手机端的插件分发属于另一套发布流程。下载本项目 ZIP 不会自动安装 ChatGPT 插件，也不意味着网页聊天能读取电脑中的 `SKILL.md`。参见[官方 Skills 说明](https://learn.chatgpt.com/docs/build-skills)。

## 在 ChatGPT 使用

普通聊天按“最简单的用法”粘贴完整指令即可。若你的账号支持创建自定义 GPT，可按 [ChatGPT 配置说明](docs/chatgpt-setup.md)设置。功能入口、知识文件和共享权限以账号实际提供的能力为准。

完整的[虚构示例对话](examples/career-direction.md)展示了事实、未知量、假设、推荐、反证、验证行动和复盘之间的关系。

## 它会怎样帮助你

它会先辨明约束和关键未知量，比较现状、候选方向与过渡路径，再给出有条件的推荐、取舍、验证行动和复盘条件。金额、时限与成功门槛是可调整建议，应按你的责任与承受能力共同修改。它不会把高强度工作或创业设为每个人的默认目标。

人物来源、通用决策工具和模型判断分别标识；近期信息需要联网核实，无法联网时应说明未知，不编造引文或核查结果。原始来源见 [sources.md](skills/musk-decision/references/sources.md)。

## 隐私与权限

使用时只提供与决策有关的资料。Skill 不附带独立存储、上传或外部执行服务；聊天内容仍受你所用 AI 平台的数据与记忆设置影响。请勿把身份证号、密码、客户资料等无关信息写进输入。

个人输入与导出结果可放在本地 `private/` 或 `decisions/`，这些目录已被 Git 忽略并被打包脚本排除。提交前仍应检查改动，尤其不要把真实个人现状直接改进公开模板。发送消息、交易、辞职或提交材料等实际行动，需要你另行决定和授权。

## 自己构建

需要 Python 3.10 或更新版本，无第三方依赖。在仓库根目录运行：

```sh
python -m unittest discover -s tests -v
python scripts/build_release.py
```

生成在 `dist/`：

- `musk-decision-v0.1.0.zip`：可安装 Skill 文件夹及许可。
- `ai-musk-skill-v0.1.0.zip`：公开仓库文本源码。
- `chatgpt-instructions.md`：已内联方法、来源和输入模板的独立指令。

发布的三个文件位于 [downloads/](https://github.com/Mj-usst/ai-musk-skill/tree/main/downloads)。维护者修改 Skill 或来源后，重新构建，将 `dist/` 中这三个文件复制到 `downloads/` 再提交；源码 ZIP 的公开路径白名单不包含 `downloads/`，避免递归打包旧分发包。

打包使用公开路径和文本扩展名白名单，排除任意层级的点号隐藏路径（仅保留根目录 `.gitignore`）、私人目录、缓存、符号链接、Windows Junction 等重解析点、生成物和二进制文件。遍历时直接跳过这些目录；输入根路径、输出目录及其祖先、已有输出目标也不能经过链接或重解析点。版本或 Skill 引用缺失时，先报错再停止，不创建输出目录。可用 `--root` 和 `--output-dir` 指定其他输入、输出路径。

## 许可

原创项目内容采用 [MIT License](LICENSE)。链接的第三方资料仍由原权利人持有，不因本项目许可而重新授权。
