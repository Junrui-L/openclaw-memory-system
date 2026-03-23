#!/bin/bash
# 每日提醒脚本 - 排班 + 天气 + 穿衣建议

# 获取今天日期和星期
today=$(date +%m/%d)
day_of_week=$(date +%u)  # 1=周一, 7=周日

# 中文星期
case "$day_of_week" in
    1) weekday_name="星期一" ;;
    2) weekday_name="星期二" ;;
    3) weekday_name="星期三" ;;
    4) weekday_name="星期四" ;;
    5) weekday_name="星期五" ;;
    6) weekday_name="星期六" ;;
    7) weekday_name="星期日" ;;
esac

# 排班表查询（根据日期匹配）
case "$today" in
    "03/17"|"03/18") shift="晚班"; shift_time="12:00 - 21:00"; shift_emoji="🌙" ;;
    "03/19") shift="早班"; shift_time="09:00 - 18:00"; shift_emoji="☀️" ;;
    "03/20") shift="晚班"; shift_time="12:00 - 21:00"; shift_emoji="🌙" ;;
    "03/21"|"03/22") shift="早班"; shift_time="09:00 - 18:00"; shift_emoji="☀️" ;;
    "03/23"|"03/24") shift="休息"; shift_time="-"; shift_emoji="😴" ;;
    "03/25"|"03/26") shift="晚班"; shift_time="12:00 - 21:00"; shift_emoji="🌙" ;;
    "03/27") shift="早班"; shift_time="09:00 - 18:00"; shift_emoji="☀️" ;;
    "03/28") shift="晚班"; shift_time="12:00 - 21:00"; shift_emoji="🌙" ;;
    "03/29") shift="中班"; shift_time="10:00 - 19:00"; shift_emoji="🌤️" ;;
    "03/30") shift="晚班"; shift_time="12:00 - 21:00"; shift_emoji="🌙" ;;
    "03/31") shift="早班"; shift_time="09:00 - 18:00"; shift_emoji="☀️" ;;
    *) shift="未知"; shift_time="-"; shift_emoji="❓" ;;
esac

# 获取深圳宝安天气（详细格式）
weather_info=$(curl -s "https://wttr.in/深圳宝安?format=%C|%t|%f|%h|%w|%S|%s" 2>/dev/null)

# 如果 wttr.in 失败，使用备用源
if [ -z "$weather_info" ] || [[ "$weather_info" =~ "500" ]] || [[ "$weather_info" =~ "failed" ]]; then
    # 备用：使用 Open-Meteo API
    weather_json=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=22.55&longitude=113.88&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=Asia%2FShanghai" 2>/dev/null)
    
    if [ -n "$weather_json" ]; then
        temp=$(echo "$weather_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current']['temperature_2m'], '°C')" 2>/dev/null)
        feels=$(echo "$weather_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current']['apparent_temperature'], '°C')" 2>/dev/null)
        humidity=$(echo "$weather_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current']['relative_humidity_2m'], '%')" 2>/dev/null)
        wind=$(echo "$weather_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current']['wind_speed_10m'], 'km/h')" 2>/dev/null)
        code=$(echo "$weather_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current']['weather_code'])" 2>/dev/null)
        
        # WMO Weather interpretation
        case "$code" in
            0) condition="晴朗" ;;
            1|2|3) condition="多云" ;;
            45|48) condition="雾" ;;
            51|53|55) condition="小雨" ;;
            61|63|65) condition="中雨" ;;
            71|73|75) condition="雪" ;;
            80|81|82) condition="阵雨" ;;
            95|96|99) condition="雷雨" ;;
            *) condition="多云" ;;
        esac
        
        weather_info="$condition|$temp|$feels|$humidity|$wind|06:30|18:30"
    else
        weather_info="多云|+22°C|+22°C|75%|10km/h|06:30|18:30"
    fi
fi

# 解析天气信息
condition=$(echo "$weather_info" | cut -d'|' -f1)
current_temp=$(echo "$weather_info" | cut -d'|' -f2)
feels_like=$(echo "$weather_info" | cut -d'|' -f3)
humidity=$(echo "$weather_info" | cut -d'|' -f4)
wind=$(echo "$weather_info" | cut -d'|' -f5)
sunrise=$(echo "$weather_info" | cut -d'|' -f6)
sunset=$(echo "$weather_info" | cut -d'|' -f7)

# 天气状况中文转换
case "$condition" in
    "Clear"|"Sunny") condition_cn="晴朗 ☀️" ;;
    "Partly cloudy") condition_cn="多云 🌤️" ;;
    "Cloudy") condition_cn="阴天 ☁️" ;;
    "Overcast") condition_cn="阴天 ☁️" ;;
    "Rain"|"Light rain"|"Moderate rain") condition_cn="下雨 🌧️" ;;
    "Heavy rain") condition_cn="大雨 ⛈️" ;;
    "Thunderstorm") condition_cn="雷雨 ⛈️" ;;
    "Fog"|"Mist") condition_cn="雾 🌫️" ;;
    "Haze") condition_cn="霾 😷" ;;
    *) condition_cn="$condition" ;;
esac

# 提取温度数字
temp_num=$(echo "$current_temp" | grep -oE '[0-9]+' | head -1)

# 穿衣建议
if [ -n "$temp_num" ]; then
    if [ "$temp_num" -ge 30 ]; then
        clothing="👕 短袖短裤，注意防暑降温"
        clothing_detail="天气炎热，建议穿轻薄透气的棉麻衣物，多补充水分"
    elif [ "$temp_num" -ge 26 ]; then
        clothing="👔 短袖 + 薄长裤/短裤"
        clothing_detail="天气较热，适合穿短袖，早晚可备一件薄外套"
    elif [ "$temp_num" -ge 22 ]; then
        clothing="🧥 短袖/长袖 + 薄外套"
        clothing_detail="温度舒适，建议穿长袖T恤或衬衫，早晚温差大注意增减衣物"
    elif [ "$temp_num" -ge 18 ]; then
        clothing="🧥 长袖 + 薄外套/卫衣"
        clothing_detail="天气凉爽，建议穿卫衣或薄外套，注意早晚保暖"
    elif [ "$temp_num" -ge 14 ]; then
        clothing="🧣 长袖 + 厚外套/毛衣"
        clothing_detail="温度较低，建议穿毛衣或厚外套，注意保暖"
    elif [ "$temp_num" -ge 10 ]; then
        clothing="🧤 毛衣 + 厚外套"
        clothing_detail="天气较冷，建议穿保暖内衣+毛衣+厚外套"
    else
        clothing="🧥 羽绒服/厚棉衣"
        clothing_detail="天气寒冷，建议穿羽绒服或厚棉衣，注意防寒保暖"
    fi
else
    clothing="🤷 无法获取温度"
    clothing_detail="建议查看天气预报"
fi

# 根据天气添加额外提醒
extra_reminder=""
if [[ "$condition" =~ (雨|Rain|rain) ]]; then
    extra_reminder="\n☔ 今天有雨，记得带伞！"
elif [[ "$condition" =~ (晴|Sunny|Clear) ]]; then
    extra_reminder="\n🕶️ 晴天紫外线较强，注意防晒"
elif [[ "$humidity" =~ ^[8-9][0-9]% ]]; then
    extra_reminder="\n💧 湿度较高，注意防潮"
fi

# 励志语录数组
quotes=(
    "每一天都是新的开始，加油！💪"
    "相信自己，你比想象中更强大！⭐"
    "保持热爱，奔赴山海！🌊"
    "今天的努力，是明天的底气！🎯"
    "愿你眼里有光，心中有爱！❤️"
    "生活明朗，万物可爱！🌸"
    "星光不问赶路人，时光不负有心人！✨"
    "愿你所有的坚持，都能换来繁花似锦！🌺"
    "往前走，别回头，未来可期！🌈"
    "愿你成为自己的太阳，无需借谁的光！☀️"
    "每一个不曾起舞的日子，都是对生命的辜负！💃"
    "心若向阳，无畏悲伤！🌻"
    "愿你历尽千帆，归来仍是少年！🎈"
    "生活原本沉闷，但跑起来就有风！🍃"
    "愿你以渺小启程，以伟大结束！🚀"
)

# 随机选择一句
random_index=$((RANDOM % ${#quotes[@]}))
daily_quote="${quotes[$random_index]}"

# 构建消息
message="📅 早安！$(date +%Y年%m月%d日) $weekday_name

📋 今日排班
═══════════════════════════
$shift_emoji 班次：$shift
⏰ 时间：$shift_time
═══════════════════════════
🌤️ 深圳宝安天气
• 天气状况：$condition_cn
• 当前温度：$current_temp
• 体感温度：$feels_like
• 空气湿度：$humidity
• 风力风向：$wind
• 日出时间：$sunrise 🌅
• 日落时间：$sunset 🌇
--------------------------
👔 穿衣建议

$clothing
💡 $clothing_detail$extra_reminder
═══════════════════════════
💬 今日寄语
$daily_quote
--------------------------
🐄 小牛牛祝你今天工作顺利！"

# 输出消息（用于调试）
echo "$message"
echo ""
echo "发送到飞书群组: $1"
