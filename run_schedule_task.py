# # run_schedule_task.py

# from crewai import Agent, Task, Crew, Process
# from crewai.project import agents_config, tasks_config

# def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
#     # Load only the specific agent and task
#     agent = agents_config.get("scheduling_agent")
#     task_template = tasks_config.get("schedule_interviews_task")

#     # Format the task with actual data
#     task = Task(
#         description=task_template.description.format(
#             candidate_name=candidate_name,
#             job_role=job_role,
#             interview_date=interview_date,
#             interview_time=interview_time
#         ),
#         expected_output=task_template.expected_output,
#         agent=agent
#     )

#     # Create a mini-crew just for this task
#     crew = Crew(
#         agents=[agent],
#         tasks=[task],
#         process=Process.sequential
#     )

#     # Run the task
#     result = crew.kickoff()
#     return result


# from crewai import Agent, Task, Crew, Process
# from crewai.project import agents_config, tasks_config

# def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
#     agent = agents_config.get("scheduling_agent")
#     task_template = tasks_config.get("schedule_interviews_task")

#     task = Task(
#         description=task_template.description.format(
#             candidate_name=candidate_name,
#             job_role=job_role,
#             interview_date=interview_date,
#             interview_time=interview_time
#         ),
#         expected_output=task_template.expected_output,
#         agent=agent
#     )

#     crew = Crew(
#         agents=[agent],
#         tasks=[task],
#         process=Process.sequential
#     )

#     result = crew.kickoff()
#     return result

# run_schedule_task.py

# from crewai import Task, Crew, Process
# from crewai.project.base import CrewBase

# class ScheduleInterviewCrew(CrewBase):
#     def run(self, candidate_name, job_role, interview_date, interview_time):
#         # Load agent and task from YAML
#         scheduling_agent = self.agent(name="scheduling_agent")
#         schedule_task_template = self.task(name="schedule_interviews_task")

#         # Inject dynamic values into the task
#         schedule_task = Task(
#             description=schedule_task_template.description.format(
#                 candidate_name=candidate_name,
#                 job_role=job_role,
#                 interview_date=interview_date,
#                 interview_time=interview_time
#             ),
#             expected_output=schedule_task_template.expected_output,
#             agent=scheduling_agent
#         )

#         # Create and run crew
#         crew = Crew(
#             agents=[scheduling_agent],
#             tasks=[schedule_task],
#             process=Process.sequential
#         )

#         result = crew.kickoff()
#         return result

# # Exposed function to import elsewhere
# def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
#     return ScheduleInterviewCrew().run(
#         candidate_name=candidate_name,
#         job_role=job_role,
#         interview_date=interview_date,
#         interview_time=interview_time
#     )

# run_schedule_task.py

# import yaml
# import os

# from crewai import Agent, Task, Crew, Process, LLM

# def load_yaml_config(path):
#     with open(path, "r") as f:
#         return yaml.safe_load(f)

# def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
#     # ✅ Load YAML configs from the correct path
#     agents = load_yaml_config("src/intelligentta/config/agents.yaml")
#     tasks = load_yaml_config("src/intelligentta/config/tasks.yaml")

#     # ✅ Get scheduling agent info
#     sa = agents["scheduling_agent"]

#     # ✅ Build the agent
#     scheduling_agent = Agent(
#         role=sa["role"],
#         goal=sa["goal"],
#         backstory=sa["backstory"],
#         tools=[],  # If you want to load the calendar tool, let me know!
#         verbose=True
#     )

#     # ✅ Prepare the task with filled placeholders
#     st = tasks["schedule_interviews_task"]
#     filled_description = st["description"].format(
#         candidate_name=candidate_name,
#         job_role=job_role,
#         interview_date=interview_date,
#         interview_time=interview_time
#     )

#     schedule_task = Task(
#         description=filled_description,
#         expected_output=st["expected_output"],
#         agent=scheduling_agent
#     )
#     llm = LLM(
#     model="gemini/gemini-pro",  # ✅ OR "gemini/gemini-1.5-pro-latest" if you're sure
#     api_key=os.getenv("GEMINI_API_KEY"),
#     provider="gemini"
# )

#     # ✅ Create a mini crew and kickoff
#     crew = Crew(
#         agents=[scheduling_agent],
#         tasks=[schedule_task],
#         llm=llm,
#         process=Process.sequential
#     )

#     return crew.kickoff()
# import yaml
# import os
# from crewai import Agent, Task, Crew, Process, LLM

# def load_yaml_config(path):
#     with open(path, "r") as f:
#         return yaml.safe_load(f)

# def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
#     # ✅ Load YAML configs from the correct path
#     agents = load_yaml_config("src/intelligentta/config/agents.yaml")
#     tasks = load_yaml_config("src/intelligentta/config/tasks.yaml")

#     # ✅ Create LLM instance - this is the correct way for Gemini

#     from crewai import LLM
# import os

# llm = LLM(
#     model=os.getenv("LITELLM_MODEL", "tiiuae/falcon-7b-instruct"),
#     api_key=os.getenv("HUGGINGFACE_API_KEY"),
#     provider="huggingface"
# )

#     llm = LLM(
#         model="gemini/gemini-pro",  # Must include gemini/ prefix
#         api_key=os.getenv("GOOGLE_API_KEY"),
#         verbose=True
#     )

#     # ✅ Get scheduling agent info
#     sa = agents["scheduling_agent"]

#     # ✅ Now build the agent with llm
#     scheduling_agent = Agent(
#         role=sa["role"],
#         goal=sa["goal"],
#         backstory=sa["backstory"],
#         tools=[],
#         verbose=True,
#         allow_delegation=False,
#         llm=llm
#     )

#     # ✅ Prepare the task with filled placeholders
#     st = tasks["schedule_interviews_task"]
#     filled_description = st["description"].format(
#         candidate_name=candidate_name,
#         job_role=job_role,
#         interview_date=interview_date,
#         interview_time=interview_time
#     )

#     schedule_task = Task(
#         description=filled_description,
#         expected_output=st["expected_output"],
#         agent=scheduling_agent
#     )

#     # ✅ Create a mini crew and kickoff
#     crew = Crew(
#         agents=[scheduling_agent],
#         tasks=[schedule_task],
#         process=Process.sequential
#     )

#     return crew.kickoff()
# from src.intelligentta.tools.google_calendar_tool import schedule_interview

import yaml
import os
import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Import the tool properly
import sys
sys.path.append(".")  # Add current directory to path
from src.intelligentta.tools.google_calendar_tool import schedule_interview

# Load environment variables
load_dotenv()

def load_yaml_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_schedule_task(candidate_name, job_role, interview_date, interview_time):
    # Load YAML configs
    agents = load_yaml_config("src/intelligentta/config/agents.yaml")
    tasks = load_yaml_config("src/intelligentta/config/tasks.yaml")

    # Create LLM with correct Hugging Face format
    llm = LLM(
        model="huggingface/tiiuae/falcon-7b-instruct",
        api_key=os.getenv("HUGGINGFACE_API_KEY"),
        provider="huggingface",
        temperature=0.7,
        max_tokens=512
    )
    
    # Simple date time conversion - no timezone complexity
    try:
        # Create start and end times (1 hour apart)
        datetime_str = f"{interview_date} {interview_time}"
        start_datetime = datetime.datetime.strptime(datetime_str, "%B %d, %Y %I:%M %p")
        end_datetime = start_datetime + datetime.timedelta(hours=1)
        
        # Format for Google Calendar
        start_time = start_datetime.isoformat()
        end_time = end_datetime.isoformat()
        
        # Build the agent with the calendar tool
        sa = agents["scheduling_agent"]
        scheduling_agent = Agent(
            role=sa["role"],
            goal=sa["goal"],
            backstory=sa["backstory"],
            tools=[schedule_interview],
            verbose=True,
            llm=llm
        )

        # Prepare the task
        st = tasks["schedule_interviews_task"]
        filled_description = st["description"].format(
            candidate_name=candidate_name,
            job_role=job_role,
            interview_date=interview_date,
            interview_time=interview_time
        )

        schedule_task = Task(
            description=filled_description,
            expected_output=st["expected_output"],
            agent=scheduling_agent
        )

        # Create and run the crew
        crew = Crew(
            agents=[scheduling_agent],
            tasks=[schedule_task],
            process=Process.sequential
        )
        
        return crew.kickoff()
    except Exception as e:
        return f"❌ Failed to schedule interview: {str(e)}"
