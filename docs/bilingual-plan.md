# Bilingual Skill Implementation Plan

> For agentic workers: use skill-creator and writing-skills for content; use test-driven development for release code and independent forward testing before publication.

**Goal:** 提供完整中英文技能，并保留中文兼容入口。
**Architecture:** 两个独立 Skill，共用按语言配置的标准库构建器。
**Tech Stack:** Markdown、YAML、JSON、Python 3.10+ 标准库。
**Spec:** [bilingual-design.md](bilingual-design.md)

- [x] 翻译并校验英文指令、参考资料、模板、README、说明和示例。
- [x] 先写并运行多语言打包失败测试，扩展配置，再运行原有与新增测试。
- [x] 校验语言版相对引用、分别打包和独立指令；检查无法借配置越界读取或写出。
- [x] 独立试答与整体审查，修复重要问题并记录验证范围。
- [x] 更新中文入口，准备分发文件及远端内容核验流程。

Review focus: 中文兼容性、英文是否完整独立、来源归因是否一致、配置文件路径边界、个人约束与可调整建议。
