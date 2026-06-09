"""AI 工具助手 — 让 AI 调用工具帮你做事"""

import json
import os
import smtplib
import urllib.request
import urllib.parse
import datetime
from email.mime.text import MIMEText

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ====== 工具实现 ======

def get_weather(city: str) -> str:
    """查询实时天气"""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C+%t+%h+%w&lang=zh"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode().strip()
            return f"🌤️ {city} 天气：{raw}"
    except Exception as e:
        return f"查询天气失败：{e}"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    allowed = {"abs", "int", "float", "str", "len", "range", "list",
               "sum", "min", "max", "round", "pow", "sqrt", "pi", "e"}
    try:
        # 替换常见符号
        expr = expression.replace("×", "*").replace("÷", "/").replace("（", "(").replace("）", ")")
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed and not name.startswith("_"):
                return f"不支持的运算：{name}"
        import math
        builtins = {n: getattr(math, n, __builtins__.get(n)) for n in allowed}
        result = eval(expr, {"__builtins__": {}}, builtins)
        return f"🧮 计算结果：{result}"
    except Exception as e:
        return f"计算失败：{e}"


def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取指定时区的当前时间"""
    import zoneinfo
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.datetime.now(tz)
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        wd = weekdays[now.weekday()]
        return f"🕐 {timezone} 当前时间：{now.strftime('%Y年%m月%d日')} {wd} {now.strftime('%H:%M:%S')}"
    except Exception as e:
        return f"获取时间失败：{e}"


def get_ip_info(ip: str = "") -> str:
    """查询 IP 地址信息"""
    try:
        url = f"http://ip-api.com/json/{ip}?lang=zh-CN" if ip else "http://ip-api.com/json/?lang=zh-CN"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("status") == "success":
                return (f"🌐 IP 信息：{data.get('query', ip)}\n"
                        f"📍 {data.get('country', '')} {data.get('regionName', '')} {data.get('city', '')}\n"
                        f"🏢 {data.get('isp', '未知')}")
            return f"查询失败：{data.get('message', '未知错误')}"
    except Exception as e:
        return f"查询 IP 失败：{e}"


# ====== 工具定义 ======
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询任意城市的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如 福州、深圳、北京"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，支持 + - × ÷ ** 和数学函数",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 25*4+18、2**10、(100-20)/4、sqrt(144)"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取指定时区的当前日期和时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "时区，如 Asia/Shanghai、America/New_York、Europe/London，默认 Asia/Shanghai"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ip_info",
            "description": "查询 IP 地址的地理位置和 ISP 信息，不传参数则查询本机 IP",
            "parameters": {
                "type": "object",
                "properties": {
                    "ip": {"type": "string", "description": "IP 地址，如 8.8.8.8，留空查本机"}
                }
            }
        }
    }
]

tool_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
    "get_ip_info": get_ip_info,
}

tool_descriptions = {
    "get_weather": "🌤️ 查天气 —— 查询任意城市实时天气",
    "calculate": "🧮 数学计算 —— 表达式求值，支持 + - × ÷ **",
    "get_current_time": "🕐 当前时间 —— 获取指定时区的时间日期",
    "get_ip_info": "🌐 IP 查询 —— 查 IP 地址的地理位置",
}

# ====== 初始化 ======
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY", "")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
)

# ====== 页面配置 ======
st.set_page_config(page_title="AI 工具助手", page_icon="🛠️", layout="centered")

st.markdown("""
<style>
    @keyframes fadeIn { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }
    @keyframes slideUp { from { opacity:0; transform:translateY(15px); } to { opacity:1; transform:translateY(0); } }
    @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
    @keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    @keyframes shimmer { 0%{background-position:-200%} 100%{background-position:200%} }
    @keyframes typingDot { 0%,80%,100%{transform:scale(0.6);opacity:0.3} 40%{transform:scale(1);opacity:1} }

    .stApp { background: #f5f7fb; }
    .block-container { padding-top: 1.5rem !important; animation: fadeIn 0.5s ease-out; }
    .header {
        background: linear-gradient(135deg, #059669, #2563eb, #7c3aed);
        background-size: 200% 200%;
        animation: gradientShift 6s ease infinite;
        color: white; padding: 1.5rem 2rem; border-radius: 16px;
        margin-bottom: 1.2rem; text-align: center;
    }
    .header h1 { margin:0; font-size:1.8rem; font-weight:700; }
    .header p { margin:0.3rem 0 0; opacity:0.85; font-size:0.9rem; }
    .tool-tag {
        display:inline-block; background:#e8edf5; color:#1e3a5f;
        font-size:0.75rem; padding:3px 12px; border-radius:12px;
        margin:2px 3px; border:1px solid #d1d9e8; transition: all 0.2s;
    }
    .tool-tag:hover { background:#d1d9e8; transform: translateY(-1px); }

    .call-card {
        background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;
        padding:0.5rem 0.8rem; margin:0.3rem 0; font-size:0.85rem;
        animation: slideUp 0.35s ease-out;
    }
    .tool-result {
        background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
        padding: 0.5rem 0.8rem; margin: 0.3rem 0;
        font-family: 'Courier New', monospace; font-size: 0.85rem;
        white-space: pre-wrap; animation: slideUp 0.3s ease-out;
    }

    div[data-testid="stChatMessage"] { animation: slideUp 0.3s ease-out; border-radius:12px; }
    div[data-testid="stChatInput"] input {
        border-radius:24px !important; border:1px solid #e5e7eb !important;
        padding:0.6rem 1.2rem !important; transition:all 0.25s !important;
    }
    div[data-testid="stChatInput"] input:focus {
        border-color:#2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    .empty-state { text-align:center; padding:4rem 1rem; color:#9ca3af; animation:fadeIn 0.8s; }
    .empty-state .icon { font-size:4rem; animation:float 3s ease-in-out infinite; }

    .typing-dots { display:flex; align-items:center; gap:4px; padding:0.5rem 0; }
    .typing-dots span { width:8px; height:8px; border-radius:50%; background:#2563eb; animation: typingDot 1.4s ease-in-out infinite; }
    .typing-dots span:nth-child(2) { animation-delay:0.2s; }
    .typing-dots span:nth-child(3) { animation-delay:0.4s; }

    hr { margin:0.8rem 0; border-color:#e5e7eb; }
    .stAlert { border-radius:10px; }

    section[data-testid="stSidebar"] > div:first-child { background:#fff; border-right:1px solid #e5e7eb; }
    section[data-testid="stSidebar"] .stButton button {
        background:#f3f4f6; color:#374151; border:1px solid #e5e7eb;
        border-radius:10px; transition:all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background:#e5e7eb; transform:translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    section[data-testid="stSidebar"] .stDownloadButton button {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white; border: none; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🛠️ AI 工具助手</h1>
    <p>查天气 · 算数学 · 看时间 · 查 IP —— 让 AI 调用工具帮你做事</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom:0.8rem;">
    <span class="tool-tag">🌤️ 查天气</span>
    <span class="tool-tag">🧮 计算器</span>
    <span class="tool-tag">🕐 时区时间</span>
    <span class="tool-tag">🌐 IP 查询</span>
</div>
""", unsafe_allow_html=True)

# ====== 状态 ======
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# ====== Agent 执行 ======
def run_agent(user_msg: str):
    st.session_state.agent_messages.append({"role": "user", "content": user_msg})
    st.session_state.agent_history.append({"role": "user", "content": user_msg})

    messages = [
        {"role": "system", "content": "你是一个智能工具助手。你可以使用工具来完成用户请求。每次调用一个工具，等结果返回后根据结果回答用户。"},
        *st.session_state.agent_messages[-10:],
    ]

    placeholder = st.empty()

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True,
        )

        collected = []
        text_content = ""

        for chunk in resp:
            delta = chunk.choices[0].delta
            if delta.content:
                text_content += delta.content
                placeholder.markdown(text_content + "▌")
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    while len(collected) <= tc.index:
                        collected.append({"id": "", "function": {"name": "", "arguments": ""}})
                    if tc.id:
                        collected[tc.index]["id"] += tc.id
                    if tc.function.name:
                        collected[tc.index]["function"]["name"] += tc.function.name
                    if tc.function.arguments:
                        collected[tc.index]["function"]["arguments"] += tc.function.arguments

        # 有工具调用
        if collected:
            placeholder.markdown(text_content + "\n\n<div class='typing-dots'><span></span><span></span><span></span> 正在调用工具...</div>" if text_content else "<div class='typing-dots'><span></span><span></span><span></span> 正在调用工具...</div>", unsafe_allow_html=True)

            for tc in collected:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                fn = tool_map.get(name)
                result = fn(**args) if fn else f"未知工具：{name}"

                # 工具调用日志
                with st.chat_message("tool"):
                    cols = st.columns([1, 3])
                    with cols[0]:
                        icon = name.replace("get_weather", "🌤️").replace("calculate", "🧮").replace("get_current_time", "🕐").replace("get_ip_info", "🌐")
                        st.markdown(f"**{icon}**")
                    with cols[1]:
                        st.markdown(f"**{name}**  ·  `{json.dumps(args, ensure_ascii=False)}`")
                    st.markdown(f'<div class="tool-result">{result}</div>', unsafe_allow_html=True)

                # 记录消息
                st.session_state.agent_messages.append({
                    "role": "assistant", "content": text_content,
                    "tool_calls": [{"id": tc["id"], "type": "function", "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}]
                })
                st.session_state.agent_messages.append({"role": "tool", "content": result, "tool_call_id": tc["id"]})

            # 生成最终回答
            final = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个智能工具助手。根据工具返回的结果，用自然语言回答用户。"},
                    *st.session_state.agent_messages
                ],
                stream=True,
            )
            full = ""
            for chunk in final:
                d = chunk.choices[0].delta.content or ""
                full += d
                placeholder.markdown(full + "▌")
            placeholder.markdown(full)
            st.session_state.agent_messages.append({"role": "assistant", "content": full})
            st.session_state.agent_history.append({"role": "assistant", "content": full})
        else:
            placeholder.markdown(text_content)
            st.session_state.agent_messages.append({"role": "assistant", "content": text_content})
            st.session_state.agent_history.append({"role": "assistant", "content": text_content})

    except Exception as e:
        st.error(f"出错了：{e}")

# ====== 主界面 ======
for msg in st.session_state.agent_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("试试说「北京天气」「现在几点」「我的 IP 是什么」..."):
    st.chat_message("user").markdown(prompt)
    run_agent(prompt)

# ====== 侧边栏 ======
with st.sidebar:
    st.markdown("### 🤖 可用工具")
    for desc in tool_descriptions.values():
        st.markdown(f'<div class="call-card">{desc}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 💡 试试这样说")
    st.caption("北京天气怎么样？")
    st.caption("1024×768 等于多少")
    st.caption("东京现在几点了")
    st.caption("查一下 8.8.8.8 的位置")
    st.caption("sqrt(144) + 3² 等于多少")
    st.caption("纽约现在的时间")

    if st.session_state.agent_history:
        st.divider()

        # 导出对话
        chat_text = ""
        for m in st.session_state.agent_history:
            role = "🧑 你" if m["role"] == "user" else "🤖 AI"
            chat_text += f"### {role}\n{m['content']}\n\n"
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button("💾 导出对话", data=chat_text, file_name=f"agent对话_{now}.md", mime="text/markdown", use_container_width=True)

        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.agent_history = []
            st.session_state.agent_messages = []
            st.rerun()
