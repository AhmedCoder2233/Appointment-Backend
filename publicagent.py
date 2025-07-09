from agents import Agent, Runner, RunConfig, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import chainlit as cl
import requests
from schema import AppointUser

load_dotenv()

set_tracing_disabled(True)

provider = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

config = RunConfig(
    model=model,
    model_provider=provider
)

@function_tool
def PostAppointment(data:AppointUser):
    result = requests.post("http://127.0.0.1:8000/userappointment", data=data)
    if result.status_code != 200:
        return "Failed To Post Data"
    return "Data Posted Succesfully"

PublicAgent = Agent(
    name="PublicAgent",
    instructions="""
You are a FastAppoint booking agent.

🎯 Your goal is to help users book clinic appointments by collecting ALL of the following fields:
- name (string)
- email (valid email)
- phone (number or string)
- day (e.g., '2025-07-12')
- time (e.g., '15:00')
- service (must be one of the 6 given below)
- isaccept (set to False)
- checkupdone (set to False)

📌 Services List (must choose one):
1. General Consultation
2. Dental Care
3. Lab Test Booking
4. Eye Checkup
5. Physiotherapy
6. Cardiology

📝 Once all info is collected, call the `PostAppointment` tool and submit the data.

⚠️ Important Rules:
- Never handle delete, cancel, or update requests. Reply: **"Please visit the website to manage your appointment."**
- If user gives incomplete or wrong info, politely ask for missing fields again in **one message**.
- After success, say: **"✅ Your appointment has been booked! Please check your email for doctor details and confirmation."**

🎯 Always ensure all 7 fields are collected before submission. Validate `service` matches one of the above.
""",
tools=[PostAppointment]
)

@cl.on_chat_start
async def ChatStart():
    await cl.Message(content="Welcome To FastAppoint Admin Panel ChatBot").send()
    cl.user_session.set("history", [])

@cl.on_message
async def MessagingStart(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})
    result = await Runner.run(PublicAgent, history, run_config=config)
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    await cl.Message(content=result.final_output).send()
