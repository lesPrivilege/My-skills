---
name: md-to-cards
description: >
  Markdown 笔记转 MiniSRS 闪卡。调用 LLM 语义提取 Q&A 对，输出 MiniSRS 可直接导入的 JSON。
  Slash command: /md-to-cards <file.md> [--deck name] [--provider deepseek|openai|local].
---

# md-to-cards — Markdown → MiniSRS 闪卡生成

从 `.md` 文件提取 Q&A 卡片对，输出 MiniSRS 格式 JSON。工具位于 `<repo>/md-to-cards/`。

## 快速用法

```bash
cd <repo>/md-to-cards

# 基本（默认 DeepSeek，最便宜）
python3 -m md_to_cards <file.md> --deck "牌组名"

# 指定 provider
python3 -m md_to_cards notes.md --provider deepseek
python3 -m md_to_cards notes.md --provider openai --model gpt-4o-mini
python3 -m md_to_cards notes.md --provider local --model qwen2.5

# 追加到已有 JSON
python3 -m md_to_cards more.md --deck "线性代数" --output cards.json --append

# 批量 glob
python3 -m md_to_cards ~/Reading/notes/*.md --output <repo>/mini-srs/cards.json
```

## API Provider 选择（token plan 兼容）

所有 provider 走 OpenAI Chat Completions 格式（`/v1/chat/completions`）。按成本排序：

| Provider | 模型 | 成本 | 备注 |
|---|---|---|---|
| `local` | qwen2.5 | 免费 | Ollama 本地运行，无 API 费用 |
| `deepseek` | deepseek-chat | ~$0.14/M tokens | **推荐默认**，性价比最高 |
| `mimo` | mimo-v2.5 | 1x credit | MiMo token plan，OpenAI 兼容格式 |
| `openai` | gpt-4o-mini | ~$0.15/M tokens | 质量略高，价格接近 |
| `openrouter` | deepseek/deepseek-chat | 浮动 | 聚合平台，按需 |

**不建议用 Pro 模型（gpt-4o, claude-sonnet）**——卡片提取是结构化 JSON 输出任务，小模型完全够用，Pro 模型是过度配置。

### 环境变量

```bash
# .env 或 shell profile
export DEEPSEEK_API_KEY=sk-xxx    # 推荐
export OPENAI_API_KEY=sk-xxx      # 可选
# local provider 无需 key
```

## 工作流

### 1. 触发条件

用户说以下任意一句时触发：
- "把这个笔记转成卡片"
- "从 md 提取 flashcard"
- "/md-to-cards"
- "导入笔记到 MiniSRS"

### 2. 执行步骤

```
1. 确认输入文件路径
2. 确认牌组名（默认用文件名）
3. 运行 python3 -m md_to_cards <file> --deck <name> --output <path>
4. 输出文件交给用户，告知导入方式
```

### 3. 导入 MiniSRS

输出的 JSON 直接导入 MiniSRS：
- 打开 MiniSRS → Import JSON → 选文件
- 或手动复制到 `localStorage`（开发者模式）

## 文件结构

```
<repo>/md-to-cards/
├── md_to_cards/
│   ├── __main__.py       # CLI 入口
│   ├── cli.py            # argparse
│   ├── config.py         # provider 配置
│   ├── reader.py         # .md 读取 + h2 分块
│   ├── extractor.py      # httpx 调 LLM + JSON 解析
│   ├── schema.py         # MiniSRS 输出格式 + system prompt
│   └── writer.py         # JSON 输出 + append
├── .env.example
└── pyproject.toml
```

## LLM 分块策略

- 按 `## ` (h2) 标题拆分 markdown 为 chunks
- 每个 chunk 独立调用 LLM（避免上下文过长导致遗漏）
- 无 h2 标题的文件整体发送
- 单个 chunk 超过 4000 字符时按段落二次拆分

## System Prompt（内置）

```
You are a flashcard generator. Given markdown study notes, extract
question-answer pairs suitable for spaced repetition review.

Rules:
- Each card tests ONE atomic concept
- Front: a clear, specific question
- Back: a concise, complete answer
- Prefer "what/how/why" questions over "define X"
- Output ONLY valid JSON array
```

## 依赖

- Python 3.11+
- `httpx`（已包含在 pyproject.toml）
- 无需额外安装：`cd <repo>/md-to-cards && pip3 install -e .`

## 注意事项

- 不做 .apkg 解析
- 不做卡片去重（LLM 输出可能有重复，用户手动删）
- 不做 SM-2 调度（那是 MiniSRS 的事）
- 不做 GUI
