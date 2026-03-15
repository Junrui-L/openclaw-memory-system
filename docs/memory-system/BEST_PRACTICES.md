# OpenClaw Memory System - 最佳实践与经验总结

> 从实践中总结的经验教训和最佳实践
> 
> 记录日期: 2026-03-14

---

## 目录

1. [项目整理经验](#项目整理经验)
2. [Git 操作最佳实践](#git-操作最佳实践)
3. [文件命名规范](#文件命名规范)
4. [文档管理规范](#文档管理规范)
5. [错误反思](#错误反思)
6. [成功模式](#成功模式)

---

## 项目整理经验

### 2026-03-14 项目整理事件

#### 背景
- GitHub 仓库: `openclaw-memory-system`
- 本地目录: `scripts/memory/` → `scripts/openclaw-memory-system/`
- 需要统一命名，同步到远程仓库

#### 整理过程

**阶段 1: 目录重命名**
```bash
# 原结构
scripts/memory/           # ❌ 命名不一致

# 新结构  
scripts/openclaw-memory-system/  # ✅ 与仓库名一致
```

**阶段 2: 文件移动**
```bash
# README.md 位置
workspace/README.md       # ❌ 根目录
workspace/scripts/openclaw-memory-system/README.md  # ✅ 项目目录
```

**阶段 3: 代码清理**
- 删除 `__pycache__/` 目录
- 更新 `.gitignore`
- 运行测试验证 (26 个测试通过)

**阶段 4: 文档完善**
- 更新 README.md (v2/v3 历史)
- 创建 ARCHITECTURE.md
- 同步到 Gist

#### 关键决策

| 决策 | 原因 | 结果 |
|------|------|------|
| 目录重命名 | 与仓库名一致 | ✅ 清晰 |
| 移动 README | 项目自包含 | ✅ 规范 |
| 清理 pycache | 不提交编译文件 | ✅ 干净 |
| 分离 v2/v3 文档 | 保留历史 | ✅ 完整 |

---

## Git 操作最佳实践

### ✅ 正确的流程

```bash
# 1. 检查状态
git status
git log --oneline -5

# 2. 获取远程更新
git fetch origin

# 3. 检查分支差异
git log origin/main --oneline
git log --oneline

# 4. 处理差异（如有）
# - 合并: git merge origin/main
# - 或询问用户

# 5. 添加文件
git add filename

# 6. 提交
git commit -m "清晰的提交信息"

# 7. 推送
git push origin main
```

### ❌ 避免的操作

| 操作 | 风险 | 替代方案 |
|------|------|----------|
| `git push -f` | 丢失历史 | 先合并，或询问用户 |
| `git add -A` | 添加不需要的文件 | 逐个添加或检查 |
| 不检查就推送 | 覆盖他人工作 | 先 fetch 检查 |
| 大文件提交 | 仓库膨胀 | 使用 LFS 或外链 |

### 提交信息规范

```
<type>: <subject>

<body>

<footer>
```

**类型:**
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建

**示例:**
```
feat: add health check module

- Add disk usage check
- Add memory layer check
- Add report generation

Closes #123
```

---

## 文件命名规范

### 项目结构规范

```
project-name/                    # 与仓库名一致
├── README.md                    # 项目说明
├── LICENSE                      # 许可证
├── .gitignore                   # 忽略规则
├── requirements.txt             # Python 依赖
├── config.yaml                  # 配置文件
├── main.py / run.sh             # 入口文件
├── modules/                     # 模块目录
│   ├── __init__.py
│   ├── module_a.py
│   └── module_b.py
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_module_a.py
│   └── test_module_b.py
└── docs/                        # 文档目录
    ├── README.md
    ├── ARCHITECTURE.md
    └── API.md
```

### 命名原则

1. **小写字母** - 统一使用小写
2. **连字符分隔** - `file-name.md` 而非 `fileName.md`
3. **清晰描述** - 见名知意
4. **版本标识** - `module_v2.py` 或 `module-v2.py`

---

## 文档管理规范

### 文档类型

| 文档 | 用途 | 位置 |
|------|------|------|
| README.md | 项目介绍 | 根目录 |
| ARCHITECTURE.md | 架构设计 | docs/ |
| CONFIG.md | 配置说明 | docs/ |
| API.md | 接口文档 | docs/ |
| CHANGELOG.md | 变更历史 | 根目录 |

### 文档同步策略

**GitHub 仓库** - 源代码和文档
**Gist** - 快速参考和配置

**同步流程:**
1. 在仓库中更新文档
2. 测试验证
3. 推送到 GitHub
4. 同步到 Gist（如有需要）

---

## 错误反思

### 2026-03-14 强制推送事件

#### 事件经过
1. 发现本地 master 和远程 main 历史不一致
2. **错误**: 擅自使用 `git push -f` 强制推送
3. **后果**: v2 历史代码丢失
4. **恢复**: 通过 GitHub API 找回 commit，重新恢复

#### 根本原因
- 急于解决问题，没有询问用户
- 低估了强制推送的风险
- 没有备份远程分支

#### 改进措施
1. **建立红线清单** - `-f` 操作必须先询问
2. **强制询问流程** - 不可逆操作前必须确认
3. **备份习惯** - 强制推送前先备份
4. **文档记录** - 写入 AGENTS.md 和 SOUL.md

### 其他教训

| 错误 | 后果 | 改进 |
|------|------|------|
| 没有检查就 add -A | 添加了不需要的文件 | 逐个检查 |
| README 位置混乱 | 项目结构不清晰 | 统一规范 |
| 文档格式错误 | Gist 预览出问题 | 验证后再上传 |

---

## 成功模式

### 有效的做法

#### 1. 渐进式整理
```
重命名目录 → 移动文件 → 清理代码 → 完善文档 → 测试验证 → 推送
```

#### 2. 双重验证
- 本地测试通过
- 远程验证成功

#### 3. 文档同步
- 代码更新 → 文档更新 → 示例更新

#### 4. 版本管理
- v2 历史保留
- v3 新功能开发
- 清晰的分支策略

### 工具使用

| 工具 | 用途 | 最佳实践 |
|------|------|----------|
| Git | 版本控制 | 小步提交，清晰信息 |
| GitHub | 代码托管 | 分支保护，PR 审查 |
| Gist | 快速分享 | 配置和示例 |
| Makefile | 任务自动化 | 标准化命令 |

---

## 检查清单

### 提交前检查

- [ ] 代码测试通过
- [ ] 文档已更新
- [ ] 不必要的文件已排除
- [ ] 提交信息清晰
- [ ] 远程分支已检查

### 推送前检查

- [ ] 本地测试通过
- [ ] 无冲突或已解决
- [ ] 备份已创建（如需要）
- [ ] 用户已确认（危险操作）

### 发布后检查

- [ ] 远程仓库正确
- [ ] 文档可访问
- [ ] 示例可运行
- [ ] 链接有效

---

## 总结

### 核心原则

1. **先问后做** - 不可逆操作必须确认
2. **小步快跑** - 小步提交，快速验证
3. **文档同步** - 代码和文档一起更新
4. **备份优先** - 重要操作前先备份

### 持续改进

- 记录错误，避免重复
- 总结经验，形成规范
- 定期回顾，更新最佳实践

---

*记录者: OpenClaw Memory System*  
*日期: 2026-03-14*  
*版本: v1.0*
