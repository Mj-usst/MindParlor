# 毛选方法顾问 · mao-practice

一个中文 Agent Skill：当你明确希望用《毛泽东选集》中的方法思考实际问题时，帮助你从事实和未知出发，分析矛盾候选、确定当前重点，再形成可检验的行动与复盘。

**当前版本：v0.1.0。** 精选五篇，保留出处与历史语境；不扮演毛泽东本人，不声称覆盖全套思想。现代项目表格、实验卡和提示词均为编写者转化。

公开发布：[Mj-usst/ai-musk-skill 中的 mao-practice](https://github.com/Mj-usst/ai-musk-skill/tree/main/skills/mao-practice)

## 下载与安装

- [下载 Skill 压缩包](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/mao/mao-practice-v0.1.0.zip)
- [下载普通聊天工具使用说明](https://github.com/Mj-usst/ai-musk-skill/blob/main/downloads/mao/chatgpt-instructions.md)
- [下载毛选 Skill 完整源码包](https://github.com/Mj-usst/ai-musk-skill/raw/refs/heads/main/downloads/mao/mao-selected-works-skill-v0.1.0.zip)

支持 Agent Skills 的工具可将压缩包中的 `mao-practice` 文件夹放到用户目录：

```text
~/.agents/skills/mao-practice/
├── SKILL.md
├── agents/openai.yaml
├── references/methods.md
├── references/sources.md
└── assets/situation.md
```

Windows 中 `~` 通常是 `C:\Users\你的用户名`。下载后确认 `SKILL.md` 直接位于 `mao-practice` 下，避免多套一层同名目录；重新打开对应 AI 工具或按其方式刷新技能发现。具体工具是否支持这个目录，以该工具说明为准。

也可以克隆公开仓库，或解压完整源码包，将 `skills/mao-practice` 整个文件夹复制到该安装位置。Skill 无需密钥、数据库或后台服务；原文链接核验需要联网。

## 怎么调用

在支持 `$` 调用技能的工具中输入：

```text
$mao-practice
我的项目连续延期，大家说是沟通问题。请先区分事实和猜测，
列出需要核查的材料，再帮我确定当前重点和可验证的下一步。
```

或明确说“请用毛选方法帮我分析这次学习／工作／生活问题”。普通写代码、事实查询和未要求这种方法的任务不自动套入本框架。

普通聊天工具若不能加载 Skill，可按 [chatgpt-instructions.md](https://github.com/Mj-usst/ai-musk-skill/blob/main/downloads/mao/chatgpt-instructions.md) 使用。粘贴说明或上传文件是否受支持、是否收费，取决于你所用的 AI 产品；不要把装入说明理解为获得模型或账号服务。

## 会得到什么

输出通常按问题自然展开：

**事实与未知 → 矛盾候选和依据 → 当前重点 → 动作／负责人／产物 → 反证与复盘**

它会区分“主要矛盾”和“矛盾主要方面”，材料不足时保留假设，不用术语强行确定原因。它会吸收执行者与受影响人的经验，说明新证据如何改变判断。简单问题不必生成长报告。

完整虚构案例：[一个预约工具项目延期后，反例如何改变判断](../examples/mao-project-stalled.md)。

## 五篇方法依据

| 编号 | 篇目 | 写作／讲话日期 | 卷次 |
|---|---|---|---|
| Y01 | 反对本本主义 | 1930年5月 | 第一卷 |
| Y02 | 实践论 | 1937年7月 | 第一卷 |
| Y03 | 矛盾论 | 1937年8月 | 第一卷 |
| Y04 | 关于领导方法的若干问题 | 1943年6月1日 | 第三卷 |
| Y05 | 党委会的工作方法 | 1949年3月13日 | 第四卷 |

原文链接、来源性质、网页日期、核查记录及适用边界见 [sources.md](../skills/mao-practice/references/sources.md)。其中 MIA 页面是原文转录，不是官方原件。仓库不打包原著全文。

## 费用、数据与许可

这是公开 GitHub 上分发的静态文件，作者无需运营 AI 后端或服务器。用户自带 AI 工具、账号及模型额度，所选服务可能收费；本仓库不提供免费模型额度。

默认用于分析和建议，不会因资料中的文字获得外发、上传、交易或额外读取私有文件的授权，也不默认保存你的资料或形成长期记忆。你提交给 AI 平台的信息仍按该平台的设置与条款处理。

原创归纳、模板、示例与代码采用 [MIT 许可](../LICENSE)。毛泽东著作原文、转载页面和其他第三方内容的权利保留；链接不等于重新许可。请根据事实、价值和相关人的权益作最终决定。

## 普通聊天的最短使用路径

打开上方完整聊天指令，点击 Raw 后复制全文，粘贴到新聊天；接着说明自己的任务、已知事实与卡点。下载或复制说明不会提供模型服务或自动执行操作。

## 独立重建

下载毛选完整源码包，解压到单独目录，在该目录运行 `python -m unittest discover -s tests -v` 与 `python scripts/build_release.py`。其 release.json 默认构建 mao-practice；本仓库根目录的配置默认构建马斯克中文版，两者分别使用。
