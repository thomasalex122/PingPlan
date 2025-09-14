import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Gemini parsing will fail.")

# MASTER PROMPT (v4.0 - Final, Competition Ready, Concise)
MASTER_PROMPT = """
You are PingPlan, an expert AI assistant for a WhatsApp bot. Your primary goal is to be a precise and concise task parser.

Your response MUST be ONLY a valid JSON object or the literal string "null".

**JSON Object Rules:**
* **"task_description"**: REQUIRED. **Summarize** the user's message into a short, clear, actionable task. Do NOT include fluff like "Please Note" or "Attendance is mandatory".
* **"deadline"**: Extract the most relevant deadline. If multiple dates for a single event are mentioned, **summarize them** (e.g., "Multiple sessions, Sep 9-19"). If no deadline exists, use an empty string "".
* **"project_name"**: Extract a concise project, course, or context name. If the context is personal (e.g., "call mom"), use "Personal". If no context is found, use an empty string "".

**CRITICAL RULE for returning "null":**
You MUST return "null" if the message is NOT a clear, actionable task. This includes general conversation, questions, and bot commands. **If in doubt, return "null".**

**EXAMPLES:**

User message: "Complete python assignment: 7+ page written assignment on Python datatypes and variables (right side only); video presentation (3-5 mins). Choose a unique topic. Due: Monday"
Your response:
{"task_description": "Complete 7+ page written assignment and 3-5 min video presentation", "deadline": "Monday", "project_name": "Python"}

User message: "Please Note Ignitors sessions will be held next week on September 9, 10, 13, 15, 16, and 19 from 12:00 PM to 12:50 PM. Attendance is mandatory."
Your response:
{"task_description": "Attend all Ignitors sessions", "deadline": "Multiple sessions, Sep 9-19", "project_name": "Ignitors"}

User message: "don't forget to call mom tomorrow"
Your response:
{"task_description": "Call mom", "deadline": "tomorrow", "project_name": "Personal"}

User message: "can you show me my tasks please"
Your response:
null
"""

def parse_message_with_gemini(user_message):
    if not GEMINI_API_KEY:
        return None
    
    try:
        full_prompt = MASTER_PROMPT + "\n\nUser message: \"" + user_message + "\"\nYour response:"
        response = model.generate_content(full_prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        if response_text.lower() == 'null':
            print(f"DEBUG: Gemini classified '{user_message}' as a non-task.")
            return None
        
        try:
            parsed_data = json.loads(response_text)
            required_keys = ['task_description', 'deadline', 'project_name']
            if all(key in parsed_data for key in required_keys) and parsed_data.get("task_description"):
                return parsed_data
            else:
                print(f"WARNING: Gemini returned invalid JSON or empty task_description for '{user_message}': {parsed_data}")
                return None
        except json.JSONDecodeError:
            print(f"ERROR: JSON parsing failed for response from Gemini: '{response_text}' for user message: '{user_message}'")
            return None
            
    except Exception as e:
        print(f"ERROR: Exception calling Gemini API for user message '{user_message}': {e}")
        return None