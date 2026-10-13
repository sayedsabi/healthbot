HealthBot-Langgraph Based Ai Health Education assistant

The program Performs the following workflow:
1. Accepts a health topic from user.
2. Searches sources using tavily.
3. Generates Summary using OpenAI llm.
4. Displays summary.
5. Asks user if ready for quiz.
6. Displays quiz and asks user for answer.
7. Grades the quiz and provides feedback.
8. Asks if user wants to continue with another topic or exit.

Technologies used:
1. Pyhton 3.11
2. LangGraph
3. Langchain
4. OPENAI GPT
5. Tavily Search API
6. python-dotenv

Project structure files:
1. config.env
2. main.py
3. requirements.txt
4. README.md
5. main.ipynb

Installation

1. install required packages:
   pip install -r requirements.txt

2. create environment file containing OPENAI and Tavily API keys

3. run project 
   python main.py

AUTHOR

Sayed Sabeeh Ahamed Airani