<div align="center">
  <br>
  <h1>🛠️ AI 工具助手</h1>
  <p><strong>基于 Function Calling 的 AI Agent — 让 AI 调用工具帮你做事</strong></p>
  <br>
</div>

## ✨ 功能

| 工具 | 说明 |
|------|------|
| 🌤️ 查天气 | 查询任意城市的实时天气（温度、湿度、风速） |
| 🧮 数学计算 | 表达式求值，支持 + - × ÷ ** sqrt 等 |
| 🕐 时区时间 | 获取任意时区的当前日期和时间 |
| 🌐 IP 查询 | 查询 IP 地址的地理位置和 ISP 信息 |

## 🛠️ 技术栈

```
AI 模型     ─  DeepSeek API (Function Calling)
前端/后端   ─  Streamlit
核心模式    ─  Agent + Tool Use
```

## 🚀 本地运行

```bash
# 1. 克隆
git clone https://github.com/LIUCHUHUAN7051/ai-agent.git
cd ai-agent

# 2. 装依赖
pip install -r requirements.txt

# 3. 配置 API Key
# 在 .env 文件中填入：
# DEEPSEEK_API_KEY=你的key

# 4. 启动
streamlit run agent_app.py
```

## 📖 使用示例

试试这样问：

```
🌤️ "北京天气怎么样？"
🧮 "1024 × 768 等于多少"
🕐 "纽约现在几点"
🌐 "查一下 8.8.8.8 的位置"
```

## 💡 核心原理

本项目演示了 **AI Agent 的 Function Calling 模式**：

1. 用户提出需求
2. AI 模型自动判断需要调用哪个工具
3. 系统执行工具并返回结果
4. AI 基于工具结果生成自然语言回答

## 📂 项目结构

```
ai-agent/
├── agent_app.py         # 主程序
├── requirements.txt     # 依赖
├── .env                # API Key（不上传）
└── README.md           # 项目说明
```

## 👤 关于

- 作者：刘理鑫
- 求职方向：AI 应用开发工程师
- 邮箱：CHUIZI705179074@outlook.com
- GitHub：https://github.com/LIUCHUHUAN7051/ai-agent
