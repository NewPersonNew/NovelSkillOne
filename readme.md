# 📚 NovelSkillOne

> 基于本地大模型（Qwen2.5）的 AI 长篇小说创作系统，支持从世界观设定、分卷规划、大纲生成到逐章创作、一致性校验的全流程。目标驾驭 **500 万～1000 万字** 的超长篇创作。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5--14B-green)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ✨ 功能特性

- **项目全生命周期管理**：创建 / 删除项目，项目名即小说标题。
- **精细化设定工坊**：支持题材、文风、故事基调、主角背景、女主、反派、家人、世界观特点等丰富字段，表单式编辑，安全保存。
- **分卷规划**：根据目标字数自动计算卷数（每卷约 30 万字），每卷包含摘要、关键事件、世界观变化、卷间衔接。
- **卷级大纲生成**：先为每卷独立生成章节大纲，再合并为全书大纲，确保结构清晰、衔接自然。
- **沉浸式编辑器**：按章生成正文，实时展示角色状态、活跃伏笔、近期事实等上下文。
- **结构化记忆层**：SQLite 存储事实、承诺（伏笔）、角色档案；ChromaDB 向量检索历史章节，保障长程一致性。
- **智能 Agent**：一致性检查（防止吃书）、伏笔分析与回收提醒。
- **本地化运行**：所有模型与数据均在本机，无需联网，保护创作隐私。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────┐
│           UI 层 (CustomTkinter)             │
│  项目看板 / 设定工坊 / 大纲设计 / 编辑器 / Agent │
├─────────────────────────────────────────────┤
│           业务逻辑层 (core/ agents/)         │
│  设定构建 / 大纲生成 / 章节生成 / 一致性检查   │
├─────────────────────────────────────────────┤
│        记忆与上下文层 (memory/ orchestration/) │
│  SQLite 事实库 / ChromaDB 向量库 / 上下文组装  │
├─────────────────────────────────────────────┤
│         基础设施层 (infrastructure/)         │
│   LLM 客户端 / 文件管理 / 配置管理            │
└─────────────────────────────────────────────┘
```

---

## 🖥️ 环境要求

- **操作系统**：Windows 10/11（推荐）、macOS、Linux
- **Python**：3.10 或更高
- **显存**：≥ 12GB（推荐 16GB，如 RTX 4070 Ti）
- **Ollama**：已安装并运行
- **模型**：
  - 主模型：`qwen2.5:14b`（或 `qwen2.5:14b-q6_K`）
  - 嵌入模型：`nomic-embed-text`（用于向量检索）

---

## 🚀 安装与启动

### 1. 克隆项目

```bash
git clone https://github.com/yourname/NovelSkillOne.git
cd NovelSkillOne
```

### 2. 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate     # macOS/Linux
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 拉取 Ollama 模型

```bash
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

### 5. 配置文件

确保 `config/settings.yaml` 存在并正确配置：

```yaml
llm:
  model: "qwen2.5:14b"
  base_url: "http://localhost:11434"
  temperature: 0.85
  max_tokens: 4096
  timeout: 120

embedding:
  model: "nomic-embed-text"
  base_url: "http://localhost:11434"

paths:
  data_root: "./data"
  prompts_root: "./config/prompts"

generation:
  chunk_size: 3000
  retrieval_top_k: 5
```

### 6. 启动应用

```powershell
python -m app.main
```

---

## 📖 使用指南

### 创建新项目

1. 点击侧边栏 **“➕ 新建项目”**。
2. 填写项目名称（即小说标题）、目标字数、题材、文风、故事基调、主角信息等。
3. 点击 **“🚀 创建项目”**，系统将调用 LLM 生成包含分卷规划的完整设定。

### 生成大纲

1. 切换到 **“📋 大纲设计”**。
2. 点击 **“🚀 生成大纲”**，系统会按卷逐一生成章节大纲并合并。
3. 可点击 **“✏️ 编辑”** 手动调整，保存后生效。

### 逐章创作

1. 切换到 **“✍️ 编辑器”**。
2. 选择章节号，点击 **“📖 加载”** 查看已有内容，或点击 **“🚀 生成”** 创建新草稿。
3. 右侧面板会显示当前章节的上下文（角色状态、活跃伏笔、近期事实）。
4. 修改满意后，点击 **“🔒 定稿”** 将内容写入记忆库，并更新角色状态与伏笔。

### 一致性检查与伏笔分析

切换到 **“🧠 智能Agent”**，可运行：
- **一致性检查**：扫描最新章节，检测与已有事实的冲突。
- **伏笔分析**：查看活跃伏笔的回收建议。

---

## 📂 项目结构

```
NovelSkillOne/
├── app/                          # UI 层
│   ├── main.py                   # 应用入口
│   ├── state.py                  # 全局状态
│   ├── styles.py                 # 字体与颜色常量
│   ├── components/               # 可复用组件
│   │   └── sidebar.py
│   └── pages/                    # 页面
│       ├── dashboard.py
│       ├── project_init.py
│       ├── setting_workshop.py
│       ├── outline_designer.py
│       ├── editor.py
│       └── agents.py
├── core/                         # 核心业务逻辑
│   ├── setting_builder.py
│   ├── outline_generator.py
│   └── chapter_generator.py
├── memory/                       # 记忆层
│   ├── db_manager.py             # SQLite 事实/承诺/角色
│   ├── state_tracker.py          # 旧版状态追踪
│   └── vector_retriever.py       # ChromaDB 向量检索
├── orchestration/                # 编排层
│   ├── workflow.py
│   └── context_assembler.py
├── agents/                       # 智能 Agent
│   ├── consistency_agent.py
│   └── foreshadowing_agent.py
├── infrastructure/               # 基础设施
│   ├── llm_client.py
│   └── file_manager.py
├── config/                       # 配置与提示词
│   ├── settings.yaml
│   └── prompts/
│       ├── setting_builder.yaml
│       ├── outline_generator.yaml
│       ├── chapter_outline.yaml
│       └── chapter_draft.yaml
├── data/                         # 运行时数据（自动生成）
│   └── {项目名}/
│       ├── settings.json
│       ├── outline.json
│       ├── chapters/
│       ├── canon.db
│       └── chroma_db/
├── requirements.txt
└── README.md
```

---

## 🗺️ 开发路线图

- [x] 基础设施：LLM 客户端、文件管理、配置管理
- [x] 项目初始化与设定生成（含分卷规划）
- [x] 设定工坊（表单式编辑）
- [x] 大纲设计（卷级生成 + 合并）
- [x] 编辑器（章节生成、定稿、上下文展示）
- [x] 结构化记忆：SQLite + ChromaDB
- [x] 智能 Agent：一致性检查、伏笔分析
- [ ] 项目看板完善
- [ ] 批量生成全部章节
- [ ] 导出为 TXT / EPUB / Markdown
- [ ] 角色关系图谱可视化
- [ ] 快照与分支管理
- [ ] 多模型路由（不同任务使用不同 LLM）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request。在提交 PR 前，请确保：
- 代码通过基本测试；
- 遵循现有代码风格；
- 更新相关文档。

---

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Ollama](https://ollama.com/) 提供本地模型运行环境
- [Qwen](https://qwenlm.github.io/) 提供强大的中文大模型
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 提供现代化 GUI 组件
- [ChromaDB](https://www.trychroma.com/) 提供向量检索能力

---

> **开始你的百万字创作之旅吧！** 🚀****