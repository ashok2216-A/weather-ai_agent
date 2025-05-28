from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain_mistralai.chat_models import ChatMistralAI
from tools import get_current_time, get_weather


def create_agent(api_key):

    if not api_key:
        return None
        
    try:
        llm = ChatMistralAI(model="mistral-small-latest", temperature=0.1, mistral_api_key=api_key)
        
        tools = [
            Tool(
                name="get_time", func=get_current_time,
                description="Get current time. Use timezone format like 'Asia/Kolkata' or 'America/New_York'. Leave empty for UTC."),
            Tool(
                name="get_weather", func=get_weather,
                description="Get current weather for any city. Just provide city name like 'London' or 'New York' or 'Mumbai'.")]
        
        agent = initialize_agent(
            tools=tools, llm=llm,
            agent="zero-shot-react-description", verbose=False,  # Reduce verbosity for cleaner output
            handle_parsing_errors=True
        )
        
        # Set a more focused system message
        agent.agent.llm_chain.prompt.template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        return agent
        
    except Exception as e:
        raise Exception(f"Error initializing agent: {str(e)}")
