# PostgreSQL 核心操作

> 文档类型: 学习笔记
> 创建时间: 2026-03-22
> 阶段: 阶段 2 - 核心操作

---

## 1. 数据类型详解

### 1.1 数值类型

| 类型 | 存储大小 | 范围 | 用途 |
|------|---------|------|------|
| `SMALLINT` | 2 字节 | -32768 到 +32767 | 小范围整数 |
| `INTEGER` | 4 字节 | -21亿 到 +21亿 | 常规整数 |
| `BIGINT` | 8 字节 | -9百亿亿 到 +9百亿亿 | 大整数（ID、计数）|
| `NUMERIC(p,s)` | 可变 | 精确小数 | 金额、精确计算 |
| `REAL` | 4 字节 | 6位精度浮点 | 科学计算 |
| `DOUBLE` | 8 字节 | 15位精度浮点 | 高精度浮点 |

```sql
-- 金额计算必须用 NUMERIC，避免浮点误差
CREATE TABLE orders (
    id      BIGINT PRIMARY KEY,
    amount  NUMERIC(10, 2),  -- 最多10位数字，2位小数
    tax     NUMERIC(10, 4)   -- 税率，4位小数
);
```

### 1.2 字符串类型

| 类型 | 特点 | 适用场景 |
|------|------|---------|
| `CHAR(n)` | 固定长度，空格补齐 | 固定格式（如邮编）|
| `VARCHAR(n)` | 变长，最多 n 字符 | 用户名、标题 |
| `TEXT` | 无限制长度 | 文章内容、日志 |

```sql
-- 推荐：用 TEXT 代替 VARCHAR，性能无差别
CREATE TABLE articles (
    title   TEXT,  -- 标题
    content TEXT   -- 内容，无长度限制
);
```

### 1.3 日期时间类型

| 类型 | 精度 | 时区 | 示例 |
|------|------|------|------|
| `DATE` | 天 | 无 | '2024-03-22' |
| `TIME` | 微秒 | 无 | '16:11:30' |
| `TIMESTAMP` | 微秒 | 无 | '2024-03-22 16:11:30' |
| `TIMESTAMPTZ` | 微秒 | 有 | '2024-03-22 16:11:30+08' |

```sql
-- 推荐：使用 TIMESTAMPTZ（带时区）
CREATE TABLE events (
    name      TEXT,
    start_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 查询特定时区
SELECT name, start_at AT TIME ZONE 'Asia/Shanghai' FROM events;
```

---

## 2. 表设计最佳实践

### 2.1 设计原则

```
┌─────────────────────────────────────────┐
│           表设计三范式                    │
├─────────────────────────────────────────┤
│ 1NF: 每列原子性，不可再分割               │
│ 2NF: 非主键列完全依赖主键                  │
│ 3NF: 消除传递依赖，非主键不依赖其他非主键   │
└─────────────────────────────────────────┘
```

### 2.2 字段设计建议

| 建议 | 说明 | 示例 |
|------|------|------|
| **主键用 BIGINT** | 自增 ID，避免 INT 溢出 | `id BIGSERIAL PRIMARY KEY` |
| **金额用 NUMERIC** | 精确计算，无浮点误差 | `price NUMERIC(19,4)` |
| **时间用 TIMESTAMPTZ** | 带时区，避免时区问题 | `created_at TIMESTAMPTZ` |
| **状态用 SMALLINT** | 节省空间 | `status SMALLINT DEFAULT 0` |
| **JSON 用 JSONB** | 二进制存储，支持索引 | `metadata JSONB` |
| **软删除** | 保留数据，标记删除 | `deleted_at TIMESTAMPTZ` |

### 2.3 完整示例：电商订单表

```sql
CREATE TABLE orders (
    -- 主键
    id              BIGSERIAL PRIMARY KEY,
    
    -- 外键
    user_id         BIGINT NOT NULL REFERENCES users(id),
    
    -- 订单信息
    order_no        VARCHAR(32) UNIQUE NOT NULL,  -- 订单号
    status          SMALLINT DEFAULT 0,           -- 0待支付 1已支付 2已发货 3已完成
    total_amount    NUMERIC(19, 4) NOT NULL,      -- 订单总金额
    
    -- 地址信息（JSONB 存储灵活）
    address         JSONB,
    
    -- 时间戳
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    paid_at         TIMESTAMPTZ,                  -- 支付时间（可为空）
    deleted_at      TIMESTAMPTZ,                  -- 软删除标记
    
    -- 约束
    CONSTRAINT chk_amount CHECK (total_amount >= 0)
);

-- 常用查询字段加索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

---

## 3. 查询进阶

### 3.1 JOIN 连接查询

```sql
-- 用户 + 订单（一对多）
SELECT 
    u.username,
    o.order_no,
    o.total_amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.status = 1;

-- 左连接：所有用户，包括没有订单的
SELECT 
    u.username,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;
```

### 3.2 子查询

```sql
-- 查询消费最多的用户
SELECT username
FROM users
WHERE id = (
    SELECT user_id 
    FROM orders 
    GROUP BY user_id 
    ORDER BY SUM(total_amount) DESC 
    LIMIT 1
);

-- 查询有未支付订单的用户
SELECT * FROM users
WHERE id IN (
    SELECT DISTINCT user_id 
    FROM orders 
    WHERE status = 0
);
```

### 3.3 窗口函数（PostgreSQL 强项）

```sql
-- 用户订单排名（每个用户的订单按金额排名）
SELECT 
    user_id,
    order_no,
    total_amount,
    RANK() OVER (
        PARTITION BY user_id 
        ORDER BY total_amount DESC
    ) as rank_in_user
FROM orders;

-- 累计销售额
SELECT 
    DATE(created_at) as date,
    SUM(total_amount) as daily_amount,
    SUM(SUM(total_amount)) OVER (ORDER BY DATE(created_at)) as running_total
FROM orders
GROUP BY DATE(created_at);
```

---

## 4. 索引优化

### 4.1 索引类型

| 类型 | 适用场景 | 语法 |
|------|---------|------|
| **B-tree** | 默认，等值、范围查询 | `CREATE INDEX idx ON table(col)` |
| **Hash** | 等值查询（不常用） | `CREATE INDEX idx ON table USING HASH(col)` |
| **GIN** | JSONB、数组、全文搜索 | `CREATE INDEX idx ON table USING GIN(col)` |
| **GiST** | 地理数据、范围类型 | `CREATE INDEX idx ON table USING GiST(col)` |

### 4.2 索引最佳实践

```sql
-- 1. 主键自动有索引（唯一索引）
-- 2. 外键建议加索引
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 3. 常用查询条件加索引
CREATE INDEX idx_orders_status_created_at 
ON orders(status, created_at);

-- 4. JSONB 字段用 GIN 索引
CREATE INDEX idx_orders_address ON orders USING GIN(address);

-- 5. 部分索引（只索引部分数据，节省空间）
CREATE INDEX idx_orders_unpaid ON orders(user_id) 
WHERE status = 0;

-- 6. 查看查询是否使用索引
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE user_id = 123;
```

---

## 5. 事务控制

```sql
-- 转账示例：保证原子性
BEGIN;

-- 扣款
UPDATE accounts 
SET balance = balance - 100 
WHERE id = 1 AND balance >= 100;

-- 检查是否扣款成功
IF NOT FOUND THEN
    ROLLBACK;
    RAISE EXCEPTION '余额不足';
END IF;

-- 加款
UPDATE accounts 
SET balance = balance + 100 
WHERE id = 2;

COMMIT;
```

### 事务隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 | 适用场景 |
|------|------|-----------|------|---------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ | 很少使用 |
| READ COMMITTED | ✗ | ✓ | ✓ | **默认，推荐** |
| REPEATABLE READ | ✗ | ✗ | ✓ | 报表查询 |
| SERIALIZABLE | ✗ | ✗ | ✗ | 严格一致性 |

```sql
-- 设置事务隔离级别
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

---

## 6. 关键要点总结

1. **数据类型选择**: 金额用 `NUMERIC`，时间用 `TIMESTAMPTZ`，字符串用 `TEXT`
2. **表设计**: 主键用 `BIGSERIAL`，软删除用 `deleted_at`，外键加索引
3. **查询优化**: 善用 JOIN、子查询、窗口函数
4. **索引策略**: 针对性创建，避免过多，用 EXPLAIN 分析
5. **事务控制**: 保证数据一致性，选择合适的隔离级别

---

*文档路径: /home/node/.openclaw/workspace/docs/postgresql-core-operations.md*
