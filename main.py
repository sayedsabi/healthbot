import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from typing import TypedDict
from langgraph.graph import StateGraph,START,END


#load environment variables

load_dotenv("config.env")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

#initialize open ai model and tavily

llm =ChatOpenAI(model="gpt-4.1-mini",api_key=OPENAI_API_KEY)
tavily_search=TavilySearch(max_results=3)

#GRAPH STATE INITIALIZATION

class HealthState(TypedDict):
    topic:str
    search_results:str
    summary:str
    ready_for_quiz:bool
    quiz_question:str
    correct_answer:str
    user_answer:str
    feedback:str
    continue_chat:bool

#GET THE TOPIC FROM USER

def get_topic(state):
    print("\nWelcome to HealthBot!")
    topic=input("Enter a health topic you want to learn about: ")   
    state["topic"]=topic
    return state
 
#Search HEALTH INFORMATION

def search_topic(state):
    print("\nSearching trusted medical sources using tavily.......")
    results=tavily_search.invoke(state["topic"])
    state["search_results"]=results
    return state

#GENERATE SUMMARY FOR USER

def generate_summary(state):
    prompt = f""" 
    You are a healthcare educator.
    Using only the information below, generate a simple,patient-friendly summary
    in 3-4 paragraphs.

    Search Results:
    {state["search_results"]}
    """
    response=llm.invoke(prompt)
    state["summary"]=response.content
    if "error" in str(state["search_results"]):
        state["summary"]=("Unable to retireve medical information possibly due to tavily requests ran out (try with another key).")
    return state

#Display Summary

def display_summary(state):
    print("\n========HEALTH SUMMARY========\n")
    print(state["summary"])
    return state

#check ready for quiz

def ready_for_quiz(state):
    choice=input("\nAre you ready to take the quiz? (y/n): ").strip().lower()
    if choice=="y":
        state["ready_for_quiz"]=True
    else:
        state["ready_for_quiz"]=False
    return state

#quiz node
def quiz_node(state):
    if not state["ready_for_quiz"]:
        return state
    prompt=f"""
    Based only on the summary below,
    Generate One simple health-related quiz question.
    Also provide the correct answer seperately.

    Summary:
    {state["summary"]}

    Return ONLY in this format:
    Question:....
    Answer:.....
    """
    response=llm.invoke(prompt).content
    question,answer=response.split("Answer:")
    state["quiz_question"]=question.replace("Question:", "").strip()
    state["correct_answer"]=answer.strip()
    return state

#GRADE NODE

def grade_node(state):
    print("\nQuiz Question:\n")
    print(state["quiz_question"])
    state["user_answer"]=input("\nYour Answer: ")
    prompt=f"""
    Question:
    {state["quiz_question"]}

    Correct Answer:
    {state["correct_answer"]}

    User Answer:
    {state["user_answer"]}

    Determine whether the answer is correct. 
    Give:
    1. Correct/Incorrect
    2. Score out of 10
    3. One line Explaination. 
    """
    feedback=llm.invoke(prompt).content
    state["feedback"]=feedback
    print("\n=======FEEDBACK======\n")
    print(feedback)
    return state

#Continue or EXIT 

def continue_or_exit(state):
    choice=input("\nWould you like to learn another health topic?(y/n): ").strip().lower()
    if choice=="y":
        #reset state
        state["topic"]=""
        state["search_results"]=""
        state["summary"]=""
        state["ready_for_quiz"]=False
        state["quiz_question"]=""
        state["correct_answer"]=""
        state["user_answer"]=""
        state["feedback"]=""
        state["continue_chat"]=True
    else:
        #reset state 
        state["topic"]=""
        state["search_results"]=""
        state["summary"]=""
        state["ready_for_quiz"]=False
        state["quiz_question"]=""
        state["correct_answer"]=""
        state["user_answer"]=""
        state["feedback"]=""
        state["continue_chat"]=False
        print("Thank you for using HealthBot!")
    return state  

#router function

def route_next(state):
    if state["continue_chat"]:
        return "get_topic"
    return END

#router quiz function
def route_quiz(state):
    if state["ready_for_quiz"]:
        return "quiz_node"
    else:
        return "ready_for_quiz"

#create graph
builder=StateGraph(HealthState)

#add all nodes

builder.add_node("get_topic",get_topic)
builder.add_node("search_topic",search_topic)
builder.add_node("generate_summary",generate_summary)
builder.add_node("display_summary",display_summary)
builder.add_node("ready_for_quiz",ready_for_quiz)
builder.add_node("quiz_node",quiz_node)
builder.add_node("grade_node",grade_node)
builder.add_node("continue_or_exit",continue_or_exit)

#add edges

builder.add_edge(START,"get_topic")
builder.add_edge("get_topic","search_topic")
builder.add_edge("search_topic","generate_summary")
builder.add_edge("generate_summary","display_summary")
builder.add_edge("display_summary","ready_for_quiz")
builder.add_conditional_edges("ready_for_quiz",route_quiz,{"quiz_node":"quiz_node","ready_for_quiz":"ready_for_quiz"})
builder.add_edge("quiz_node","grade_node")
builder.add_edge("grade_node","continue_or_exit")
builder.add_conditional_edges("continue_or_exit",route_next,{"get_topic":"get_topic",END:END})
graph=builder.compile()

if __name__=="__main__":
    initial_state=HealthState(
        topic="",
        search_results="",
        summary="",
        ready_for_quiz=False,
        quiz_question="",
        correct_answer="",
        user_answer="",
        feedback="",
        continue_chat=True,
    )
    graph.invoke(initial_state)




