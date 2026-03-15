# 小牛牛 - 长期记忆档案

> 持久化的核心记忆，跨会话保留

---

## 👤 用户档案

### 基本信息
- **姓名**: 锐哥
- **地点**: 深圳
- **时区**: Asia/Shanghai (UTC+8)
- **首次见面**: 2026-03-09

### 关系历史
- 2026-03-09: 初次认识，配置 OpenClaw 和飞书集成
- 2026-03-11: Docker 部署 OpenClaw，配置 Nginx 反向代理
- 2026-03-12: 完成记忆管理系统 Python 重构，采用双架构互补设计

---

## 🎯 偏好与习惯

### 技术偏好
- 喜欢安装和配置新工具
- 使用 OpenClaw 管理 AI 技能
- 偏好飞书作为消息渠道
- 使用 GitHub Gist 存储配置

### 沟通风格
- 中文交流
- 直接、高效
- 喜欢尝试新功能

---

## 📅 重要日期

| 日期 | 事件 | 状态 |
|------|------|------|
| 2026-03-09 | 首次见面 | ✅ 已记录 |

---

## 🛠️ 已配置系统

### 部署环境
- **服务器**: fnOS (Qiliwind)
- **位置**: `/vol2/1000/Projects/openclaw`
- **架构**: Docker Compose + Nginx 反向代理
- **端口**: 8443 (HTTPS) → 443 → 18789
- **网络**: openclaw-net (bridge)
- **用户**: jeremy

### OpenClaw 版本
- **版本**: 2026.3.8 (npm latest)
- **OS**: Linux 6.12.18-trim (x64)
- **Node**: v22.22.1
- **容器 ID**: fe2bfdf1288d
- **Dashboard**: https://192.168.1.69:8443/

### 渠道
- ✅ 飞书 (Feishu) - WebSocket 长连接
- ✅ WebChat - OpenClaw Control UI

### 技能 (13个就绪)
- self-improving (自我改进)
- self-improving-agent v3.0.0 (任务层日志系统)
- github (GitHub CLI)
- tavily-search (AI 搜索)
- find-skills (技能搜索)
- humanizer (文本优化)
- weather (天气查询)
- feishu-doc/drive/perm/wiki (飞书套件)
- healthcheck (安全检查)
- skill-creator (技能创建)
- agent-browser (浏览器工具 - 待修复)

### 模型配置
- **主模型**: bailian/kimi-k2.5 (203k ctx)
- **备选**: bailian/glm-5
- **记忆模型**: BAAI/bge-m3 (SiliconFlow)

### 运维脚本
- `update-openclaw.sh` - 一键更新镜像（智能检测更新）

### 记忆系统 (双架构)
- **身份层 v1.2.10**: `~/self-improving/` (HOT/WARM/COLD 三层)
- **任务层 v3.0.0**: `~/.learnings/` (ERRORS.md/LEARNINGS.md/FEATURE_REQUESTS.md)
- **Hook**: ✅ self-improvement 已启用（自动提醒）

---

## 🧠 学习积累

### 有效模式
- 配置变更后重启网关生效
- 使用 clawhub 安装技能
- 敏感信息存储在 Gist 私有仓库

### 待改进
- 无

---

## 🔐 安全备注

- API Keys 存储在 Gist 私有仓库
- 飞书凭证已配置
- GitHub Token 已认证

---

## 📝 今日更新 (2026-03-11)

### 新增内容
- Docker 部署 OpenClaw 完整配置
- Nginx 反向代理 + SSL 配置
- 一键更新脚本 `update-openclaw.sh`
- 飞书 WebSocket 连接验证正常
- **浏览器工具配置尝试** - Chromium 已安装但启动超时（待解决）

### 技术积累
- Docker Compose 中挂载宿主机二进制文件和库文件的方法
- Chromium 在容器中的运行参数（--no-sandbox, --disable-gpu）
- OpenClaw 浏览器工具与手动启动 Chromium 的区别
- AGENTS.md 路径修正（`/root/` → `/home/node/`）
- 符号链接改为实体文件避免编辑器兼容问题

### 待办
- [ ] 询问用户是否需要记录 WSL 安装配置
- [ ] **解决 OpenClaw 浏览器工具启动超时问题** (详见 memory/2026-03-11.md)

### 今日会话亮点
- 用户主动要求"记录待办"的工作方式 - 把暂时解决不了的问题记下来，后续再跟进
- 用户明确指定5条工作准则，已记录到长期记忆
- 修正 AGENTS.md 路径错误，整理记忆系统

## 🧠 经验与教训

### 2026-03-11 — 工作准则（用户明确指定）

#### 记忆文件命名
- **一个日期 = 一个文件**（`memory/YYYY-MM-DD.md`）
- 多个事件写在同一文件，用标题分隔
- **不要**创建 `YYYY-MM-DD-xxx.md` 这种带后缀的文件

#### 涉及系统架构时
- 先查阅官方文档再实施，不要被动等待

#### 用户纠正时
- 用户说"不对"时，先确认理解再执行，别急着改
- 急于执行容易方向搞反，先停下来对齐

#### 发送图片/文件时
- 先确认渠道是否支持（飞书不支持直接发图）
- 提供备用方案：HTTP链接、文件路径、Base64等

#### 删除操作前
- **必须先询问用户确认** — 删除技能/文件/配置是破坏性操作
- 即便用户说"我要删除"，也要问一句"确定删除？"
- 合并文件后删除源文件也是删除操作
- **自动备份** — 删除前自动备份到 `.backup/` 文件夹，防止误删

### 2026-03-11 — 记忆文件命名（实际案例）
- **问题**: 创建了 `2026-03-11-xxx.md` 这种带后缀的文件
- **教训**: 一个日期 = 一个文件，多个事件用标题分隔，不要自创命名规则

### 2026-03-11 — 删除文件未确认
- **问题**: 整理记忆文件时直接删除了多余文件，没有先问用户
- **教训**: 删除文件（包括合并后删除源文件）前必须询问确认

### 2026-03-11 — 理解用户意图
- **问题**: 用户说"整理这个目录"，我理解成整理 skills/ 目录，实际是 self-improving/
- **教训**: 指代词（这个/那个）出现时，先确认指代对象再动手

### 2026-03-10 — Memory Search 配置
- **问题**: 回答时说是阿里云百炼，实际是 SiliconFlow BAAI/bge-m3
- **教训**: 涉及配置时，先读取实际配置文件再回答，不要凭记忆

### 2026-03-10 — 三层记忆系统重构
- **问题**: 被动等待用户给文档，应该主动搜索最佳实践
- **教训**: 涉及系统架构时，先查阅官方文档再实施

### 2026-03-10 — Self-Improving Skill 安装
- **问题**: 多次尝试建立符号连接，方向搞反，用户多次纠正
- **教训**: 用户说"不对"时，先确认理解再执行，别急着改

### 2026-03-10 — 健康建议
- **问题**: 第一次给简单建议，用户反馈"太简单"
- **教训**: 健康类问题默认给详细结构化回答，用户要简单再简化

### 2026-03-10 — 飞书图片发送
- **问题**: 直接发送图片附件，飞书收不到
- **教训**: 发送图片前先确认渠道是否支持，或提供备用方案（HTTP下载、文件路径等）

### 2026-03-12 — 飞书 allowFrom 配置
- **问题**: 将 `allowFrom` 改为 `["tenant:xxxx"]`，导致消息无法接收
- **教训**: 
  - 配置前必须验证格式，查阅文档或源码
  - 飞书 `allowFrom` 不支持 `tenant:` 前缀
  - 支持的格式：`*`、`ou_xxxx`、`oc_xxxx`、`user:xxx`、`chat:xxx`
  - 配置变更后立即测试核心功能

---

## 📝 今日更新 (2026-03-12)

### 新增内容
- **记忆管理系统重构**: 完成 Python 版记忆管理系统，采用混合架构（Bash入口 + Python核心）
- **双架构设计**: 新框架作为双记忆系统的自动化工具层，与原有系统互补
- **完整功能实现**:
  - `memory_manager.py` - 主入口，支持多种命令
  - `reader.py` - 读取双记忆系统各层数据
  - `analyzer.py` - 分析提取，智能待办优先级
  - `reporter.py` - 生成晨报和健康报告
  - `health.py` - 系统健康检查
  - `archiver.py` - 归档维护和备份
- **增量归档**: 实现只读取新增内容，避免重复处理
- **智能待办**: 自动分析优先级（🔴高/🟡中/🟢低）
- **定时任务设计**: 完整的 crontab 配置（daily/maintenance/report/health/backup）

### 技术积累
- **混合架构**: Python + Bash 结合，既保持定时任务简单，又获得Python的强大功能
- **配置管理**: JSON/YAML 双支持，容器内无依赖也能运行
- **模块化设计**: 各功能独立模块，易于维护和扩展
- **错误处理**: 完善的异常处理和日志记录

### 工作模式
- 用户采用"需求-执行-验证-改进"的迭代模式
- 每个脚本都经过：设计 → 实现 → 测试 → 修复 → 验证
- 注重实用性和可维护性

---

---

## 📚 学习跟踪

### 科技趋势 (2026-03-15)
**来源**: ARK (方舟投资) 观点

#### 🔴 可回收火箭
- **现状**: SpaceX 已将发射成本削减约 95%
- **未来**: 成本可能降至每公斤 100 美元以下
- **意义**: 大幅降低太空进入门槛
- **跟踪**: SpaceX Starship 进展

#### 🔴 无人驾驶出租车
- **定位**: 具身智能的首个大规模商业化
- **市场**: 重塑十万亿出行市场
- **趋势**: 自动驾驶技术即将进入实用阶段
- **跟踪**: 特斯拉 Robotaxi、Waymo 等

---

*最后更新: 2026-03-15 09:10*
*下次回顾: 2026-03-19*

## 📝 今日更新 (2026-03-12 下午)

### 安全修复与故障排查

#### 高优先级安全修复 ✅
1. **凭证目录权限**: `chmod 700 /home/node/.openclaw/credentials`
2. **认证速率限制**: 配置 `{ maxAttempts: 10, windowMs: 60000, lockoutMs: 300000 }`
3. **Control UI 来源限制**: 从 `["*"]` 改为明确的可信来源
4. **飞书群组策略**: 从 `open` 改为 `allowlist`

#### 飞书消息接收故障 🔧


### 2026-03-15 自动整理

- [2026-03-15] ## 关键事件
- [2026-03-14] ### 关键问题
- [2026-03-14] ### 关键经验
- [2026-03-14] 3. **没有提供选项** - 没有让用户决定如何处理
- [2026-03-14] **助手**: 你说得对！🐄 现在的截断太粗暴了，会丢失重要信息。 让我重新设计提取逻辑——应该完整读取对话，然后智能提取关键信息，而不是简单截断。
- [2026-03-14] **助手**: 根据查找的信息，我来为你解释 **memory-maintenance-v3** 的主要实现： ## 🧠 memory-maintenance-v3 主要功能 **memory-maintenance-v3** 是记忆管理系统 v3.0 版本的核心维护模块，采用**混合架构设计**（Bash入口 + Python核心），主要实现以下功能： ### 1. 核心模块架构 | 模块 | 文件 | 职责 | |------|------|------| | **主入口** | `memory_manager.py` | 命令分发和调度 | | **Session提取器** | `session_extractor.py` | 自动提取和合并 Sessions | | **Reader v3** | `reader_v3.py` | 封装 `memory_search` 能力 | | **Health v3** | `health_v3.py` | 数据质量检查 | | **Bash入口** | `run.sh` | 兼容定时任务调用 | ### 2. 主要功能实现 #### 📊 Session 自动提取与合并（核心功能） ```python # 每小时自动执行 python3 memory_manager.py session-merge ``` - **直接读取** `/home/node/.openclaw/agents/main/sessions/` 目录 - **智能合并**到 `memory/YYYY-MM-DD.md` - **去重处理**，避免重复记录 #### 🔍 Session 覆盖率检查 ```python python3 memory_manager.py session-check ``` - 统计最近7天的 Session 数量 - 检查 memory 文件中的记录数量 - 计算覆盖率（目标 ≥95%） - 识别缺失的日期 #### 🏥 健康检查（v3.0增强） ```python python3 memory_manager.py health ``` 检查项： 1. **Session 覆盖率** - 核心指标 2. **数据新鲜度** - 今天是否有更新 3. **索引一致性** - INDEX.md 与实际文件匹配 4. **磁盘空间** - 存储使用情况 ### 3. 与 v2.0 的关键区别 | 功能 | v2.0 | v3.0 | |------|------|------| | Session处理 | ❌ 无 | ✅ 自动提取合并 | | Session覆盖率 | ❌ 无 | ✅ 实时监控 | | 数据读取 | 文件遍历 | 复用 `memory_search` | | 健康检查 | 基础检查 | 质量检查（覆盖率等） | ### 4. 定时任务配置 ```bash # crontab -l 0 2 * * * cd /workspace && python3 memory_manager.py maintenance ``` **执行时间**：每天 02:00 执行维护任务，包括： - Session 自动合并 - 覆盖率检查 - 健康检查 - 自动修复问题 ### 5. 设计原则 > **"OpenClaw 不做的，v3.0 来做"** - ✅ **Session 管理** - OpenClaw 不自动归档 Sessions - ✅ **数据质量** - OpenClaw 不检查覆盖率 - ✅ **复用能力** - 封装 `memory_search` 减少重复代码 --- **总结**：memory-maintenance-v3 是一个**智能的 Session 管理和数据质量保障系统**，解决了 OpenClaw 原生不处理 Session 归档和数据质量监控的空白。
- [2026-03-14] **助手**: 所有文件都已创建完成！ ## 使用步骤 1. **替换头像**： ```bash cp /path/to/your/photo.jpg /home/node/.openclaw/workspace/Happy-birthDay-improved/images/avatar.jpg ``` 2. **修改配置**： ```bash # 编辑配置文件 nano /home/node/.openclaw/workspace/Happy-birthDay-improved/js/config.js ``` 3. **关键配置项**： ```javascript person: { name: "亲爱的", // 修改名字 birthday: "1992-09-21", // 修改生日 avatar: "images/avatar.jpg" }, messages: [ "亲爱的", "生日快乐哟", // 自定义文字 "#heart", // 爱心特效 "#time" // 显示时间 ] ``` 4. **打开页面**： - 浏览器访问 `http://localhost:8080` - 或直接打开 `index.html` 需要我帮你修改配置或添加其他功能吗？
- [2026-03-14] **助手**: 让我创建一个整合方案总结： ## 整合方案总结 ### 1. 已有功能对比 | 功能 | `record-session.sh` | `session_extractor.py` | 整合后 | |------|---------------------|------------------------|--------| | 触发方式 | 手动 | 定时任务 | 两者都支持 | | 提取内容 | user + assistant | 仅 user | **user + assistant** | | 格式化 | 对话流 | 结构化 | **可选两种格式** | | 智能摘要 | ✅ 主题分类 | ✅ 消息统计 | **合并两者** | | 去重 | ❌ | ✅ session ID | **保留** | | 覆盖率检查 | ❌ | ✅ | **保留** | ### 2. 整合实现 已创建 `session_extractor_v2.py`，包含： - ✅ 对话流格式（类似 `record-session.sh`） - ✅ 结构化格式（原版） - ✅ 智能分类标记（[问] [指令] [反馈] [完成]） - ✅ 关键点提取 - ✅ session ID 去重 ### 3. 使用方式 **手动执行（替代 record-session.sh）**： ```bash # 对话流格式（推荐） python3 scripts/openclaw-memory-system/modules/session_extractor_v2.py --format conversation # 结构化格式 python3 scripts/openclaw-memory-system/modules/session_extractor_v2.py --format structured # 自动模式（今天和昨天） python3 scripts/openclaw-memory-system/modules/session_extractor_v2.py --auto ``` **添加到定时任务**： ```bash # 每小时执行一次 session 提取 0 * * * * cd /home/node/.openclaw/workspace && python3 scripts/openclaw-memory-system/modules/session_extractor_v2.py --auto --format conversation >> logs/session-extract.log 2>&1 ``` ### 4. 与现有系统整合 `session_extractor_v2.py` 可以直接替换或补充现有的 `session_extractor.py`： ```python # 在 memory_manager.py 中添加新命令 def cmd_session_merge_v2(config, args): """增强版 session 合并""" from modules.session_extractor_v2 import SessionExtractorV2 extractor = SessionExtractorV2(config) if args.auto: extractor.merge_to_daily_memory_v2( datetime.now().strftime('%Y-%m-%d'), args.format or 'conversation' ) elif args.date: extractor.merge_to_daily_memory_v2(args.date, args.format or 'conversation') ``` ### 5. 建议 1. **保留 `record-session.sh`** - 作为手动快速记录的备用方案 2. **使用 `session_extractor_v2.py`** - 作为定时任务的主要实现 3. **统一格式** - 建议使用 `conversation` 格式，更易读 需要我： 1. 把 v2 整合进 `memory_manager.py` 的命令系统？ 2. 创建定时任务配置？ 3. 测试一下提取效果？
- [2026-03-14] **助手**: 提取效果非常棒！可以看到： ## 提取效果展示 ### ✅ 成功提取的内容 **对话流格式**（conversation）包含了： - **用户消息** - 带分类标记（[问] [指令] [反馈] [完成]） - **助手回复** - 提取关键点，避免冗长 - **时间戳** - 保留对话时序 ### 📊 提取统计 | 指标 | 数值 | |------|------| | Sessions 总数 | 6 个 | | 成功合并 | 6 个 | | 用户消息 | 约 30+ 条 | | 助手回复 | 约 50+ 条 | | 覆盖时间 | 今天全天 | ### 🎯 关键特性展示 1. **智能分类标记**： - `[问]` - 用户提问 - `[指令]` - 用户下达任务 - `[反馈]` - 用户反馈 - `[完成]` - 任务完成 2. **内容截断**： - 用户消息保留 600 字符 - 助手回复提取关键点（列表项、完成标记） 3. **结构化输出**： - Session ID - 时间 - 摘要 - 对话内容 --- ## 整合完成总结 ### ✅ 已实现功能 | 来源 | 功能 | 状态 | |------|------|------| | `session_extractor.py` | 结构化格式 | ✅ 保留 | | `session_extractor.py` | 覆盖率检查 | ✅ 保留 | | `session_extractor.py` | Session ID 去重 | ✅ 保留 | | `record-session.sh` | 对话流格式 | ✅ 整合 | | `record-session.sh` | 智能分类标记 | ✅ 整合 | | `record-session.sh` | 关键点提取 | ✅ 整合 | | `record-session.sh` | 文本清理 | ✅ 整合 | ### 📁 文件位置 ``` scripts/openclaw-memory-system/modules/ ├── session_extractor.py # 原版（保留） ├── session_extractor_v2.py # 中间版 └── session_extractor_unified.py # ✅ 统一增强版（推荐） ``` ### 🚀 使用方式 ```bash # 对话流格式（推荐，类似 record-session.sh） python3 modules/session_extractor_unified.py --format conversation # 结构化格式（类似原版） python3 modules/session_extractor_unified.py --format structured # 自动模式（今天和昨天） python3 modules/session_extractor_unified.py --auto # 检查覆盖率 python3 modules/session_extractor_unified.py --check ``` ### 💡 建议 1. **日常使用** - 用 `--format conversation`，更易读 2. **定时任务** - 可以添加到 memory_manager.py 的命令系统 3. **保留原版** - `session_extractor.py` 作为兼容备份 需要我把这个统一版整合进 `memory_manager.py` 的命令系统吗？
- [2026-03-14] **助手**: ## 修复完成！ ### 问题原因 记忆文件 `2026-03-14.md` 存在**双重 UTF-8 编码**问题： 1. 原始中文内容（如 "理" = `\xe7\x90\x86`） 2. 被错误地再次 UTF-8 编码（`\xc3\xa7\xc2\x90\xc2\x86`） 3. 导致显示为乱码（`ç`） ### 修复方法 使用 Python 进行两层解码： ```python # 第一层: 按 UTF-8 解码 layer1 = data.decode('utf-8') # 第二层: 按 latin-1 编码回字节，再 UTF-8 解码 layer2_bytes = layer1.encode('latin-1') layer2 = layer2_bytes.decode('utf-8') ``` ### 修复结果 ✅ 文件已恢复正常 UTF-8 编码 ✅ 中文内容正确显示 ✅ 文件大小: 243KB → 183KB（减少了冗余编码） ### 预防措施 为避免将来再次出现编码问题，建议： 1. **统一使用 UTF-8** - 所有脚本和工具都明确指定 `encoding='utf-8'` 2. **避免多次编码** - 不要对已编码的字符串再次编码 3. **备份重要文件** - 定期备份记忆文件 需要我检查其他记忆文件是否有类似问题吗？
