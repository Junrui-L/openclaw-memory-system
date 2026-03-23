# PostgreSQL 基础入门

> 文档类型: 学习笔记
> 创建时间: 2026-03-22
> 阶段: 阶段 1 - 基础入门

---

## 1. PostgreSQL 简介

### 什么是 PostgreSQL？

PostgreSQL（简称 Postgres）是一个开源的关系型数据库管理系统，始于 1986 年（加州大学伯克利分校），是世界上最先进的开源数据库之一。

### 核心特点

| 特点 | 说明 |
|------|------|
| **开源免费** | BSD 许可证，可自由使用和修改 |
| **标准兼容** | 高度兼容 SQL 标准 |
| **可扩展** | 支持自定义数据类型、函数、操作符 |
| **高级特性** | 支持 JSON、全文搜索、地理信息、并发控制 |
| **稳定可靠** | 生产环境广泛使用，数据安全有保障 |

### PostgreSQL vs MySQL

| 对比项 | PostgreSQL | MySQL |
|--------|-----------|-------|
| **定位** | 企业级、功能丰富 | 轻量、易用 |
| **复杂查询** | 更强大（CTE、窗口函数） | 基础支持 |
| **数据完整性** | 更严格（外键、约束） | 相对灵活 |
| **扩展性** | 极强（自定义类型、索引） | 有限 |
| **JSON 支持** | JSONB（二进制、高效） | JSON（文本存储） |
| **适用场景** | 复杂业务、数据分析 | 简单应用、Web 网站 |

### 适用场景

✅ **适合使用 PostgreSQL**：
- 复杂业务逻辑（金融、电商）
- 地理信息系统（GIS）
- 需要 JSON/NoSQL 混合能力
- 数据仓库和分析
- 高并发事务处理

---

## 2. 基础概念

### 数据库核心概念

```
┌─────────────────────────────────────┐
│           PostgreSQL 实例            │
│  ┌─────────────────────────────┐    │
│  │        数据库 mydb           │    │
│  │  ┌─────────────────────┐    │    │
│  │  │      表 users       │    │    │
│  │  │  ┌───────────────┐  │    │    │
│  │  │  │ id │ name │ age │  │    │    │
│  │  │  ├────┼──────┼─────┤  │    │    │
│  │  │  │ 1  │ 张三 │ 25  │  │    │    │
│  │  │  │ 2  │ 李四 │ 30  │  │    │    │
│  │  │  └────┴──────┴─────┘  │    │    │
│  │  └─────────────────────┘    │    │
│  │  ┌─────────────────────┐    │    │
│  │  │      表 orders      │    │    │
│  │  │  ...                │    │    │
│  │  └─────────────────────┘    │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### 核心术语

| 术语 | 解释 | 类比 |
|------|------|------|
| **数据库 (Database)** | 数据的集合，独立的数据空间 | 一个 Excel 文件 |
| **表 (Table)** | 存储同类数据的结构 | Excel 中的一个 Sheet |
| **行 (Row)** | 一条记录 | Excel 中的一行 |
| **列 (Column)** | 一个字段/属性 | Excel 中的一列 |
| **主键 (Primary Key)** | 唯一标识每行的字段 | 身份证号 |
| **外键 (Foreign Key)** | 关联其他表的字段 | 引用其他表的 ID |

---

## 3. 数据类型

### 常用数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **INTEGER** | 整数 | 1, 100, -50 |
| **BIGINT** | 大整数 | 9223372036854775807 |
| **NUMERIC** | 精确小数 | NUMERIC(10,2) → 12345678.90 |
| **VARCHAR(n)** | 变长字符串 | 'Hello', '中文' |
| **TEXT** | 长文本 | 文章、描述 |
| **BOOLEAN** | 布尔值 | TRUE, FALSE |
| **DATE** | 日期 | '2024-03-22' |
| **TIMESTAMP** | 日期时间 | '2024-03-22 16:03:00' |
| **JSONB** | JSON 二进制 | '{"key": "value"}' |
| **ARRAY** | 数组 | '{1, 2, 3}' |

### 特殊类型（PostgreSQL 特有）

| 类型 | 说明 | 示例 |
|------|------|------|
| **UUID** | 全局唯一标识符 | 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' |
| **INET** | IP 地址 | '192.168.1.1' |
| **CIDR** | IP 网络 | '192.168.1.0/24' |
| **GEOMETRY** | 几何数据 | 点、线、多边形（PostGIS 扩展） |

---

## 4. 基本 SQL 语句

### 4.1 创建数据库和表

```sql
-- 创建数据库
CREATE DATABASE mydb;

-- 创建表
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,      -- 自增主键
    username    VARCHAR(50) NOT NULL,    -- 用户名，非空
    email       VARCHAR(100) UNIQUE,     -- 邮箱，唯一
    age         INTEGER CHECK (age > 0), -- 年龄，必须大于0
    created_at  TIMESTAMP DEFAULT NOW()  -- 创建时间，默认当前时间
);
```

### 4.2 插入数据 (INSERT)

```sql
-- 插入单条
INSERT INTO users (username, email, age) 
VALUES ('张三', 'zhangsan@example.com', 25);

-- 插入多条
INSERT INTO users (username, email, age) 
VALUES 
    ('李四', 'lisi@example.com', 30),
    ('王五', 'wangwu@example.com', 28);
```

### 4.3 查询数据 (SELECT)

```sql
-- 查询所有
SELECT * FROM users;

-- 查询特定列
SELECT username, email FROM users;

-- 条件查询
SELECT * FROM users WHERE age > 25;

-- 排序
SELECT * FROM users ORDER BY age DESC;

-- 分页
SELECT * FROM users LIMIT 10 OFFSET 20;
```

### 4.4 更新数据 (UPDATE)

```sql
-- 更新单条
UPDATE users 
SET age = 26 
WHERE username = '张三';

-- 更新多条
UPDATE users 
SET age = age + 1 
WHERE age < 30;
```

### 4.5 删除数据 (DELETE)

```sql
-- 删除单条
DELETE FROM users WHERE id = 1;

-- 删除所有（危险！）
DELETE FROM users;
```

---

## 5. 练习场景

### 博客系统数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) NOT NULL,
    email       VARCHAR(100) UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 文章表
CREATE TABLE posts (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    title       VARCHAR(200) NOT NULL,
    content     TEXT,
    published   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 标签表
CREATE TABLE tags (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) UNIQUE
);

-- 文章-标签关联表
CREATE TABLE post_tags (
    post_id     INTEGER REFERENCES posts(id),
    tag_id      INTEGER REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

-- 评论表
CREATE TABLE comments (
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER REFERENCES posts(id),
    user_id     INTEGER REFERENCES users(id),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

---

## 6. 关键要点总结

1. **PostgreSQL 优势**: 功能强大、标准兼容、扩展性好
2. **数据类型丰富**: 支持 JSONB、数组、UUID 等高级类型
3. **SQL 标准**: 语法标准，易学易用
4. **表设计**: 注意主键、外键、约束的使用

---

*文档路径: /home/node/.openclaw/workspace/docs/postgresql-basics.md*
