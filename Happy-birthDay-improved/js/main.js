/**
 * 主程序入口
 * 协调所有模块，控制动画流程
 */

const App = (function() {
    'use strict';
    
    let currentMessageIndex = 0;
    let isAnimating = false;
    let messageInterval;
    let countdownInterval;
    
    /**
     * 初始化应用
     */
    function init() {
        console.log('🎂 Happy-birthDay initializing...');
        
        // 初始化画布
        Canvas.init('.canvas');
        
        // 初始化粒子系统
        Particles.init();
        
        // 初始化音频
        AudioManager.init();
        
        // 设置主题
        applyTheme();
        
        // 加载头像
        loadAvatar();
        
        // 绑定事件
        bindEvents();
        
        // 开始动画循环
        Canvas.loop(function() {
            Particles.update();
            Particles.render();
        });
        
        // 开始消息序列
        startMessageSequence();
        
        // 开始倒计时更新
        startCountdown();
        
        // 添加 body-ready 类
        document.body.classList.add('body--ready');
        
        console.log('🎉 Happy-birthDay initialized successfully!');
    }
    
    /**
     * 应用主题配置
     */
    function applyTheme() {
        const theme = CONFIG.theme;
        
        // 设置背景
        if (theme.backgroundType === 'gradient') {
            document.body.style.background = `linear-gradient(to bottom, ${theme.gradient.start}, ${theme.gradient.end})`;
        } else {
            document.body.style.background = theme.solidColor;
        }
        
        // 设置文字颜色
        document.querySelectorAll('.text').forEach(el => {
            el.style.color = theme.textColor;
        });
        
        // 设置头像边框
        const logo = document.getElementById('logo');
        if (logo) {
            logo.style.borderColor = theme.avatarBorder;
        }
    }
    
    /**
     * 加载头像
     */
    function loadAvatar() {
        const logo = document.getElementById('logo');
        if (!logo) return;
        
        // 设置头像源
        if (CONFIG.person.avatar) {
            logo.src = CONFIG.person.avatar;
        }
        
        // 头像加载错误处理
        logo.addEventListener('error', function() {
            console.log('Avatar load failed, using default');
            // 可以设置默认头像
            logo.src = 'data:image/svg+xml,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="50" fill="#ddd"/>
                    <text x="50" y="60" text-anchor="middle" font-size="40" fill="#999">🎂</text>
                </svg>
            `);
        });
    }
    
    /**
     * 绑定事件
     */
    function bindEvents() {
        // 点击画布创建粒子
        const canvas = document.querySelector('.canvas');
        if (canvas) {
            canvas.addEventListener('click', function(e) {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // 在点击位置创建烟花效果
                createFirework(x, y);
            });
        }
        
        // 键盘快捷键
        document.addEventListener('keydown', function(e) {
            switch(e.key) {
                case ' ': // 空格键切换音乐
                    e.preventDefault();
                    AudioManager.toggle();
                    break;
                case 'ArrowRight': // 右箭头下一个消息
                    nextMessage();
                    break;
                case 'ArrowLeft': // 左箭头上一个消息
                    previousMessage();
                    break;
                case 'r': // R键重置
                case 'R':
                    resetSequence();
                    break;
            }
        });
        
        // 触摸支持
        let touchStartX = 0;
        document.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', function(e) {
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > 50) { // 滑动距离阈值
                if (diff > 0) {
                    nextMessage(); // 左滑下一个
                } else {
                    previousMessage(); // 右滑上一个
                }
            }
        });
    }
    
    /**
     * 开始消息序列
     */
    function startMessageSequence() {
        showMessage(0);
        
        messageInterval = setInterval(function() {
            nextMessage();
        }, CONFIG.animation.textInterval);
    }
    
    /**
     * 显示指定消息
     */
    function showMessage(index) {
        if (index < 0 || index >= CONFIG.messages.length) return;
        
        currentMessageIndex = index;
        const message = CONFIG.messages[index];
        
        // 清除现有粒子
        Particles.clear();
        
        // 处理特殊指令
        if (message.startsWith('#')) {
            handleCommand(message);
        } else {
            // 显示文字
            Particles.createText(message, function() {
                console.log('Text animation complete:', message);
            });
            updateTextDisplay(message);
        }
    }
    
    /**
     * 处理特殊指令
     */
    function handleCommand(command) {
        const parts = command.split(' ');
        const cmd = parts[0];
        const arg = parts[1];
        
        switch(cmd) {
            case '#countdown':
                // 倒计时
                const seconds = parseInt(arg) || 3;
                startCountdownAnimation(seconds);
                break;
                
            case '#rectangle':
                // 绘制矩形
                const rectSize = arg ? arg.split('x').map(Number) : [15, 15];
                Particles.createShape('rectangle', {
                    size: Math.max(rectSize[0], rectSize[1]) * 10
                });
                updateTextDisplay('矩形');
                break;
                
            case '#circle':
                // 绘制圆形
                const radius = parseInt(arg) || 12;
                Particles.createShape('circle', { size: radius * 10 });
                updateTextDisplay('圆形');
                break;
                
            case '#time':
                // 显示当前时间
                const time = Countdown.getCurrentTime();
                Particles.createText(time);
                updateTextDisplay('当前时间: ' + time);
                break;
                
            case '#heart':
                // 爱心
                Particles.createShape('heart', { size: 150 });
                updateTextDisplay('❤️');
                break;
                
            case '#star':
                // 星星
                Particles.createShape('star', { size: 120 });
                updateTextDisplay('⭐');
                break;
                
            case '#firework':
                // 烟花效果
                createFirework();
                updateTextDisplay('🎆');
                break;
                
            default:
                console.log('Unknown command:', command);
        }
    }
    
    /**
     * 倒计时动画
     */
    function startCountdownAnimation(seconds) {
        let count = seconds;
        const textEl = document.querySelector('.text-main');
        
        const update = function() {
            if (count > 0) {
                if (textEl) textEl.textContent = count;
                Particles.createText(String(count));
                count--;
                setTimeout(update, 1000);
            } else {
                if (textEl) textEl.textContent = '开始！';
                Particles.createText('开始！');
                createFirework();
            }
        };
        
        update();
    }
    
    /**
     * 创建烟花效果
     */
    function createFirework(x, y) {
        const area = Canvas.getArea();
        const centerX = x || Math.random() * area.w;
        const centerY = y || Math.random() * area.h * 0.6;
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dfe6e9'];
        
        // 创建爆炸粒子
        for (let i = 0; i < 30; i++) {
            const angle = (Math.PI * 2 / 30) * i;
            const speed = Math.random() * 5 + 2;
            
            Particles.create({
                x: centerX,
                y: centerY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                z: Math.random() * 4 + 2,
                color: colors[Math.floor(Math.random() * colors.length)],
                life: 1,
                decay: 0.02,
                type: 'firework'
            });
        }
    }
    
    /**
     * 更新文字显示
     */
    function updateTextDisplay(text) {
        const mainText = document.querySelector('.text-main');
        if (mainText) {
            mainText.textContent = text;
        }
    }
    
    /**
     * 开始倒计时显示
     */
    function startCountdown() {
        const countdownEl = document.querySelector('.text-countdown');
        if (!countdownEl) return;
        
        // 立即更新一次
        updateCountdown();
        
        // 每秒更新
        countdownInterval = setInterval(updateCountdown, 1000);
    }
    
    /**
     * 更新倒计时显示
     */
    function updateCountdown() {
        const countdownEl = document.querySelector('.text-countdown');
        if (!countdownEl) return;
        
        const birthday = Countdown.parseDate(CONFIG.person.birthday);
        if (!birthday) {
            countdownEl.textContent = '';
            return;
        }
        
        const diff = Countdown.calculate(birthday);
        if (diff) {
            countdownEl.textContent = Countdown.format(diff);
        }
    }
    
    /**
     * 显示下一条消息
     */
    function nextMessage() {
        const nextIndex = (currentMessageIndex + 1) % CONFIG.messages.length;
        showMessage(nextIndex);
    }
    
    /**
     * 显示上一条消息
     */
    function previousMessage() {
        const prevIndex = (currentMessageIndex - 1 + CONFIG.messages.length) % CONFIG.messages.length;
        showMessage(prevIndex);
    }
    
    /**
     * 重置消息序列
     */
    function resetSequence() {
        currentMessageIndex = 0;
        showMessage(0);
    }
    
    /**
     * 停止动画
     */
    function stop() {
        if (messageInterval) {
            clearInterval(messageInterval);
            messageInterval = null;
        }
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
        }
    }
    
    /**
     * 重新开始
     */
    function restart() {
        stop();
        resetSequence();
        startMessageSequence();
        startCountdown();
    }
    
    // 公开 API
    return {
        init: init,
        nextMessage: nextMessage,
        previousMessage: previousMessage,
        resetSequence: resetSequence,
        restart: restart,
        stop: stop
    };
})();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 等待所有脚本加载
    if (typeof CONFIG !== 'undefined' && 
        typeof Canvas !== 'undefined' && 
        typeof Particles !== 'undefined' &&
        typeof Countdown !== 'undefined' &&
        typeof AudioManager !== 'undefined') {
        App.init();
    } else {
        console.error('Required modules not loaded');
    }
});