# from crewai import Crew, Process
# from crewai.project import agents_config, tasks_config


# def create_crew():
#     agents = agents_config.load()
#     tasks = tasks_config.load()
#     llm = LLM(
#     model="gemini/gemini-pro",  # ✅ OR "gemini/gemini-1.5-pro-latest" if you're sure
#     api_key=os.getenv("GEMINI_API_KEY")
# )


#     crew = Crew(
#         agents=agents,
#         tasks=tasks,
#         llm=llm,
#         process=Process.sequential  # Change to Process.parallel if needed
#     )

#     return crew

# import os
# from crewai import Crew, Process
# from crewai.project import agents_config, tasks_config
# from crewai.llm import LLM  # Ensure this is the correct import for the LLM class

# def create_crew():
#     agents = agents_config.load()
#     tasks = tasks_config.load()
    
#     llm = LLM(
#         model="gemini/gemini-pro",  # Or "gemini/gemini-1.5-pro-latest" if that's required
#         api_key=os.getenv("GEMINI_API_KEY")
#     )
    
#     crew = Crew(
#         agents=agents,
#         tasks=tasks,
#         llm=llm,
#         process=Process.sequential  # Change to Process.parallel if needed
#     )

#     return crew

# import os
# from crewai import Crew, Process
# from crewai.project import agents_config, tasks_config
# from langchain_google_genai import ChatGoogleGenerativeAI  # ✅ Correct Gemini LLM

# def create_crew():
#     agents = agents_config.load()
#     tasks = tasks_config.load()

#     # ✅ Use Gemini model from LangChain
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-pro",
#         google_api_key=os.getenv("GEMINI_API_KEY")
#     )

#     crew = Crew(
#         agents=agents,
#         tasks=tasks,
#         llm=llm,
#         process=Process.sequential
#     )
#     print(f"[CREW SETUP] ✅ Using model: gemini-pro with key: {'✅' if os.getenv('GEMINI_API_KEY') else '❌ MISSING'}")

#     return crew



import os
import yaml
from crewai import Crew, Process, Agent
from langchain_google_genai import ChatGoogleGenerativeAI

def load_yaml_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def create_crew():
    # Load YAML configs manually
    agents_config = load_yaml_config("src/intelligentta/config/agents.yaml")
    tasks_config = load_yaml_config("src/intelligentta/config/tasks.yaml")
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        convert_system_message_to_human=True
    )
    
    # Import tools
    from src.intelligentta.tools.resume_reader_tool import read_resume_tool, list_resumes_tool
    from src.intelligentta.tools.send_whatsapp_tool import send_whatsapp_message_tool
    from src.intelligentta.tools.google_calendar_tool import schedule_interview
    
    # Create agents manually
    talent_manager = Agent(
        role=agents_config["talent_acquisition_manager"]["role"],
        goal=agents_config["talent_acquisition_manager"]["goal"],
        backstory=agents_config["talent_acquisition_manager"]["backstory"],
        llm=llm,
        verbose=True
    )
    
    sourcing_agent = Agent(
        role=agents_config["sourcing_agent"]["role"],
        goal=agents_config["sourcing_agent"]["goal"],
        backstory=agents_config["sourcing_agent"]["backstory"],
        tools=[list_resumes_tool, read_resume_tool],
        llm=llm,
        verbose=True
    )
    
    screening_agent = Agent(
        role=agents_config["screening_agent"]["role"],
        goal=agents_config["screening_agent"]["goal"],
        backstory=agents_config["screening_agent"]["backstory"],
        tools=[read_resume_tool],
        llm=llm,
        verbose=True
    )
    
    engagement_agent = Agent(
        role=agents_config["engagement_agent"]["role"],
        goal=agents_config["engagement_agent"]["goal"],
        backstory=agents_config["engagement_agent"]["backstory"],
        tools=[send_whatsapp_message_tool],
        llm=llm,
        verbose=True
    )
    
    scheduling_agent = Agent(
        role=agents_config["scheduling_agent"]["role"],
        goal=agents_config["scheduling_agent"]["goal"],
        backstory=agents_config["scheduling_agent"]["backstory"],
        tools=[schedule_interview],
        llm=llm,
        verbose=True
    )
    
    # Create and return crew
    crew = Crew(
        agents=[talent_manager, sourcing_agent, screening_agent, engagement_agent, scheduling_agent],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
