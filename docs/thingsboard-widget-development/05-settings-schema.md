# 第五章：Settings Schema 配置系统

## 5.1 什么是 Settings Schema？

Settings Schema 使用 **JSON Schema** 定义 Widget 的配置表单，ThingsBoard 会自动生成对应的 UI 界面。

```
Settings Schema (JSON)
        ↓
react-schema-form builder
        ↓
自动生成 UI 表单
        ↓
用户配置 → 存储到 ctx.settings
        ↓
JavaScript 代码中使用
```

## 5.2 基础结构

```json
{
    "schema": {
        "type": "object",
        "title": "Settings",
        "properties": {
            // 字段定义...
        },
        "required": ["fieldName"]
    },
    "form": [
        // 表单布局...
    ]
}
```

## 5.3 支持的字段类型

### 基础类型

| JSON Schema 类型 | 生成的控件 | 示例 |
|------------------|-----------|------|
| `string` | 文本输入框 | `"type": "string"` |
| `number` | 数字输入框 | `"type": "number"` |
| `boolean` | 复选框 | `"type": "boolean"` |
| `integer` | 整数输入框 | `"type": "integer"` |

### 表单控件类型

在 `form` 数组中通过 `type` 指定：

| 类型 | 说明 | 示例 |
|------|------|------|
| `rc-select` | 下拉选择 | `"type": "rc-select"` |
| `color` | 颜色选择器 | `"type": "color"` |
| `image` | 图片选择 | `"type": "image"` |
| `javascript` | JS 代码编辑器 | `"type": "javascript"` |
| `html` | HTML 编辑器 | `"type": "html"` |
| `css` | CSS 编辑器 | `"type": "css"` |

## 5.4 基础示例

```json
{
    "schema": {
        "type": "object",
        "title": "Settings",
        "properties": {
            "cardType": {
                "title": "Card type",
                "type": "string",
                "default": "Average"
            },
            "cardTitle": {
                "title": "Card title",
                "type": "string",
                "default": "Gateways online"
            },
            "showIcon": {
                "title": "Show icon",
                "type": "boolean",
                "default": true
            },
            "maxValue": {
                "title": "Maximum value",
                "type": "number",
                "default": 100
            }
        },
        "required": ["cardType"]
    },
    "form": [
        {
            "key": "cardType",
            "type": "rc-select",
            "multiple": false,
            "items": [
                {"value": "avg", "label": "Average"},
                {"value": "max", "label": "Maximum"},
                {"value": "min", "label": "Minimum"}
            ]
        },
        "cardTitle",
        "showIcon",
        "maxValue"
    ]
}
```

## 5.5 复杂示例

```json
{
    "schema": {
        "type": "object",
        "properties": {
            "button": {
                "title": "Button settings",
                "type": "object",
                "properties": {
                    "color": {
                        "title": "Primary color",
                        "type": "string",
                        "default": "#545454"
                    },
                    "backgroundColor": {
                        "title": "Background color",
                        "type": "string",
                        "default": null
                    }
                }
            },
            "markerImage": {
                "title": "Custom marker image",
                "type": "string"
            },
            "markerImageSize": {
                "title": "Custom marker image size (px)",
                "type": "number",
                "default": 34
            },
            "useMarkerImageFunction": {
                "title": "Use marker image function",
                "type": "boolean",
                "default": false
            },
            "markerImageFunction": {
                "title": "Marker image function: f(data, images, dsData, dsIndex)",
                "type": "string"
            },
            "markerImages": {
                "title": "Marker images",
                "type": "array",
                "items": {
                    "title": "Marker image",
                    "type": "string"
                }
            }
        },
        "required": []
    },
    "form": [
        [
            {
                "key": "button",
                "items": [
                    {
                        "key": "button.color",
                        "type": "color"
                    },
                    {
                        "key": "button.backgroundColor",
                        "type": "color"
                    }
                ]
            }
        ],
        [
            "useMarkerImageFunction",
            {
                "key": "markerImage",
                "type": "image",
                "condition": "model.useMarkerImageFunction !== true"
            },
            {
                "key": "markerImageSize",
                "condition": "model.useMarkerImageFunction !== true"
            },
            {
                "key": "markerImageFunction",
                "type": "javascript",
                "helpId": "widget/lib/map/marker_image_fn",
                "condition": "model.useMarkerImageFunction === true"
            },
            {
                "key": "markerImages",
                "items": [
                    {
                        "key": "markerImages[]",
                        "type": "image"
                    }
                ],
                "condition": "model.useMarkerImageFunction === true"
            }
        ]
    ],
    "groupInfoes": [
        {
            "formIndex": 0,
            "GroupTitle": "Button Style Settings"
        },
        {
            "formIndex": 1,
            "GroupTitle": "Marker Settings"
        }
    ]
}
```

## 5.6 条件显示

```json
{
    "form": [
        "useCustomFunction",
        {
            "key": "customValue",
            "condition": "model.useCustomFunction === true"
        },
        {
            "key": "defaultValue",
            "condition": "model.useCustomFunction !== true"
        }
    ]
}
```

## 5.7 数组类型

```json
{
    "schema": {
        "properties": {
            "items": {
                "title": "Items",
                "type": "array",
                "items": {
                    "title": "Item",
                    "type": "object",
                    "properties": {
                        "name": {
                            "title": "Name",
                            "type": "string"
                        },
                        "value": {
                            "title": "Value",
                            "type": "number"
                        }
                    }
                }
            }
        }
    },
    "form": [
        {
            "key": "items",
            "items": [
                "items[].name",
                "items[].value"
            ]
        }
    ]
}
```

## 5.8 分组布局

```json
{
    "form": [
        [
            "field1",
            "field2"
        ],
        [
            "field3",
            "field4"
        ]
    ],
    "groupInfoes": [
        {
            "formIndex": 0,
            "GroupTitle": "Group 1"
        },
        {
            "formIndex": 1,
            "GroupTitle": "Group 2"
        }
    ]
}
```

## 5.9 在 JavaScript 中使用 Settings

```javascript
self.onInit = function() {
    // 获取设置值
    var cardTitle = ctx.settings.cardTitle;      // "Gateways online"
    var cardType = ctx.settings.cardType;        // "Average"
    var showIcon = ctx.settings.showIcon;        // true
    var maxValue = ctx.settings.maxValue;        // 100
    
    // 应用设置
    $('#title', ctx.$container).text(cardTitle);
    
    // 根据设置初始化
    if (showIcon) {
        $('#icon', ctx.$container).show();
    } else {
        $('#icon', ctx.$container).hide();
    }
};
```

## 5.10 Data Key Settings Schema

```json
{
    "schema": {
        "type": "object",
        "properties": {
            "threshold": {
                "title": "告警阈值",
                "type": "number",
                "default": 100
            },
            "enabled": {
                "title": "启用告警",
                "type": "boolean",
                "default": true
            }
        }
    },
    "form": [
        "threshold",
        "enabled"
    ]
}
```

在 JavaScript 中访问：
```javascript
self.onDataUpdated = function() {
    // 获取数据键设置
    var dataKey = ctx.data[0].dataKey;
    var settings = dataKey.settings || {};
    
    var threshold = settings.threshold || 100;
    var enabled = settings.enabled !== false;
    
    if (enabled && value > threshold) {
        // 触发告警
    }
};
```

---

## 下一步

继续学习 [第六章：完整实战示例](./06-practical-examples.md)