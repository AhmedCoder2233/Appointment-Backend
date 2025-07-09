from agents import Agent, Runner, RunConfig, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import chainlit as cl
import requests

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
def SendEmail(to: str, body: str, subject: str):
    message = EmailMessage()
    message["to"] = to
    message.set_content(body)
    message["from"] = "ahmedmemon3344@gmail.com"
    message["subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("ahmedmemon3344@gmail.com", "enme cmsb pjnu edzt")
        server.send_message(message)

@function_tool
def checked_as_accepted(email: str):
    data = requests.post(f"http://127.0.0.1:8000/isaccept/{email}")
    return data.json()

@function_tool
def checkupDone(email: str):
    data = requests.post(f"http://127.0.0.1:8000/checkedupdone/{email}")
    return data.json()

@function_tool
def get_user_data(email: str):
    data = requests.get(f"http://127.0.0.1:8000/userappointment/{email}")
    if data.status_code != 200:
        return "Failed to fetch data"
    return data.json()

@function_tool
def AllData():
    data = requests.get("http://127.0.0.1:8000/alldata")
    if data.status_code != 200:
        return "Failed to fetch data"
    return data.json()

ManagerAgent = Agent(
    name="ManagerAgent",
    instructions="""
You are a highly efficient assistant for the FastAppoint Admin Panel. You MUST use only the given tools when needed. Never guess. Never respond without tool usage if required. Be efficient.

---

📌 EXAMPLE (Accept Appointment):
User: Accept the appointment for ahmed@gmail.com

1. Call: checked_as_accepted(email="ahmed@gmail.com")
2. If response is: {"message": "User with this email not found!"}
   → Reply: "User with this email not found!"
3. If response is: {"message": "User accepted Successfully"}
   a. Call: get_user_data(email="ahmed@gmail.com")
   b. Extract: day, time, service
   c. Call:
      SendEmail(
        to="ahmed@gmail.com",
        subject="Appointment Accepted",
        body="Your appointment has been accepted.\nDay: {day}\nTime: {time}\nService: {service}"
      )

---

📌 EXAMPLE (Reject Appointment):
User: Reject the appointment for ahmed@gmail.com

1. Ask: "Why should I reject this appointment? Please provide a reason."
2. After reason:
   a. Call: get_user_data(email="ahmed@gmail.com")
   b. If response = "Failed to fetch data", reply that.
   c. Else call:
      SendEmail(
        to="ahmed@gmail.com",
        subject="Appointment Rejected",
        body="Your appointment has been rejected.\nReason: {reason}\nService: {service}\nDay: {day}\nTime: {time}"
      )

---

📌 EXAMPLE (Today’s Appointments):
User: Show me 2025-04-15 appointments

1. Call: AllData()
2. Filter by date
3. Return: name, time, service

---

📌 Checkup Done:
User: Mark checkup done for ahmed@gmail.com

→ Call: checkupDone(email="ahmed@gmail.com") and return the response.

---

📌 Show All Users:
User: Show all users

→ Call: AllData() and return all data.

---

⚠️ RULES:
- Use tools strictly and only when needed
- Never fake data
- Follow each step as described
- Don’t repeat calls or waste tokens
""",
    tools=[SendEmail, checked_as_accepted, checkupDone, get_user_data, AllData]
)

@cl.on_chat_start
async def ChatStart():
    await cl.Message(content="Welcome To FastAppoint Admin Panel ChatBot").send()
    cl.user_session.set("history", [])

@cl.on_message
async def MessagingStart(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})
    result = await Runner.run(ManagerAgent, history, run_config=config)
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    await cl.Message(content=result.final_output).send()
