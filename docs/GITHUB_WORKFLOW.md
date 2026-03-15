# GitHub 推送完整流程

> 标准操作流程，避免数据丢失

---

## 前置检查清单

### 1. 检查远程仓库
```bash
git remote -v
git branch -a
```

### 2. 检查本地状态
```bash
git status
git log --oneline -5
```

### 3. 获取远程最新状态
```bash
git fetch origin
```

---

## 分支不一致处理

### 情况 A：本地和远程分支相同（正常推送）
```bash
git push origin main
```

### 情况 B：本地 master，远程 main（不同名）
```bash
# 方案 1：推送本地 master 到远程 main
git push origin master:main

# 方案 2：重命名本地分支
git branch -m main
git push origin main
```

### 情况 C：历史不一致（⚠️ 危险）
**必须先询问用户！**

```bash
# 查看远程历史
git log origin/main --oneline

# 查看本地历史
git log --oneline
```

**提供选项给用户：**
1. **合并分支**（推荐）：保留所有历史
   ```bash
   git checkout master
   git fetch origin
   git merge origin/main --allow-unrelated-histories
   # 解决冲突后推送
   git push origin master:main
   ```

2. **强制推送**（会丢失远程历史，**必须用户同意**）
   ```bash
   # 先创建备份
   git push origin main:main-backup
   # 再强制推送
   git push -f origin master:main
   ```

---

## 标准推送流程

### 步骤 1：配置用户信息（首次）
```bash
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

### 步骤 2：添加文件
```bash
# 添加特定文件
git add filename1 filename2

# 或添加所有修改
git add -A
```

### 步骤 3：提交更改
```bash
git commit -m "提交信息"
```

### 步骤 4：推送到远程
```bash
git push origin main
```

---

## 危险操作清单（必须先询问）

| 操作 | 风险 | 必须先问 |
|------|------|:--------:|
| `git push -f` | 丢失远程历史 | ✅ |
| `git push --force` | 同上 | ✅ |
| `git reset --hard` | 丢失本地修改 | ✅ |
| `git rebase -i` + push -f | 重写历史 | ✅ |
| 覆盖远程分支 | 丢失原有内容 | ✅ |

---

## 本次事件教训

### 错误
1. 发现分支不一致时，没有询问用户
2. 擅自使用 `git push -f` 强制推送
3. 没有备份远程分支
4. 导致 v2 历史代码丢失

### 正确做法
1. **发现不一致 → 立即停止**
2. **通知用户 → 说明情况**
3. **提供选项 → 让用户选择**
4. **执行操作 → 先备份再操作**

---

## 快速参考

```bash
# 查看状态
git status

# 查看历史
git log --oneline --graph --all | head -10

# 查看远程分支
git branch -r

# 获取远程更新
git fetch origin

# 合并远程分支
git merge origin/main

# 创建备份分支
git branch backup-main origin/main

# 推送本地到远程
git push origin local-branch:remote-branch
```

---

*记录日期: 2026-03-14*  
*事件: GitHub 推送流程标准化*
