/**
 * Canvas 绘制模块
 * 处理画布初始化、绘制和动画循环
 */

const Canvas = (function() {
    'use strict';
    
    let canvas, context;
    let renderFn;
    let dpr = window.devicePixelRatio || 1;
    
    // 请求动画帧的兼容处理
    const requestFrame = window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame ||
        window.oRequestAnimationFrame ||
        window.msRequestAnimationFrame ||
        function(callback) {
            window.setTimeout(callback, 1000 / CONFIG.animation.fps);
        };
    
    /**
     * 初始化画布
     * @param {string} selector - CSS 选择器
     */
    function init(selector) {
        canvas = document.querySelector(selector);
        if (!canvas) {
            console.error('Canvas element not found:', selector);
            return;
        }
        
        context = canvas.getContext('2d');
        if (!context) {
            console.error('Could not get 2D context');
            return;
        }
        
        // 启用抗锯齿
        context.imageSmoothingEnabled = true;
        context.imageSmoothingQuality = 'high';
        
        // 调整画布尺寸
        adjustCanvas();
        
        // 监听窗口大小变化
        window.addEventListener('resize', debounce(adjustCanvas, 100));
        
        // 监听设备方向变化
        window.addEventListener('orientationchange', function() {
            setTimeout(adjustCanvas, 300);
        });
        
        console.log('Canvas initialized successfully');
    }
    
    /**
     * 调整画布尺寸以适应窗口
     */
    function adjustCanvas() {
        if (!canvas) return;
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // 移动端优化
        const isMobile = width <= CONFIG.responsive.mobile;
        const padding = isMobile ? 20 : 100;
        
        // 设置画布尺寸（考虑高清屏）
        canvas.width = (width - padding) * dpr;
        canvas.height = (height - 30) * dpr;
        
        // 设置显示尺寸
        canvas.style.width = (width - padding) + 'px';
        canvas.style.height = (height - 30) + 'px';
        
        // 缩放上下文以匹配 DPR
        context.scale(dpr, dpr);
        
        console.log('Canvas resized:', width, 'x', height, 'DPR:', dpr);
    }
    
    /**
     * 动画循环
     * @param {Function} fn - 渲染函数
     */
    function loop(fn) {
        renderFn = !renderFn ? fn : renderFn;
        clearFrame();
        renderFn();
        requestFrame.call(window, loop.bind(this));
    }
    
    /**
     * 清除画布
     */
    function clearFrame() {
        if (!context || !canvas) return;
        context.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);
    }
    
    /**
     * 获取画布区域尺寸
     * @returns {Object} 宽度和高度
     */
    function getArea() {
        if (!canvas) return { w: 0, h: 0 };
        return {
            w: canvas.width / dpr,
            h: canvas.height / dpr
        };
    }
    
    /**
     * 绘制圆形
     * @param {Object} p - 位置对象 {x, y, z}
     * @param {Object} c - 颜色对象
     */
    function drawCircle(p, c) {
        if (!context) return;
        context.fillStyle = c.render ? c.render() : c;
        context.beginPath();
        context.arc(p.x, p.y, p.z, 0, 2 * Math.PI, true);
        context.closePath();
        context.fill();
    }
    
    /**
     * 绘制矩形
     * @param {Object} p - 位置对象
     * @param {Object} size - 尺寸对象 {w, h}
     * @param {Object} c - 颜色对象
     */
    function drawRect(p, size, c) {
        if (!context) return;
        context.fillStyle = c.render ? c.render() : c;
        context.fillRect(p.x, p.y, size.w, size.h);
    }
    
    /**
     * 绘制文字
     * @param {string} text - 文字内容
     * @param {Object} p - 位置对象
     * @param {Object} style - 样式对象
     */
    function drawText(text, p, style) {
        if (!context) return;
        context.font = style.font || '20px sans-serif';
        context.fillStyle = style.color || '#fff';
        context.textAlign = style.align || 'center';
        context.textBaseline = style.baseline || 'middle';
        context.fillText(text, p.x, p.y);
    }
    
    /**
     * 绘制心形
     * @param {Object} p - 中心位置
     * @param {number} size - 大小
     * @param {Object} c - 颜色
     */
    function drawHeart(p, size, c) {
        if (!context) return;
        context.fillStyle = c.render ? c.render() : c;
        context.beginPath();
        const x = p.x;
        const y = p.y;
        const s = size;
        
        context.moveTo(x, y + s / 4);
        context.quadraticCurveTo(x, y, x + s / 4, y);
        context.quadraticCurveTo(x + s / 2, y, x + s / 2, y + s / 4);
        context.quadraticCurveTo(x + s / 2, y, x + s * 3 / 4, y);
        context.quadraticCurveTo(x + s, y, x + s, y + s / 4);
        context.quadraticCurveTo(x + s, y + s / 2, x + s * 3 / 4, y + s * 3 / 4);
        context.lineTo(x + s / 2, y + s);
        context.lineTo(x + s / 4, y + s * 3 / 4);
        context.quadraticCurveTo(x, y + s / 2, x, y + s / 4);
        context.closePath();
        context.fill();
    }
    
    /**
     * 绘制星星
     * @param {Object} p - 中心位置
     * @param {number} size - 大小
     * @param {Object} c - 颜色
     * @param {number} points - 角的数量
     */
    function drawStar(p, size, c, points = 5) {
        if (!context) return;
        context.fillStyle = c.render ? c.render() : c;
        context.beginPath();
        
        const outerRadius = size;
        const innerRadius = size / 2;
        
        for (let i = 0; i < points * 2; i++) {
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const angle = (i * Math.PI) / points - Math.PI / 2;
            const x = p.x + radius * Math.cos(angle);
            const y = p.y + radius * Math.sin(angle);
            
            if (i === 0) {
                context.moveTo(x, y);
            } else {
                context.lineTo(x, y);
            }
        }
        
        context.closePath();
        context.fill();
    }
    
    /**
     * 防抖函数
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // 公开 API
    return {
        init: init,
        loop: loop,
        adjustCanvas: adjustCanvas,
        clearFrame: clearFrame,
        getArea: getArea,
        drawCircle: drawCircle,
        drawRect: drawRect,
        drawText: drawText,
        drawHeart: drawHeart,
        drawStar: drawStar
    };
})();