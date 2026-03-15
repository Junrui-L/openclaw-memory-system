# 记忆管理系统 v3.0 完整设计文档

> 深度复用 OpenClaw 平台能力的极简架构
> 
> 版本: 3.0.0  
> 日期: 2026-03-13  
> 状态: 设计阶段

---

## 目录

1. [概述](#1-概述)
2. [架构设计](#2-架构设计)
3. [模块详细设计](#3-模块详细设计)
4. [数据流设计](#4-数据流设计)
5. [Sessions 记忆保障](#5-sessions-记忆保障)
6. [接口设计](#6-接口设计)
7. [配置设计](#7-配置设计)
8. [测试策略](#8-测试策略)
9. [迁移计划](#9-迁移计划)
10. [附录](#10-附录)

---

## 1. 概述

### 1.1 设计目标

记忆管理系统 v3.0 的核心目标是：**深度复用 OpenClaw 平台能力，构建极简、高效、智能的记忆管理工具**。

#### 核心原则

| 原则 | v2.0 做法 | v3.0 改进 | 收益 |
|------|----------|----------|------|
| **不重复造轮子** | 自己遍历文件系统 | 复用 `memory_search` | 代码减少 71% |
| **不重复造轮子** | 自己提取关键词 | 复用 search 返回的关键词 | 代码减少 50% |
| **不重复造轮子** | 自己检查文件存在 | 依赖 OpenClaw 启动检查 | 删除重复代码 |
| **专注深度价值** | 简单分析 | 情感分析、主题聚类、洞察生成 | 新增智能能力 |
| **保障数据完整** | 无 Sessions 处理 | 自动合并、完整性检查 | 数据不丢失 |

### 1.2 系统定位

```
┌─────────────────────────────────────────────────────────┐
│                    系统定位                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   OpenClaw 平台层                                       │
│   ├── memory_search (向量语义搜索)                       │
│   ├── memory_get (精确读取)                             │
│   └── 启动检查 (文件/权限/配置)                          │
│          ↑                                              │
│   复用：数据查询、关键词提取、存在性检查                   │
│          ↓                                              │
│   记忆管理系统 v3.0                                     │
│   ├── 薄封装层 (reader)                                 │
│   ├── 深度分析层 (analyzer)                             │
│   ├── 质量检查层 (health)                               │
│   └── 数据保障层 (session-extractor)                    │
│          ↓                                              │
│   输出：报告、归档、备份、完整性保障                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.3 关键改进

#### 代码精简

| 模块 | v2.0 行数 | v3.0 行数 | 变化 | 关键改进 |
|------|----------|----------|------|---------|
| reader.py | 350 | 100 | -71% | 只做封装，删除文件遍历 |
| analyzer.py | 357 | 280 | -22% | 删除索引生成，保留深度分析 |
| health.py | 551 | 300 | -46% | 删除基础检查，新增质量检查 |
| archiver.py | 533 | 200 | -62% | 删除整理功能，专注归档 |
| reporter.py | 249 | 150 | -40% | 使用 reader/analyzer |
| session-extractor.py | 0 | 150 | +150 | **新增，保障 Sessions** |
| backup.py | 0 | 100 | +100 | 独立模块 |
| **总计** | **2040** | **1280** | **-37%** | |

#### 新增能力

| 能力 | 说明 | 价值 |
|------|------|------|
| **Sessions 自动合并** | 每小时自动提取 sessions，合并到 memory/ | **解决数据丢失** |
| **数据完整性检查** | 检查 session 覆盖率、记忆完整性 | **保障数据完整** |
| **情感分析** | 识别记忆内容的情绪倾向 | 深度洞察 |
| **主题聚类** | 识别近期讨论的主要话题 | 智能分析 |
| **洞察生成** | 基于记忆生成智能建议 | 主动服务 |
| **搜索性能监控** | 监控 memory_search 响应时间 | 性能保障 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│              OpenClaw 平台层（内置能力）                  │
├─────────────────────────────────────────────────────────┤
│  🔍 memory_search    📄 memory_get    ✅ 启动检查        │
│  (向量语义搜索)      (精确读取)       (文件存在性)        │
├─────────────────────────────────────────────────────────┤
│  能力清单：                                              │
│  • 语义搜索（embedding）                                 │
│  • 关键词自动提取                                        │
│  • 搜索结果聚合                                          │
│  • 文件存在性检查                                        │
│  • 权限检查                                              │
└─────────────────────────────────────────────────────────┘
                            ↓ 深度复用
┌─────────────────────────────────────────────────────────┐
│              记忆管理系统 v3.0                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                 Core 核心层                      │   │
│  ├─────────────┬─────────────┬─────────────────────┤   │
│  │   reader    │  analyzer   │      health         │   │
│  │  (薄封装层)  │  (深度分析)  │    (质量检查)        │   │
│  │             │             │                     │   │
│  │ • search()  │ • sentiment │ • data_quality      │   │
│  │ • get()     │ • topics    │ • index_consistency │   │
│  │ • get_recent│ • insights  │ • search_perf       │   │
│  │ • get_todos │ • lessons   │ • data_freshness    │   │
│  │             │ • trends    │ • learning_acc      │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
│                          ↓                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Services 服务层                     │   │
│  ├─────────────┬─────────────┬─────────────────────┤   │
│  │  archiver   │  reporter   │      backup         │   │
│  │  (归档服务)  │  (报告服务)  │    (备份服务)        │   │
│  │             │             │                     │   │
│  │ • daily     │ • morning   │ • incremental       │   │
│  │ • old       │ • health    │ • verify            │   │
│  │ • position  │             │ • cleanup           │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
│                          ↓                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Session 数据保障层                     │   │
│  ├─────────────────────────────────────────────────┤   │
│  │         session_extractor                       │   │
│  │              (Sessions 提取)                     │   │
│  │                                                 │   │
│  │ • extract_daily_sessions()                      │   │
│  │ • merge_to_daily_memory()                       │   │
│  │ • check_session_coverage()                      │   │
│  └─────────────────────────────────────────────────┘   │
│                          ↓                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Output 输出层                       │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  📁 reports/    📁 archive/    📁 .backup/     │   │
│  │  📄 INDEX.md    📄 integrity-report.md          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 设计原则 |
|------|------|---------|
| **reader** | 封装 OpenClaw 数据读取 | 只做封装，不做逻辑 |
| **analyzer** | 深度分析（OpenClaw 做不到） | 只做深度分析，不复用基础查询 |
| **health** | 数据质量检查 | 只检查 OpenClaw 不检查的质量 |
| **archiver** | 增量归档 | 只归档，不整理 |
| **reporter** | 报告生成 | 使用 reader/analyzer 数据 |
| **backup** | 增量备份 | 独立服务 |
| **session-extractor** | Sessions 提取与合并 | **保障数据不丢失** |

### 2.3 依赖关系

```
session-extractor
       ↓
    reader
       ↓
   ┌───┴───┐
   ↓       ↓
analyzer  health
   ↓       ↓
   └───┬───┘
       ↓
   ┌───┴───┬───┐
   ↓       ↓   ↓
archiver reporter backup
```

---

## 3. 模块详细设计（按优先级）

### 3.0 优先级总览

```
Phase 1 (核心 - 必须实现)
├── session_extractor.py      【新增】Session 自动提取合并 ⭐⭐⭐
├── reader.py                 【重构】复用 memory_search ⭐⭐⭐
├── health.py                 【新增】Session 覆盖率检查 ⭐⭐⭐
└── archiver.py               【保留】增量归档 ⭐⭐

Phase 2 (增强 - 可选实现)
├── analyzer.py               【增强】情感分析、主题聚类 ⭐
└── reporter.py               【增强】报告升级 ⭐
```

---

### 3.1 Phase 1 - 核心模块

### 3.1 reader.py - 薄封装层

#### 设计原则

- **只做封装**：不实现任何业务逻辑
- **统一接口**：封装 `memory_search` 和 `memory_get`
- **零重复**：不复用 v2.0 的文件遍历逻辑

#### 类定义

```python
class MemoryReader:
    """
    记忆数据读取器
    
    职责：薄封装 OpenClaw memory_search/memory_get
    原则：
        - 只做工具封装，不做业务逻辑
        - 所有数据查询都通过 search/get
        - 不直接操作文件系统
    """
    
    def __init__(self, config: Dict):
        """
        初始化
        
        Args:
            config: 配置字典，包含 paths 等
        """
        self.config = config
        self.cache = {}  # 简单缓存
    
    # ==================== 核心封装方法 ====================
    
    def search(
        self, 
        query: str, 
        max_results: int = 10,
        min_score: float = 0.5,
        **kwargs
    ) -> List[Dict]:
        """
        语义搜索记忆
        
        封装: OpenClaw memory_search 工具
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            min_score: 最小匹配分数
            
        Returns:
            搜索结果列表，每项包含:
            - path: 文件路径
            - score: 匹配分数
            - snippet: 匹配片段
            - keywords: 提取的关键词
            - source: 来源
            
        Example:
            >>> reader.search("待办事项", max_results=5)
            [
                {
                    "path": "memory/2026-03-13.md",
                    "score": 0.85,
                    "snippet": "- [ ] 完成代码审查...",
                    "keywords": ["待办", "代码审查"],
                    "source": "memory"
                }
            ]
        """
        # 调用 OpenClaw memory_search 工具
        # 返回标准化格式
        pass
    
    def get(
        self, 
        path: str, 
        from_line: int = None, 
        lines: int = None
    ) -> Optional[str]:
        """
        精确读取文件内容
        
        封装: OpenClaw memory_get 工具
        
        Args:
            path: 文件路径（相对 workspace）
            from_line: 起始行号（1-based）
            lines: 读取行数
            
        Returns:
            文件内容字符串，文件不存在返回 None
            
        Example:
            >>> reader.get("memory/2026-03-13.md", from_line=1, lines=50)
            "# 2026-03-13..."
        """
        # 调用 OpenClaw memory_get 工具
        pass
    
    # ==================== 便捷查询方法（基于 search） ====================
    
    def get_recent(self, days: int = 7) -> List[Dict]:
        """
        获取最近N天的记忆
        
        实现: 使用 search 查询日期范围，然后过滤
        
        Args:
            days: 天数
            
        Returns:
            记忆列表，每项包含日期、路径、摘要
            
        Example:
            >>> reader.get_recent(7)
            [
                {"date": "2026-03-13", "path": "...", "summary": "..."},
                ...
            ]
        """
        # 1. 计算日期范围
        # 2. 使用 search 查询
        # 3. 过滤并格式化
        pass
    
    def get_todos(self, status: str = "pending") -> List[Dict]:
        """
        获取待办事项
        
        实现: 使用 search 搜索待办语法
        
        Args:
            status: 状态 (pending/done/all)
            
        Returns:
            待办列表
            
        Example:
            >>> reader.get_todos("pending")
            [
                {
                    "text": "完成代码审查",
                    "date": "2026-03-13",
                    "path": "memory/2026-03-13.md",
                    "priority": "high"
                }
            ]
        """
        # 根据 status 构建查询
        # 使用 search 搜索
        # 格式化结果
        pass
    
    def get_keywords(self, path: str) -> List[str]:
        """
        获取指定记忆的关键词
        
        实现: 复用 search 返回的关键词，不自己提取
        
        Args:
            path: 记忆文件路径
            
        Returns:
            关键词列表
            
        Example:
            >>> reader.get_keywords("memory/2026-03-13.md")
            ["code", "review", "修复"]
        """
        # 使用 search 查询该文件
        # 提取返回的 keywords
        pass
    
    def get_stats(self) -> Dict:
        """
        获取记忆统计
        
        实现: 使用 search 聚合统计
        
        Returns:
            统计信息
            
        Example:
            >>> reader.get_stats()
            {
                "total_memories": 50,
                "total_todos": 30,
                "total_learnings": 20,
                "recent_7_days": 7
            }
        """
        # 使用多个 search 查询聚合
        pass
    
    def get_sessions(self, date: str) -> List[Dict]:
        """
        获取指定日期的 sessions
        
        实现: 使用 search 搜索 sessions 目录
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Session 列表
        """
        # 使用 search 搜索 sessions 目录
        pass
    
    # ==================== 删除的方法（v2.0 → v3.0） ====================
    
    # ❌ 删除: read_daily_memory() - 使用 get() 替代
    # ❌ 删除: read_hot_memory() - 使用 search("HOT") 替代
    # ❌ 删除: read_warm_memory() - 使用 search("WARM") 替代
    # ❌ 删除: list_memory_files() - 使用 search 替代
    # ❌ 删除: read_sessions() - 使用 get_sessions() 替代
    # ❌ 删除: get_learning_stats() - 使用 search("LEARNINGS") 替代
```

#### 与 v2.0 对比

| v2.0 方法 | v3.0 替代 | 改进 |
|-----------|----------|------|
| `read_daily_memory()` | `get(path)` | 统一为 memory_get 封装 |
| `read_hot_memory()` | `search("HOT记忆")` | 语义搜索替代文件读取 |
| `list_memory_files()` | `search("2026-03")` | 搜索聚合替代文件遍历 |
| `get_learning_stats()` | `search("LEARNINGS")` | 搜索替代手动统计 |
| `read_sessions()` | `get_sessions()` | 统一使用 search |

---

### 3.2 analyzer.py - 深度分析层

#### 设计原则

- **只做深度分析**：只做 OpenClaw 做不到的事
- **依赖 reader**：所有数据从 reader 来
- **不复用基础查询**：简单查询用 reader，复杂分析才自己实现

#### 类定义

```python
class MemoryAnalyzer:
    """
    记忆分析器
    
    职责：深度分析，只做 OpenClaw 做不到的事
    原则：
        - 基础查询用 reader.search
        - 深度分析才自己实现
        - 情感、聚类、洞察等 AI 能力
    """
    
    def __init__(self, reader: MemoryReader):
        """
        初始化
        
        Args:
            reader: MemoryReader 实例
        """
        self.reader = reader
    
    # ==================== 删除的方法（移到 reader） ====================
    
    # ❌ 删除: generate_index() - 使用 reader.get_stats() + 格式化
    # ❌ 删除: extract_key_events() - 使用 reader.search("###") 替代
    # ❌ 删除: extract_time_entries() - 使用 reader.search("### HH:MM") 替代
    # ❌ 删除: _extract_keywords() - 复用 reader.search 返回的关键词
    
    # ==================== 保留的方法（深度分析） ====================
    
    def extract_todos(self, content: str) -> List[Dict]:
        """
        提取待办事项
        
        保留原因: 需要正则匹配优先级，search 做不到
        
        但改为: 先用 reader.get() 获取内容，再分析
        
        Args:
            content: 记忆内容
            
        Returns:
            待办列表，包含优先级
        """
        # 正则匹配 - [ ] 语法
        # 分析优先级
        pass
    
    def analyze_todo_priority(self, todo: str) -> str:
        """
        智能分析待办优先级
        
        保留原因: 需要关键词匹配逻辑
        
        Args:
            todo: 待办文本
            
        Returns:
            优先级 (high/medium/low)
        """
        # 关键词匹配
        pass
    
    # ==================== 新增深度分析方法 ====================
    
    def analyze_sentiment(self, content: str) -> Dict:
        """
        情感分析
        
        输入: 记忆内容
        输出: {"sentiment": "positive/negative/neutral", "score": 0.8}
        
        实现: 
            - 调用外部 API (如 SiliconFlow)
            - 或使用本地轻量级模型
            
        原因: OpenClaw 不提供情感分析
        
        Args:
            content: 记忆内容
            
        Returns:
            情感分析结果
        """
        pass
    
    def extract_topics(self, contents: List[str], n_topics: int = 5) -> List[Dict]:
        """
        主题聚类
        
        输入: 多条记忆内容
        输出: [{"topic": "Code Review", "keywords": [...], "count": 10}]
        
        实现:
            - TF-IDF + K-Means 聚类
            - 或使用 LDA 主题模型
            
        原因: OpenClaw 不提供主题聚类
        
        Args:
            contents: 记忆内容列表
            n_topics: 主题数量
            
        Returns:
            主题列表
        """
        pass
    
    def generate_insights(self, days: int = 7) -> List[Dict]:
        """
        智能洞察生成
        
        输入: 时间范围
        输出: [{"type": "pattern", "description": "...", "suggestion": "..."}]
        
        实现:
            1. 使用 reader.get_recent(days) 获取近期记忆
            2. 使用 extract_topics() 识别主题
            3. 使用 analyze_sentiment() 分析情绪
            4. 基于规则生成洞察
            
        原因: 综合多个分析结果，OpenClaw 做不到
        
        Args:
            days: 天数
            
        Returns:
            洞察列表
        """
        pass
    
    def extract_lessons(self, days: int = 30) -> List[Dict]:
        """
        经验教训提取
        
        输入: 时间范围
        输出: [{"lesson": "...", "source": "LRN-xxx", "count": 3}]
        
        实现:
            1. 使用 reader.search("LRN-", max_results=100) 获取学习记录
            2. 聚类相似的学习记录
            3. 提取核心经验教训
            
        原因: 需要聚类和摘要，OpenClaw 做不到
        
        Args:
            days: 天数
            
        Returns:
            教训列表
        """
        pass
    
    def predict_trends(self, metric: str, days: int = 30) -> Dict:
        """
        趋势预测
        
        输入: 指标名称（如 "待办数量"）
        输出: {"trend": "increasing", "prediction": 15, "confidence": 0.85}
        
        实现: 简单时间序列分析（线性回归或移动平均）
        
        原因: OpenClaw 不提供趋势预测
        
        Args:
            metric: 指标名称
            days: 历史天数
            
        Returns:
            趋势预测结果
        """
        pass
    
    def generate_index_content(self) -> str:
        """
        生成索引内容
        
        实现:
            1. 使用 reader.get_stats() 获取统计
            2. 使用 reader.get_recent(30) 获取近期记忆
            3. 使用 extract_topics() 识别主题
            4. 格式化输出 Markdown
            
        替代: v2.0 的 generate_index()
        """
        pass
```

---

### 3.3 health.py - 质量检查层

#### 设计原则

- **只检查质量**：不检查 OpenClaw 已检查的基础项
- **数据驱动**：使用 reader 获取数据进行检查
- **自动修复**：发现问题自动修复

#### 类定义

```python
class HealthChecker:
    """
    健康检查器
    
    职责：检查 OpenClaw 不检查的数据质量
    原则：
        - 基础检查 OpenClaw 已做，只补充质量检查
        - 数据质量、索引一致性、搜索性能
    """
    
    def __init__(self, reader: MemoryReader):
        """
        初始化
        
        Args:
            reader: MemoryReader 实例
        """
        self.reader = reader
    
    # ==================== 删除的检查项（OpenClaw 已做） ====================
    
    # ❌ 删除: _check_memory_layer() - OpenClaw 启动检查文件存在
    # ❌ 删除: _check_identity_layer() - OpenClaw 启动检查
    # ❌ 删除: _check_task_layer() - OpenClaw 启动检查
    # ❌ 删除: _check_permissions() - OpenClaw 启动检查
    # ❌ 删除: _check_config_validity() - OpenClaw 配置检查
    
    # ==================== 保留的检查项（仍然需要） ====================
    
    def _check_disk_space(self) -> Dict:
        """
        磁盘空间检查
        
        保留原因: OpenClaw 不检查磁盘空间
        """
        pass
    
    def _check_backup_integrity(self) -> Dict:
        """
        备份完整性检查
        
        保留原因: 需要自定义检查
        """
        pass
    
    # ==================== 新增数据质量检查 ====================
    
    def _check_data_quality(self) -> Dict:
        """
        数据质量检查
        
        检查项:
            1. 空内容记忆文件
               - 使用 reader.get() 读取检查
               
            2. 格式错误的待办
               - 使用 reader.search("- [") 然后验证格式
               
            3. 损坏的索引
               - 使用 reader.get("memory/INDEX.md") 检查
               
        Returns:
            检查结果
        """
        pass
    
    def _check_index_consistency(self) -> Dict:
        """
        索引一致性检查
        
        检查项:
            1. INDEX.md 中的文件数 vs 实际文件数
               - reader.get("memory/INDEX.md") 解析统计
               - reader.search("2026-", max_results=1000) 聚合统计
               - 对比两者是否一致
               
            2. 待办统计是否准确
               - INDEX.md 中的待办数
               - reader.search("- [ ]") 实际统计
               - 对比两者
               
        Returns:
            检查结果
        """
        pass
    
    def _check_search_performance(self) -> Dict:
        """
        搜索性能检查
        
        检查项:
            1. memory_search 响应时间
               - 记录 reader.search() 执行时间
               
            2. 索引覆盖率
               - 对比文件数 vs 索引文档数
               
            3. 搜索结果质量
               - 检查返回结果的相关性分数
               
        Returns:
            检查结果
        """
        pass
    
    def _check_data_freshness(self) -> Dict:
        """
        数据新鲜度检查
        
        检查项:
            1. 最近是否有新记忆
               - reader.get_recent(1) 检查今天是否有记录
               
            2. 记忆更新频率是否正常
               - reader.search("2026-03", max_results=100)
               - 分析时间分布是否均匀
               
            3. 长时间未更新的重要记忆
               - 识别超过 7 天未更新的重要记忆
               
        Returns:
            检查结果
        """
        pass
    
    def _check_learning_accumulation(self) -> Dict:
        """
        学习积累检查
        
        检查项:
            1. 待处理学习记录数量
               - reader.search("Status.*pending") 统计
               
            2. 学习记录升级情况
               - reader.search("Recurrence-Count") 检查
               - 识别验证次数足够但未升级的学习
               
            3. 学习记录分布
               - 按 area 统计学习记录分布
               
        Returns:
            检查结果
        """
        pass
    
    def _check_session_coverage(self) -> Dict:
        """
        Session 覆盖率检查
        
        检查项:
            1. Sessions 是否都合并到 memory/
            2. 覆盖率是否达标
            3. 缺失的 Sessions
            
        Returns:
            检查结果
        """
        pass
    
    def repair_issues(self, issues: List[Dict]) -> bool:
        """
        自动修复问题
        
        Args:
            issues: 问题列表
            
        Returns:
            修复成功返回 True
        """
        pass
```

#### 检查项对比

| v2.0 检查项 | v3.0 检查项 | 原因 |
|------------|------------|------|
| 日记层存在性 | ❌ 删除 | OpenClaw 启动检查 |
| 身份层存在性 | ❌ 删除 | OpenClaw 启动检查 |
| 任务层存在性 | ❌ 删除 | OpenClaw 启动检查 |
| 权限检查 | ❌ 删除 | OpenClaw 启动检查 |
| 配置有效性 | ❌ 删除 | OpenClaw 配置检查 |
| 磁盘空间 | ✅ 保留 | OpenClaw 不检查 |
| 备份完整性 | ✅ 保留 | 需要自定义检查 |
| 日志大小 | ✅ 保留 | 需要自定义检查 |
| 定时任务 | ✅ 保留 | 需要自定义检查 |
| 数据质量 | 🆕 新增 | **核心价值** |
| 索引一致性 | 🆕 新增 | **核心价值** |
| 搜索性能 | 🆕 新增 | **核心价值** |
| 数据新鲜度 | 🆕 新增 | **核心价值** |
| 学习积累 | 🆕 新增 | **核心价值** |
| Session 覆盖 | 🆕 新增 | **核心价值** |

---

### 3.4 session_extractor.py - Sessions 数据保障层

#### 设计原则

- **自动提取**：每小时自动提取 sessions
- **智能合并**：去重、补充，不重复记录
- **完整性保障**：确保所有 session 都被记录

#### 类定义

```python
class SessionExtractor:
    """
    Sessions 提取器
    
    职责：自动提取 sessions 记录，合并到每日记忆
    原则：
        - 每小时自动执行
        - 智能去重、补充
        - 保障数据不丢失
    
    重要说明：
        - memory_search 不覆盖 agents/main/sessions/ 目录
        - 必须直接读取文件系统
        - 提取后合并到 memory/，才能被 memory_search 搜索
    """
    
    def __init__(self, reader: MemoryReader, config: Dict):
        """
        初始化
        
        Args:
            reader: MemoryReader 实例（用于读取 memory/）
            config: 配置
        """
        self.reader = reader
        self.config = config
        # Sessions 目录路径（直接指定，不通过 reader）
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
        self.extracted_cache = {}  # 已提取的 session 缓存
    
    def extract_daily_sessions(self, date: str) -> List[Dict]:
        """
        提取指定日期的 sessions
        
        实现:
            1. 【直接读取】遍历 self.sessions_dir 下的 .jsonl 文件
            2. 【直接读取】读取 JSON Lines 格式
            3. 【直接读取】按日期过滤（检查 timestamp）
            4. 提取用户消息内容（过滤系统消息）
            5. 去重（基于消息内容 hash）
            6. 格式化返回
            
        注意:
            - 不使用 reader.search()，因为 memory_search 不覆盖 sessions/
            - 必须直接操作文件系统
            
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Session 列表，每项包含:
            - session_id: Session ID
            - timestamp: 时间戳
            - messages: 用户消息列表
            - summary: 自动摘要
            
        Example:
            >>> extractor.extract_daily_sessions("2026-03-13")
            [
                {
                    "session_id": "7b742ae7-...",
                    "timestamp": "2026-03-13T16:00:00",
                    "messages": ["用户: 你好", "助手: 你好"],
                    "summary": "用户问候"
                }
            ]
        """
        # 1. 遍历 sessions_dir 下的 .jsonl 文件
        # 2. 读取并解析 JSON Lines
        # 3. 按日期过滤
        # 4. 提取用户消息
        # 5. 去重
        pass
    
    def _read_session_file(self, file_path: Path) -> List[Dict]:
        """
        读取单个 session 文件
        
        文件格式: JSON Lines (.jsonl)
        每行一个 JSON 对象，包含消息记录
        
        Args:
            file_path: .jsonl 文件路径
            
        Returns:
            消息记录列表
        """
        # 读取 JSON Lines 文件
        # 解析每行 JSON
        # 返回消息列表
        pass
    
    def merge_to_daily_memory(self, date: str) -> bool:
        """
        将 sessions 合并到每日记忆
        
        实现:
            1. 提取当日 sessions（直接读取文件系统）
            2. 【使用 reader】reader.get(f"memory/{date}.md") 获取现有记忆
            3. 智能合并:
               - 去重：已存在的 session 不重复添加
               - 补充：新 session 添加到合适位置
               - 更新：已有 session 有新消息时更新
            4. 写回记忆文件
            
        Args:
            date: 日期
            
        Returns:
            合并成功返回 True
        """
        pass
    
    def check_session_coverage(self, days: int = 7) -> Dict:
        """
        检查 session 覆盖度
        
        实现:
            1. 【直接读取】统计 sessions/ 目录下的 session 数量
            2. 【使用 reader】reader.get(f"memory/{date}.md") 检查是否已记录
            3. 计算覆盖率
            
        Args:
            days: 检查天数
            
        Returns:
            覆盖率报告:
            {
                "total_sessions": 50,
                "recorded_in_memory": 45,
                "coverage_rate": 0.9,
                "missing_dates": ["2026-03-10"],
                "details": [...]
            }
        """
        pass
    
    def auto_extract_and_merge(self):
        """
        自动提取并合并（定时任务调用）
        
        执行:
            1. 获取今天和昨天的日期
            2. 【直接读取】提取 sessions
            3. 【使用 reader】合并到记忆
            4. 记录日志
        """
        pass
```

---

## 4. 数据流设计

### 4.1 正常数据流

```
用户对话
    ↓
OpenClaw 自动记录 → agents/main/sessions/
    ↓
SessionExtractor (每小时)
    - extract_daily_sessions()  【直接读取 sessions/*.jsonl】
    - merge_to_daily_memory()   【使用 reader 读取 memory/】
    ↓
memory/YYYY-MM-DD.md
    ↓
定时任务触发
    ├─ daily (00:00, 06:00, 12:00, 18:00)
    │   └─ Archiver.daily_archive()
    │       └─ 增量归档
    │
    ├─ maintenance (02:00)
    │   └─ Archiver.maintenance()
    │       └─ Analyzer.generate_insights()
    │       └─ Analyzer.extract_lessons()
    │       └─ Archiver._archive_old_memories()
    │
    ├─ report (08:00)
    │   └─ Reporter.generate_morning_report()
    │       └─ Reader.get_recent()
    │       └─ Reader.get_todos()
    │       └─ Analyzer.generate_insights()
    │
    ├─ health (04:00)
    │   └─ HealthChecker.check()
    │       └─ 各项质量检查
    │
    └─ backup (03:00)
        └─ BackupManager.create_incremental_backup()
```

### 4.2 Sessions 保障数据流

```
┌─────────────────────────────────────────┐
│         Sessions 保障机制                │
├─────────────────────────────────────────┤
│                                         │
│  第一层: 实时记录（OpenClaw）             │
│  ├── 用户对话                           │
│  └── 自动记录到 sessions/                │
│                                         │
│  第二层: 自动提取（每小时）               │
│  ├── SessionExtractor.extract_daily()   │
│  ├── 【直接读取】sessions/*.jsonl        │
│  ├── 【直接读取】解析 JSON Lines         │
│  └── 提取用户消息，过滤系统消息           │
│                                         │
│  第三层: 智能合并（每小时）               │
│  ├── SessionExtractor.merge_to_daily()  │
│  ├── 去重（基于 hash）                   │
│  ├── 补充（新 session）                  │
│  └── 更新（已有 session 新消息）          │
│                                         │
│  第四层: 完整性检查（每天 02:00）         │
│  ├── HealthChecker._check_session_coverage()
│  ├── 对比 sessions/ vs memory/           │
│  └── 自动修复缺失                        │
│                                         │
│  第五层: 备份恢复（每天 03:00）           │
│  ├── 增量备份 memory/                    │
│  └── 损坏时可恢复                        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 5. Sessions 记忆保障

### 5.1 问题分析

**现状问题**:
- OpenClaw 自动记录 sessions 到 `agents/main/sessions/`
- 但这些记录**不会自动**进入 `memory/YYYY-MM-DD.md`
- 如果不手动整理，存在记忆丢失风险

**v3.0 解决方案**:
- **自动提取**：每小时自动提取 sessions
- **智能合并**：去重、补充、更新
- **完整性检查**：每天检查覆盖率
- **自动修复**：发现问题自动修复

**重要说明**:
- `memory_search` **不覆盖** `agents/main/sessions/` 目录
- SessionExtractor 必须**直接读取文件系统**
- 提取后合并到 `memory/`，才能被 `memory_search` 搜索

### 5.2 保障机制

```
┌─────────────────────────────────────────┐
│           数据完整性保障体系             │
├─────────────────────────────────────────┤
│                                         │
│  第一层: 实时捕获（OpenClaw）            │
│  ├── 用户对话                           │
│  └── 自动记录到 sessions/                │
│                                         │
│  第二层: 自动提取（每小时）               │
│  ├── SessionExtractor.extract_daily()   │
│  ├── 【直接读取】遍历 sessions/*.jsonl   │
│  ├── 【直接读取】解析 JSON Lines         │
│  ├── 【直接读取】按日期过滤              │
│  └── 提取用户消息，过滤系统消息           │
│                                         │
│  第三层: 智能合并（每小时）               │
│  ├── SessionExtractor.merge_to_daily()  │
│  ├── 去重（基于 hash）                   │
│  ├── 补充（新 session）                  │
│  └── 更新（已有 session 新消息）          │
│                                         │
│  第四层: 完整性检查（每天 02:00）         │
│  ├── HealthChecker._check_session_coverage()
│  ├── 对比 sessions/ vs memory/           │
│  └── 自动修复缺失                        │
│                                         │
│  第五层: 备份恢复（每天 03:00）           │
│  ├── 增量备份 memory/                    │
│  └── 损坏时可恢复                        │
│                                         │
└─────────────────────────────────────────┘
```

### 5.3 关键指标

```python
# 数据完整性指标
METRICS = {
    "session_coverage_rate": 0.95,      # Session 覆盖率目标 >=95%
    "memory_completeness": 0.99,        # 记忆完整性目标 >=99%
    "search_index_coverage": 0.98,      # 搜索索引覆盖率 >=98%
    "data_freshness_hours": 1,          # 数据新鲜度 <=1小时
}
```

---

## 6. 接口设计

### 6.1 命令行接口

```bash
# 查看系统状态
bash scripts/memory/run.sh status

# 生成晨报
bash scripts/memory/run.sh report

# 健康检查
bash scripts/memory/run.sh health

# 每日归档
bash scripts/memory/run.sh daily

# 记忆维护
bash scripts/memory/run.sh maintenance

# 生成索引
bash scripts/memory/run.sh index

# 手动备份
bash scripts/memory/run.sh backup

# 执行全部任务
bash scripts/memory/run.sh all

# 【新增】提取并合并 Sessions
bash scripts/memory/run.sh session-merge

# 【新增】检查数据完整性
bash scripts/memory/run.sh integrity-check
```

### 6.2 Python API

```python
from memory_manager import MemoryManager

# 初始化
manager = MemoryManager(config)

# 执行命令
manager.run("daily")
manager.run("report")
manager.run("health")

# 【新增】提取 Sessions
manager.session_extractor.extract_daily_sessions("2026-03-13")
manager.session_extractor.merge_to_daily_memory("2026-03-13")

# 【新增】检查完整性
manager.health_checker.check_session_coverage(days=7)
```

---

## 7. 配置设计

### 7.1 完整配置

```yaml
# ========================================
# 基础路径
# ========================================
paths:
  workspace: "/home/node/.openclaw/workspace"
  reports: "/home/node/.openclaw/workspace/reports"
  archive: "/home/node/.openclaw/workspace/archive"
  backup: "/home/node/.openclaw/workspace/.backup"
  logs: "/home/node/.openclaw/workspace/logs"

# ========================================
# 归档配置
# ========================================
archive:
  retention_days: 7           # 7天后归档
  incremental: true           # 启用增量

# ========================================
# 备份配置
# ========================================
backup:
  enabled: true
  daily: true
  weekly: true
  retention_daily: 7
  retention_weekly: 4

# ========================================
# Sessions 提取配置
# ========================================
sessions:
  auto_merge: true            # 自动合并
  merge_interval: 3600        # 合并间隔（秒）
  coverage_threshold: 0.95    # 覆盖率阈值

# ========================================
# 分析配置
# ========================================
analysis:
  sentiment_analysis: true      # 情感分析
  topic_clustering: true        # 主题聚类
  insight_generation: true      # 洞察生成
  lesson_extraction: true       # 教训提取
  trend_prediction: true        # 趋势预测

# ========================================
# 健康检查配置
# ========================================
health:
  data_quality: true            # 数据质量
  index_consistency: true       # 索引一致性
  search_performance: true      # 搜索性能
  data_freshness: true          # 数据新鲜度
  learning_accumulation: true   # 学习积累
  session_coverage: true        # Session 覆盖
  disk_warning: 80              # 磁盘告警阈值
  disk_critical: 90             # 磁盘严重阈值

# ========================================
# 报告配置
# ========================================
reports:
  morning:
    enabled: true
    hour: 8
```

---

## 8. 测试策略

### 8.1 测试分层

```
┌─────────────────────────────────────────┐
│           测试策略                       │
├─────────────────────────────────────────┤
│                                         │
│  单元测试（Unit Tests）                   │
│  ├── test_reader.py                     │
│  ├── test_analyzer.py                   │
│  ├── test_health.py                     │
│  └── test_session_extractor.py          │
│                                         │
│  集成测试（Integration Tests）            │
│  ├── test_reader_analyzer.py            │
│  ├── test_session_merge.py              │
│  └── test_end_to_end.py                 │
│                                         │
│  性能测试（Performance Tests）            │
│  ├── test_search_performance.py         │
│  └── test_memory_usage.py               │
│                                         │
└─────────────────────────────────────────┘
```

### 8.2 关键测试用例（按优先级）

**Phase 1 核心测试（必须）**：

| 模块 | 测试用例 | 优先级 | 说明 |
|------|---------|:------:|------|
| session-extractor | `test_extract_sessions` | ⭐⭐⭐ | 提取 sessions |
| session-extractor | `test_merge_deduplication` | ⭐⭐⭐ | 合并去重 |
| session-extractor | `test_coverage_rate` | ⭐⭐⭐ | 覆盖率 >=95% |
| reader | `test_search_returns_results` | ⭐⭐ | search 返回正确格式 |
| reader | `test_get_reads_file` | ⭐⭐ | get 读取文件内容 |
| health | `test_session_coverage_check` | ⭐⭐⭐ | Session 覆盖率检查 |
| health | `test_data_freshness` | ⭐⭐ | 数据新鲜度检查 |

**Phase 2 增强测试（可选）**：

| 模块 | 测试用例 | 优先级 | 说明 |
|------|---------|:------:|------|
| analyzer | `test_sentiment_analysis` | ⭐ | 情感分析准确性 |
| analyzer | `test_topic_clustering` | ⭐ | 主题聚类效果 |
| analyzer | `test_insight_generation` | ⭐ | 洞察生成 |

---

### 8.3 测试代码示例

#### Phase 1 核心测试代码

**test_session_extractor.py**

```python
#!/usr/bin/env python3
"""
SessionExtractor 单元测试
Phase 1 核心测试
"""

import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.session_extractor import SessionExtractor


class TestSessionExtractor(unittest.TestCase):
    """测试 SessionExtractor"""
    
    def setUp(self):
        """测试前准备"""
        self.config = {
            'paths': {
                'workspace': '/tmp/test_workspace',
                'memory': '/tmp/test_workspace/memory'
            }
        }
        self.mock_reader = Mock()
        self.extractor = SessionExtractor(self.mock_reader, self.config)
    
    def test_extract_sessions_from_jsonl(self):
        """
        测试从 JSONL 文件提取 Sessions
        
        场景: 读取 sessions/ 目录下的 .jsonl 文件
        验证: 正确解析 JSON Lines 格式
        """
        # 准备测试数据
        test_jsonl_content = '''
{"timestamp": "2026-03-13T10:00:00", "role": "user", "content": "你好"}
{"timestamp": "2026-03-13T10:01:00", "role": "assistant", "content": "你好"}
{"timestamp": "2026-03-13T10:02:00", "role": "user", "content": "测试"}
'''
        
        # Mock 文件读取
        with patch('builtins.open', unittest.mock.mock_open(read_data=test_jsonl_content)):
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'glob', return_value=[Path('test.jsonl')]):
                    result = self.extractor.extract_daily_sessions('2026-03-13')
        
        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['session_id'], 'test')
        self.assertEqual(len(result[0]['messages']), 2)  # 过滤系统消息
    
    def test_merge_deduplication(self):
        """
        测试合并去重
        
        场景: 同一 session 已存在于 memory/
        验证: 不重复添加
        """
        # 准备现有记忆
        existing_memory = '''
# 2026-03-13

## Session: test-session
- 10:00 用户: 你好
- 10:01 助手: 你好
'''
        # 准备新 sessions
        new_sessions = [
            {
                'session_id': 'test-session',
                'timestamp': '2026-03-13T10:00:00',
                'messages': ['用户: 你好', '助手: 你好']
            }
        ]
        
        # Mock reader.get 返回现有记忆
        self.mock_reader.get.return_value = existing_memory
        
        # 执行合并
        result = self.extractor.merge_to_daily_memory('2026-03-13')
        
        # 验证不重复添加
        self.assertTrue(result)
        # 验证 reader.get 被调用
        self.mock_reader.get.assert_called_once_with('memory/2026-03-13.md')
    
    def test_coverage_rate_calculation(self):
        """
        测试覆盖率计算
        
        场景: sessions/ 有 10 个，memory/ 记录了 8 个
        验证: 覆盖率 = 80%
        """
        # Mock sessions 目录文件
        mock_session_files = [Path(f'session_{i}.jsonl') for i in range(10)]
        
        # Mock memory 中记录了 8 个
        mock_memory_content = '''
# 2026-03-13

## Sessions
- session_0
- session_1
- session_2
- session_3
- session_4
- session_5
- session_6
- session_7
'''
        
        with patch.object(Path, 'glob', return_value=mock_session_files):
            self.mock_reader.get.return_value = mock_memory_content
            
            result = self.extractor.check_session_coverage(days=1)
        
        # 验证覆盖率计算
        self.assertEqual(result['total_sessions'], 10)
        self.assertEqual(result['recorded_in_memory'], 8)
        self.assertEqual(result['coverage_rate'], 0.8)


class TestSessionExtractorIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_extraction_and_merge(self):
        """
        端到端测试：提取 + 合并
        
        场景: 完整流程
        验证: Sessions 正确合并到 memory/
        """
        # 创建临时目录
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # 准备测试环境
            sessions_dir = Path(tmpdir) / 'sessions'
            memory_dir = Path(tmpdir) / 'memory'
            sessions_dir.mkdir()
            memory_dir.mkdir()
            
            # 创建测试 session 文件
            session_file = sessions_dir / 'test-session.jsonl'
            session_file.write_text('''
{"timestamp": "2026-03-13T10:00:00", "role": "user", "content": "测试"}
''')
            
            # 执行提取和合并
            config = {'paths': {'workspace': tmpdir, 'memory': str(memory_dir)}}
            extractor = SessionExtractor(Mock(), config)
            extractor.sessions_dir = sessions_dir
            
            result = extractor.extract_daily_sessions('2026-03-13')
            
            # 验证提取成功
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['messages'], ['用户: 测试'])


if __name__ == '__main__':
    unittest.main()
```

**test_health.py**

```python
#!/usr/bin/env python3
"""
HealthChecker 单元测试
Phase 1 核心测试
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

from core.health import HealthChecker


class TestHealthChecker(unittest.TestCase):
    """测试 HealthChecker"""
    
    def setUp(self):
        """测试前准备"""
        self.config = {
            'paths': {
                'workspace': '/tmp/test',
                'memory': '/tmp/test/memory'
            },
            'health': {
                'session_coverage_threshold': 0.95
            }
        }
        self.mock_reader = Mock()
        self.checker = HealthChecker(self.mock_reader, self.config)
    
    def test_session_coverage_check_high_coverage(self):
        """
        测试 Session 覆盖率高的情况
        
        场景: sessions/ 100 个，memory/ 记录了 98 个
        验证: 覆盖率 98%，检查通过
        """
        # Mock sessions 数量（直接读取）
        with patch.object(Path, 'glob', return_value=[Path(f's{i}.jsonl') for i in range(100)]):
            # Mock memory 中记录的数量
            self.mock_reader.search.return_value = [
                {'path': f'memory/2026-03-{i:02d}.md'} for i in range(1, 99)
            ]
            
            result = self.checker._check_session_coverage()
        
        # 验证结果
        self.assertEqual(result['total_sessions'], 100)
        self.assertEqual(result['recorded_in_memory'], 98)
        self.assertEqual(result['coverage_rate'], 0.98)
        self.assertEqual(result['status'], 'ok')
    
    def test_session_coverage_check_low_coverage(self):
        """
        测试 Session 覆盖率低的情况
        
        场景: sessions/ 100 个，memory/ 只记录了 80 个
        验证: 覆盖率 80%，告警
        """
        with patch.object(Path, 'glob', return_value=[Path(f's{i}.jsonl') for i in range(100)]):
            self.mock_reader.search.return_value = [
                {'path': f'memory/2026-03-{i:02d}.md'} for i in range(1, 81)
            ]
            
            result = self.checker._check_session_coverage()
        
        # 验证告警
        self.assertEqual(result['coverage_rate'], 0.8)
        self.assertEqual(result['status'], 'warning')
        self.assertIn('alert', result)
    
    def test_data_freshness_check_fresh(self):
        """
        测试数据新鲜度检查 - 数据新鲜
        
        场景: 1 小时内有新数据
        验证: 检查通过
        """
        # Mock 最近记忆
        self.mock_reader.get_recent.return_value = [
            {'date': '2026-03-13', 'path': 'memory/2026-03-13.md'}
        ]
        
        result = self.checker._check_data_freshness()
        
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['hours_since_last_update'], 0)
    
    def test_data_freshness_check_stale(self):
        """
        测试数据新鲜度检查 - 数据陈旧
        
        场景: 超过 24 小时无更新
        验证: 告警
        """
        # Mock 旧数据
        old_date = (datetime.now() - timedelta(hours=25)).strftime('%Y-%m-%d')
        self.mock_reader.get_recent.return_value = [
            {'date': old_date, 'path': f'memory/{old_date}.md'}
        ]
        
        result = self.checker._check_data_freshness()
        
        self.assertEqual(result['status'], 'warning')
        self.assertGreater(result['hours_since_last_update'], 24)


class TestHealthCheckerIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_health_check(self):
        """
        完整健康检查流程
        
        验证: 所有检查项都执行
        """
        mock_reader = Mock()
        checker = HealthChecker(mock_reader, {})
        
        # Mock 所有依赖
        mock_reader.search.return_value = []
        mock_reader.get.return_value = ""
        
        with patch.object(checker, '_check_disk_space', return_value={'status': 'ok'}):
            with patch.object(checker, '_check_session_coverage', return_value={'status': 'ok'}):
                result = checker.check({})
        
        # 验证所有检查都执行
        self.assertIn('checks', result)
        self.assertEqual(len(result['checks']), 2)


if __name__ == '__main__':
    unittest.main()
```

---

### 8.4 测试执行命令

```bash
# 运行所有测试
python -m pytest tests/ -v

# 只运行 Phase 1 核心测试
python -m pytest tests/test_session_extractor.py tests/test_reader.py tests/test_health.py -v

# 运行特定测试
python -m pytest tests/test_session_extractor.py::TestSessionExtractor::test_coverage_rate_calculation -v

# 生成覆盖率报告
python -m pytest tests/ --cov=core --cov-report=html
```

---

### 8.5 测试数据准备

```python
# conftest.py - pytest 配置

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_workspace():
    """创建临时工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / 'memory').mkdir()
        (workspace / 'sessions').mkdir()
        yield workspace


@pytest.fixture
def sample_session_data():
    """示例 Session 数据"""
    return '''
{"timestamp": "2026-03-13T10:00:00", "role": "user", "content": "你好"}
{"timestamp": "2026-03-13T10:01:00", "role": "assistant", "content": "你好"}
{"timestamp": "2026-03-13T10:02:00", "role": "user", "content": "测试"}
'''


@pytest.fixture
def sample_memory_data():
    """示例记忆数据"""
    return '''
# 2026-03-13

## Sessions
- session_1
- session_2

## 对话记录
用户: 你好
助手: 你好
'''
```

**test_reader.py**

```python
#!/usr/bin/env python3
"""
Reader 单元测试
Phase 1 核心测试
"""

import unittest
from unittest.mock import Mock, patch

from core.reader import MemoryReader


class TestMemoryReader(unittest.TestCase):
    """测试 MemoryReader"""
    
    def setUp(self):
        """测试前准备"""
        self.config = {
            'paths': {
                'workspace': '/tmp/test',
                'memory': '/tmp/test/memory'
            }
        }
        self.reader = MemoryReader(self.config)
    
    @patch('core.reader.memory_search')
    def test_search_returns_results(self, mock_search):
        """
        测试 search 返回正确格式
        
        验证: 封装 memory_search，返回标准化格式
        """
        # Mock memory_search 返回
        mock_search.return_value = {
            'results': [
                {
                    'path': 'memory/2026-03-13.md',
                    'score': 0.85,
                    'snippet': '测试内容',
                    'keywords': ['测试'],
                    'source': 'memory'
                }
            ]
        }
        
        # 执行搜索
        result = self.reader.search('测试', max_results=5)
        
        # 验证结果格式
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['path'], 'memory/2026-03-13.md')
        self.assertEqual(result[0]['score'], 0.85)
        


---

## 9. 实施计划（按优先级）

### 9.1 Phase 1 - 核心功能（必须）

**目标**：保障 Sessions 不丢失，复用 OpenClaw 能力

**时间**：2周

**核心模块**：

```
Phase 1/
├── session_extractor.py      【新增】Session 自动提取合并
│   ├── 直接读取 sessions/*.jsonl
│   ├── 解析 JSON Lines
│   ├── 按日期过滤
│   └── 合并到 memory/
│
├── reader.py                 【重构】复用 memory_search
│   ├── search()              封装 memory_search
│   ├── get()                 封装 memory_get
│   ├── get_recent()          使用 search
│   └── get_todos()           使用 search
│
├── health.py                 【新增】Session 覆盖率检查
│   ├── _check_session_coverage()  【核心】覆盖率检查
│   ├── _check_data_freshness()
│   └── _check_index_consistency()
│
└── archiver.py               【保留】增量归档
    ├── daily_archive()
    └── _archive_old_memories()
```

**详细步骤**：

```
Week 1:
├── Day 1-2: session_extractor.py
│   └── 实现 Session 提取和合并
├── Day 3-4: reader.py 重构
│   └── 封装 memory_search/memory_get
└── Day 5-7: health.py 新增
    └── 实现 Session 覆盖率检查

Week 2:
├── Day 1-3: 集成测试
├── Day 4-5: 与 v2.0 并行运行
└── Day 6-7: 修复问题
```

**验收标准**：
- [ ] Session 自动提取合并正常工作
- [ ] Session 覆盖率 >=95%
- [ ] reader 复用 memory_search 成功
- [ ] 无数据丢失

---

### 9.2 Phase 2 - 增强功能（可选）

**目标**：深度分析能力

**时间**：1周（可延后）

**增强模块**：

```
Phase 2/
├── analyzer.py               【增强】深度分析
│   ├── analyze_sentiment()   情感分析
│   ├── extract_topics()      主题聚类
│   ├── generate_insights()   洞察生成
│   └── predict_trends()      趋势预测
│
└── reporter.py               【增强】报告升级
    └── 使用 analyzer 生成洞察
```

**详细步骤**：

```
Week 1:
├── Day 1-2: 情感分析
├── Day 3-4: 主题聚类
└── Day 5-7: 洞察生成 + 测试
```

**验收标准**：
- [ ] 情感分析可用
- [ ] 主题聚类可用
- [ ] 洞察生成可用

---

### 9.3 Phase 3 - 灰度切换

**时间**：1周

```
Week 1:
├── Day 1-2: 50% 流量切到 v3.0
├── Day 3-5: 监控对比
└── Day 6-7: 100% 切换
```

---

### 9.4 Phase 4 - 清理

**时间**：1周

```
Week 1:
├── Day 1-3: 确认稳定
├── Day 4-5: 删除 v2.0
└── Day 6-7: 更新文档
```

**Phase 2: 灰度测试（1周）**

```
- 50% 定时任务使用 v3.0
- 对比输出结果
- 监控差异
- 修复问题
```

**Phase 3: 全面切换（3天）**

```
- 全部切换到 v3.0
- v2.0 保留备份
- 监控稳定性
```

**Phase 4: 清理（1周）**

```
- 确认 v3.0 稳定
- 删除 v2.0
- 更新文档
```

---

## 10. 附录

### 10.1 设计反思与教训

#### 反思一：未先验证假设导致设计缺陷

**问题**：在设计初期假设 `memory_search` 可以搜索所有记忆数据，包括 `agents/main/sessions/`

**实际**：
- `memory_search` 只覆盖 `workspace/memory/` 和 `MEMORY.md`
- `agents/main/sessions/` **不在**搜索范围内
- 导致 `SessionExtractor` 最初设计错误

**根本原因**：
1. **未先测试验证**：设计前没有实际测试 `memory_search` 的覆盖范围
2. **假设代替验证**：想当然地认为搜索会覆盖所有相关目录
3. **文档阅读不细**：没有仔细阅读 OpenClaw 文档关于搜索范围的说明

**影响**：
- 需要重新设计 `SessionExtractor`
- 混合使用"直接读取"和"search"两种模式
- 架构复杂度增加

**改进措施**：
1. **设计前必测试**：任何假设都要先验证
2. **明确边界**：清晰定义每个工具的覆盖范围
3. **文档化限制**：将发现限制写入设计文档

#### 反思二：分层设计的重要性

**问题**：v2.0 的 `reader.py` 混合了文件遍历和搜索逻辑

**改进**：v3.0 明确分层
- `reader`：只封装 OpenClaw 能力
- `session-extractor`：直接读取文件系统
- 职责清晰，便于维护

#### 反思三：复用 vs 自制的权衡

**正确做法**：
- ✅ 复用 `memory_search`（覆盖范围内）
- ✅ 复用 `memory_get`（精确读取）
- ❌ 不要复用 `memory_search`（覆盖范围外）
- ✅ 自制文件遍历（sessions/ 目录）

**决策标准**：
1. 先测试工具能力
2. 明确覆盖范围
3. 范围内复用，范围外自制

### 10.2 设计检查清单

**设计前必做**：
- [ ] 测试所有假设（工具能力、覆盖范围）
- [ ] 明确工具边界
- [ ] 验证数据流可行性
- [ ] 检查依赖关系

**设计中必做**：
- [ ] 分层清晰
- [ ] 职责单一
- [ ] 接口明确
- [ ] 错误处理

**设计后必做**：
- [ ] 文档化限制
- [ ] 记录反思
- [ ] 更新检查清单

### 10.3 已验证的假设清单

| 假设 | 验证方法 | 结果 | 影响 |
|------|---------|------|------|
| memory_search 覆盖 sessions/ | 实际搜索测试 | ❌ 否 | SessionExtractor 改为直接读取 |
| memory_search 覆盖 memory/ | 实际搜索测试 | ✅ 是 | reader 可以复用 |
| memory_get 可以读取任意文件 | 实际读取测试 | ✅ 是 | reader 可以复用 |
| OpenClaw 启动检查文件存在 | 查阅文档 | ✅ 是 | health 删除重复检查 |

**验证记录**：
- 时间：2026-03-13 17:00
- 方法：`memory_search` 搜索 "session"，结果只返回 `memory/` 目录
- 结论：`sessions/` 不在搜索范围内

### 10.4 参考文档

| 术语 | 说明 |
|------|------|
| memory_search | OpenClaw 内置的向量语义搜索工具 |
| memory_get | OpenClaw 内置的精确文件读取工具 |
| Session | OpenClaw 的会话记录 |
| HOT/WARM/COLD | 身份层的三层记忆结构 |
| 增量归档 | 只读取新增内容，避免重复处理 |
| TF-IDF | 词频-逆文档频率算法 |

### 10.2 参考文档

- OpenClaw 官方文档: https://docs.openclaw.ai
- memory_search 工具说明
- memory_get 工具说明

---

## 11. 优先级总结

### 实施路线图

```
Phase 1 (核心 - 必须)
├── 目标: 保障 Sessions 不丢失
├── 时间: 2周
├── 模块:
│   ├── session_extractor.py ⭐⭐⭐
│   ├── reader.py ⭐⭐⭐
│   ├── health.py ⭐⭐⭐
│   └── archiver.py ⭐⭐
└── 标准: Session 覆盖率 >=95%

Phase 2 (增强 - 可选)
├── 目标: 深度分析能力
├── 时间: 1周
├── 模块:
│   ├── analyzer.py (情感、聚类) ⭐
│   └── reporter.py (洞察报告) ⭐
└── 标准: 功能可用

Phase 3 (灰度)
├── 目标: 平稳切换
├── 时间: 1周
└── 标准: 无数据丢失

Phase 4 (清理)
├── 目标: 删除 v2.0
├── 时间: 1周
└── 标准: 稳定运行
```

### 关键决策

| 决策 | Phase 1 | Phase 2 | 原因 |
|------|:-------:|:-------:|------|
| Session 自动提取 | ✅ | - | 核心痛点，必须解决 |
| 复用 memory_search | ✅ | - | 减少代码，提升质量 |
| 情感分析 | - | ✅ | 增强功能，可延后 |
| 主题聚类 | - | ✅ | 增强功能，可延后 |

### 风险缓解

| 风险 | 缓解措施 |
|------|---------|
| Session 丢失 | Phase 1 优先实现提取合并 |
| 数据不一致 | Health 检查覆盖率 |
| 搜索不准确 | 保留直接读取作为 fallback |

---

*文档版本: 3.0.0*  
*最后更新: 2026-03-13*  
*状态: 设计阶段 - Phase 1 就绪*