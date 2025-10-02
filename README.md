🌙 Luna AI Agent

Luna AI is a calm, problem-solving AI agent built by Surjan Thakur.
.
Its mission is simple: understand user problems → plan smartly → solve using tools or knowledge.

✨ Features

🧠 AI Agent Brain — Powered by LangGraph + LangChain for reasoning & tool orchestration.

🖥️ Frontend — Built with Streamlit, simple and elegant chat-like UI.

⚙️ Backend — Pure Python, lightweight and modular.

🗄️ Database — MongoDB for checkpointing (saving chat state & workflows).

🛠️ Integrated Tools:

🌐 web_search → Fetches real-time info when Luna doesn’t know something.

🌦️ get_weather → Provides live weather updates for any city.

📍 access_location → Gets user’s location and answers location-based queries.

👨‍💻 coding → Debugs errors, writes snippets, and explains code.

🚀 Tech Stack

Frontend: Streamlit

Backend: Python

AI Orchestration: LangGraph + LangChain

Database: MongoDB (checkpointing)

APIs: Custom tool integrations (Weather, Location, Web Search)

🧭 How Luna Works

Understand the user’s query.

Plan the best path:

Use tools if external data is required.

Or answer directly if internal knowledge is enough.

Execute with clarity: Step-by-step + highlighted key points.

Summarize the solution (with light emojis for a human-like feel).

⚡ Installation & Setup

# Clone the repo

git clone https://github.com/surjanthakur/Luna-Ai.git
cd luna-ai

# Create virtual environment

python -m venv .venv
source .venv/bin/activate # Mac/Linux
.venv\Scripts\activate # Windows

# Install dependencies

pip install -r requirements.txt

# Run the app

streamlit run main.py

📌 Roadmap

More tool integrations (Task management, MS To Do, Twitter posting 🐦)

UI upgrades (better theming, animations)

Deploy on cloud (Docker + Render/Heroku)

📬 Contact

Created with ❤️ by Surjan Thakur

📧 tsurjan506@gmail.com

🐙 GitHub: Add your GitHub link here

🌐 Portfolio: Coming soon...

🔥 Luna AI isn’t just a bot — it’s your daily problem-solving companion.
