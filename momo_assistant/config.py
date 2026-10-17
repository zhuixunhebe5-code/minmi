"""
陌陌聊天助手 - 配置模块
所有可调参数集中在此处，方便根据实际设备/应用版本微调。
"""

# ============ 设备配置 ============
# Android 设备序列号（adb devices 查看）。为空则自动连接第一台设备。
DEVICE_SERIAL = ""

# 陌陌包名
MOMO_PACKAGE = "com.immomo.momo"

# ============ AI 接口配置（OpenAI 兼容协议）===========
# 支持 OpenAI / DeepSeek / 月之暗面 / 通义千问 / 本地 Ollama 等
AI_API_KEY = "sk-your-api-key-here"
AI_BASE_URL = "https://api.openai.com/v1"   # 例如 DeepSeek: https://api.deepseek.com/v1
AI_MODEL = "gpt-4o-mini"                     # 例如 deepseek-chat

# 回复建议数量
SUGGESTION_COUNT = 3

# 回复风格设定，可自行修改
AI_SYSTEM_PROMPT = (
    "你是一个聊天回复助手。请根据对方发来的消息和聊天上下文，"
    "生成自然、口语化的中文回复建议，要像真人聊天，不要太官方。"
    "每条建议控制在 50 字以内，用换行分隔。"
)

# ============ UI 元素选择器（可根据实际界面微调）============
# 陌陌版本不同，控件 ID 可能变化。这里提供候选，代码会依次尝试。
# 聊天消息列表容器（RecyclerView）
MESSAGE_LIST_SELECTORS = [
    {"resourceId": "com.immomo.momo:id/recycler_view"},
    {"resourceId": "com.immomo.momo:id/list_view"},
    {"className": "androidx.recyclerview.widget.RecyclerView"},
    {"className": "android.widget.ListView"},
]

# 消息文本控件（气泡内的文字）
MESSAGE_TEXT_SELECTORS = [
    {"resourceId": "com.immomo.momo:id/tv_message"},
    {"resourceId": "com.immomo.momo:id/content"},
    {"className": "android.widget.TextView"},
]

# 输入框
INPUT_BOX_SELECTORS = [
    {"resourceId": "com.immomo.momo:id/et_input"},
    {"resourceId": "com.immomo.momo:id/edit_text"},
    {"className": "android.widget.EditText"},
]

# 发送按钮（仅用于定位，不会自动点击）
SEND_BUTTON_SELECTORS = [
    {"resourceId": "com.immomo.momo:id/btn_send"},
    {"text": "发送"},
]

# ============ 运行参数 ============
# 新消息轮询间隔（秒）
POLL_INTERVAL = 3.0

# 读取最近 N 条消息作为上下文
CONTEXT_MESSAGE_COUNT = 10

# 屏幕宽高（用于判断消息是左侧=对方/右侧=自己）
# 留空则自动从设备获取
SCREEN_WIDTH = None
SCREEN_HEIGHT = None
