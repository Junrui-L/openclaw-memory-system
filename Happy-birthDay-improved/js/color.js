/**
 * 颜色工具模块
 * 处理颜色转换和随机生成
 */

const Color = (function() {
    'use strict';
    
    // 预定义颜色调色板
    const PALETTE = [
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
        '#ffeaa7', '#dfe6e9', '#fd79a8', '#fdcb6e',
        '#6c5ce7', '#a29bfe', '#74b9ff', '#0984e3',
        '#00b894', '#00cec9', '#e17055', '#d63031'
    ];
    
    /**
     * 从十六进制字符串创建颜色对象
     * @param {string} hex - 十六进制颜色值
     * @returns {Object} 颜色对象
     */
    function from(hex) {
        // 处理简写格式 #RGB
        if (hex.length === 4) {
            hex = '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
        }
        
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (!result) {
            console.warn('Invalid color format:', hex);
            return from('#ffffff');
        }
        
        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);
        
        return {
            r: r,
            g: g,
            b: b,
            hex: hex,
            
            /**
             * 渲染为 RGBA 字符串
             * @param {number} alpha - 透明度 (0-1)
             * @returns {string} rgba 字符串
             */
            render: function(alpha) {
                const a = alpha !== undefined ? alpha : 1;
                return `rgba(${this.r}, ${this.g}, ${this.b}, ${a})`;
            },
            
            /**
             * 转换为 RGB 字符串
             * @returns {string} rgb 字符串
             */
            toRGB: function() {
                return `rgb(${this.r}, ${this.g}, ${this.b})`;
            },
            
            /**
             * 变亮
             * @param {number} percent - 百分比
             * @returns {Object} 新颜色对象
             */
            lighten: function(percent) {
                const factor = 1 + percent / 100;
                return fromRGB(
                    Math.min(255, Math.floor(this.r * factor)),
                    Math.min(255, Math.floor(this.g * factor)),
                    Math.min(255, Math.floor(this.b * factor))
                );
            },
            
            /**
             * 变暗
             * @param {number} percent - 百分比
             * @returns {Object} 新颜色对象
             */
            darken: function(percent) {
                const factor = 1 - percent / 100;
                return fromRGB(
                    Math.max(0, Math.floor(this.r * factor)),
                    Math.max(0, Math.floor(this.g * factor)),
                    Math.max(0, Math.floor(this.b * factor))
                );
            }
        };
    }
    
    /**
     * 从 RGB 值创建颜色对象
     * @param {number} r - 红色 (0-255)
     * @param {number} g - 绿色 (0-255)
     * @param {number} b - 蓝色 (0-255)
     * @returns {Object} 颜色对象
     */
    function fromRGB(r, g, b) {
        const hex = '#' + [r, g, b].map(x => {
            const hex = Math.max(0, Math.min(255, x)).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
        return from(hex);
    }
    
    /**
     * 从 HSL 值创建颜色对象
     * @param {number} h - 色相 (0-360)
     * @param {number} s - 饱和度 (0-100)
     * @param {number} l - 亮度 (0-100)
     * @returns {Object} 颜色对象
     */
    function fromHSL(h, s, l) {
        h = h % 360;
        s = Math.max(0, Math.min(100, s)) / 100;
        l = Math.max(0, Math.min(100, l)) / 100;
        
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = l - c / 2;
        
        let r, g, b;
        
        if (h < 60) {
            r = c; g = x; b = 0;
        } else if (h < 120) {
            r = x; g = c; b = 0;
        } else if (h < 180) {
            r = 0; g = c; b = x;
        } else if (h < 240) {
            r = 0; g = x; b = c;
        } else if (h < 300) {
            r = x; g = 0; b = c;
        } else {
            r = c; g = 0; b = x;
        }
        
        return fromRGB(
            Math.round((r + m) * 255),
            Math.round((g + m) * 255),
            Math.round((b + m) * 255)
        );
    }
    
    /**
     * 生成随机颜色
     * @returns {Object} 颜色对象
     */
    function random() {
        const hex = PALETTE[Math.floor(Math.random() * PALETTE.length)];
        return from(hex);
    }
    
    /**
     * 生成随机鲜艳颜色
     * @returns {Object} 颜色对象
     */
    function randomVibrant() {
        const h = Math.random() * 360;
        const s = 70 + Math.random() * 30; // 70-100%
        const l = 50 + Math.random() * 20; // 50-70%
        return fromHSL(h, s, l);
    }
    
    /**
     * 生成渐变颜色
     * @param {string} start - 起始颜色
     * @param {string} end - 结束颜色
     * @param {number} steps - 步数
     * @returns {Array} 颜色数组
     */
    function gradient(start, end, steps) {
        const startColor = from(start);
        const endColor = from(end);
        const colors = [];
        
        for (let i = 0; i < steps; i++) {
            const ratio = i / (steps - 1);
            const r = Math.round(startColor.r + (endColor.r - startColor.r) * ratio);
            const g = Math.round(startColor.g + (endColor.g - startColor.g) * ratio);
            const b = Math.round(startColor.b + (endColor.b - startColor.b) * ratio);
            colors.push(fromRGB(r, g, b));
        }
        
        return colors;
    }
    
    /**
     * 获取调色板中的颜色
     * @param {number} index - 索引
     * @returns {Object} 颜色对象
     */
    function palette(index) {
        const hex = PALETTE[index % PALETTE.length];
        return from(hex);
    }
    
    /**
     * 获取调色板大小
     * @returns {number} 调色板大小
     */
    function paletteSize() {
        return PALETTE.length;
    }
    
    // 公开 API
    return {
        from: from,
        fromRGB: fromRGB,
        fromHSL: fromHSL,
        random: random,
        randomVibrant: randomVibrant,
        gradient: gradient,
        palette: palette,
        paletteSize: paletteSize,
        PALETTE: PALETTE
    };
})();