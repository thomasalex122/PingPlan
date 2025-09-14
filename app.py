from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from dotenv import load_dotenv
from parser_gemini import parse_message_with_gemini

load_dotenv()
app = Flask(__name__)

# --- Data Storage Functions ---
def load_tasks():
    try:
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}
    except Exception as e:
        print(f"Error loading tasks: {e}")
        return {}

def save_tasks(tasks_data):
    try:
        with open('tasks.json', 'w', encoding='utf-8') as file:
            json.dump(tasks_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving tasks: {e}")

# --- Main WhatsApp Webhook ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    resp = MessagingResponse()
    
    all_tasks = load_tasks()
    user_tasks = all_tasks.get(from_number, [])
    
    response_text = ""

    # --- Command Logic (Order of Priority) ---
    # 1. Handle "show tasks" command (more flexible)
    if 'show' in incoming_msg.lower() and 'task' in incoming_msg.lower():
        if not user_tasks:
            response_text = "You have no pending tasks! 🎉"
        else:
            response_text = "*Your Tasks:*\n\n"
            for i, task in enumerate(user_tasks, 1):
                deadline = f"_Due: {task['deadline']}_" if task.get('deadline') else "_No deadline specified_"
                project = f"Project: {task['project_name']}" if task.get('project_name') else ""
                response_text += f"{i}. *{task['task_description']}*\n   {deadline}\n   {project}\n\n".strip() + "\n"
            response_text += "Type 'delete [number]' to remove a task."

    # 2. Handle "delete" command (smarter multi-delete)
    elif incoming_msg.lower().startswith('delete '):
        if not user_tasks:
            response_text = "You have no tasks to delete."
        else:
            try:
                parts = incoming_msg.split()[1:]
                indices_to_delete = sorted([int(num) - 1 for num in parts], reverse=True)
                deleted_tasks_desc = []
                valid_indices = True
                for index in indices_to_delete:
                    if 0 <= index < len(user_tasks):
                        deleted_task = user_tasks.pop(index)
                        deleted_tasks_desc.append(deleted_task['task_description'])
                    else:
                        valid_indices = False
                if deleted_tasks_desc:
                    all_tasks[from_number] = user_tasks
                    save_tasks(all_tasks)
                    response_text = f"✅ Deleted task(s): *{', '.join(deleted_tasks_desc)}*"
                    if not valid_indices:
                        response_text += "\n(Note: One or more numbers were invalid.)"
                else:
                    response_text = f"❌ Invalid task number(s). You have {len(user_tasks)} tasks."
            except (ValueError, IndexError):
                response_text = "❌ Please use the format: 'delete [num1] [num2]'"

    # 3. Handle "thanks" (the personality touch)
    elif any(word in incoming_msg.lower() for word in ['thanks', 'thank you', 'thx', 'ty']):
        response_text = "My pleasure to help! 😊"

    # 4. Default to Gemini parsing for all other messages
    else:
        parsed_task = parse_message_with_gemini(incoming_msg)
        if parsed_task:
            user_tasks.append(parsed_task)
            all_tasks[from_number] = user_tasks
            save_tasks(all_tasks)
            deadline = f"_Due: {parsed_task['deadline']}_" if parsed_task.get('deadline') else "_No deadline specified_"
            project = f"Project: {parsed_task['project_name']}" if parsed_task.get('project_name') else ""
            response_text = f"✅ *Task Added!*\n\n*{parsed_task['task_description']}*\n{deadline}\n{project}".strip()
        else:
            response_text = "Sorry, I didn't quite get that. Try:\n• Forwarding a task message\n• Typing 'show my tasks'\n• Using 'delete [number]'"
    
    # Send the final response
    resp.message(response_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)