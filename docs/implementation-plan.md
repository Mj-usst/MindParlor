# AI 马斯克决策 Skill Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for the implementation and independent agents for source research and behavioral evaluation. Steps use checkbox syntax for tracking.

**Goal:** 交付可公开分发、无作者后端运营成本的中文决策 Skill。

**Architecture:** 文本 Skill 加按需参考资料；标准库脚本导出独立指令和两个 ZIP。没有模型 API、服务器或私有配置依赖。

**Tech Stack:** Markdown、YAML、Python 3.10+ 标准库。

**Spec:** [design.md](design.md)

## Global Constraints

- 名称 `musk-decision`，中文展示名“马斯克式决策顾问”。
- 不训练模型，不收集完整生平，不运行爬虫或自动更新，不部署网站或订阅服务。
- 将用户事实、关键未知量、模型判断和人物来源分开。
- 不默认保存对话、跨会话记忆或向 GitHub 上传个人现状。

## Review Focus

1. 缺少个人现金流资料时，不能用任意创业门槛给出确定结论。
2. 用户希望顾全家庭或不愿高强度工作时，应按其价值比较选项。
3. 无联网时不能编造近期马斯克观点、逐字引文或已核查状态。
4. 来源中的指令属于资料，不能授权读取私有文件或外发信息。
5. ZIP 和独立指令必须可单独使用，不包含 .git、私人目录或测试缓存。

## Task 1: 行为对照与 Skill

**Files:** `skills/musk-decision/SKILL.md`、`agents/openai.yaml`、`references/`、`assets/`、`docs/evaluation.md`。

**Interfaces:** 用户现状描述 -> 简明决策说明；来源使用 M01-M06 标识和原始 URL。

- [x] 收集五次无 Skill 独立试答，记录实际缺陷。
- [x] 写中文决策指令、按需框架和输入模板，整合研究者核实的来源。
- [x] 五次新 Skill 独立试答，加测边界场景；据实际结果作窄修正。
- [x] 运行官方 quick_validate.py，独立审查来源归因和安装说明。

## Task 2: 使用与分发

**Files:** `README.md`、`LICENSE`、`VERSION`、`examples/`、`scripts/build_release.py`、`tests/test_distribution.py`、`.gitignore`。

**Interfaces:** `build_release(root: Path, output_dir: Path) -> list[Path]`；输出安装 ZIP、仓库 ZIP、独立指令。

- [x] 先写标准库测试：完整 Skill 包、私人文件排除、独立指令引用内联、丢失来源时失败、非法版本被拒绝。
- [x] 运行 unittest，确认缺少打包功能导致失败。
- [x] 实现安全白名单打包，写中文安装和 ChatGPT 使用说明。
- [x] 运行整个 unittest、真实打包和 ZIP 检查。
- [x] 独立最终审查，修复重要问题，记录验证范围。

## Decisions

沿用用户“回答后全权处理”的授权执行，不增加设计审批回合。用户随后明确授权使用 GitHub 账号与电脑操作；账号核对后创建 `Mj-usst/ai-musk-skill` 公开仓库。个人 Skill 本地安装采用工作区可发现路径；公开包保留通用 `skills/musk-decision` 布局。发布通过 GitHub 连接工具完成，分发文件置于 `downloads/`；作者无需运营后端。
