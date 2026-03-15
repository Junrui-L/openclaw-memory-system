/**
 * Happy-birthDay 配置文件
 * 修改以下配置即可自定义你的生日祝福页面
 */

const CONFIG = {
    // ==================== 目标人物信息 ====================
    person: {
        name: "亲爱的",                    // 显示的名字
        birthday: "1992-09-21",           // 生日日期 (YYYY-MM-DD)
        avatar: "images/avatar.jpg",      // 头像图片路径
        meetDate: null                    // 相识日期 (可选，格式同上)
    },

    // ==================== 显示文字序列 ====================
    // 支持以下特殊指令：
    // #countdown N    - 倒计时 N 秒
    // #rectangle WxH  - 绘制矩形 (如 15x15)
    // #circle R       - 绘制圆形 (如 12)
    // #time           - 显示当前时间
    // #heart          - 爱心形状
    // #firework       - 烟花效果
    // #star           - 星星形状
    messages: [
        "亲爱的",
        "生日快乐哟",
        "愿你永远开心",
        "#heart",
        "#countdown 3",
        "#rectangle 15x15",
        "#circle 12",
        "#time"
    ],

    // ==================== 主题配色 ====================
    theme: {
        // 背景类型: "gradient" (渐变) 或 "solid" (纯色)
        backgroundType: "gradient",
        
        // 渐变色 (backgroundType 为 gradient 时有效)
        gradient: {
            start: "rgb(203, 235, 219)",    // 起始颜色
            end: "rgb(55, 148, 192)"        // 结束颜色
        },
        
        // 纯色背景 (backgroundType 为 solid 时有效)
        solidColor: "#79a8ae",
        
        // 文字颜色
        textColor: "#ed3073",
        
        // 头像边框颜色
        avatarBorder: "#00a0ff"
    },

    // ==================== 倒计时配置 ====================
    countdown: {
        // 显示格式: "full" (完整) 或 "simple" (简单)
        format: "full",
        // 自定义文案
        prefix: "世界已经有你",
        suffix: ""
    },

    // ==================== 动画配置 ====================
    animation: {
        // 点阵最大尺寸
        maxShapeSize: 30,
        // 动画帧率
        fps: 60,
        // 文字切换间隔 (毫秒)
        textInterval: 3000
    },

    // ==================== 音效配置 ====================
    audio: {
        // 是否启用背景音乐
        enabled: false,
        // 音乐文件路径
        music: "audio/birthday.mp3",
        // 自动播放 (部分浏览器可能阻止)
        autoplay: false,
        // 循环播放
        loop: true,
        // 音量 (0-1)
        volume: 0.5
    },

    // ==================== 特效配置 ====================
    effects: {
        // 头像悬停旋转
        avatarRotate: true,
        // 粒子效果
        particles: true,
        // 背景闪烁
        backgroundTwinkle: false
    },

    // ==================== 响应式断点 ====================
    responsive: {
        mobile: 768,    // 手机端最大宽度
        tablet: 1024    // 平板端最大宽度
    }
};

// 防止配置被修改
Object.freeze(CONFIG);
Object.freeze(CONFIG.person);
Object.freeze(CONFIG.theme);
Object.freeze(CONFIG.animation);
Object.freeze(CONFIG.audio);
Object.freeze(CONFIG.effects);
Object.freeze(CONFIG.responsive);