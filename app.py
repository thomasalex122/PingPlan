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
    msg_lower = incoming_msg.lower()

    try: 
        # --- Command Logic (Order of Priority) ---
        # 1. Handle "show tasks" command (flexible and concise)
        if 'show' in msg_lower and 'task' in msg_lower: # Catches "show task", "show tasks", "show my task", etc.
            if not user_tasks:
                response_text = "You have no pending tasks! 🎉"
            else:
                response_text = "📝 *Your PingPlan Tasks:*\n\n"
                for i, task in enumerate(user_tasks, 1):
                    deadline_str = task.get('deadline', '') 
                    deadline_display = f"_Due: {deadline_str}_" if deadline_str else "" 
                    
                    project_name_display = task.get('project_name', '')
                    project_display = f" | Project: *{project_name_display}*" if project_name_display else ""
                    
                    task_line = f"*{i}. {task['task_description']}*\n"
                    details_line = ""
                    if deadline_display or project_display:
                        details_line = f"   {deadline_display}{project_display}\n"
                    
                    response_text += f"{task_line}{details_line}\n"
                
                response_text += "Type `delete [number]` to remove a task."

        # 2. Handle "delete" command (single task delete for maximum stability)
        elif msg_lower.startswith('delete '):
            if not user_tasks:
                response_text = "You have no tasks to delete."
            else:
                try:
                    task_num_str = msg_lower.split(' ')[1].strip()
                    task_num_to_delete = int(task_num_str)
                    
                    if 1 <= task_num_to_delete <= len(user_tasks):
                        deleted_task = user_tasks.pop(task_num_to_delete - 1)
                        all_tasks[from_number] = user_tasks
                        save_tasks(all_tasks)
                        response_text = f"✅ Task deleted: *{deleted_task['task_description']}*"
                    else:
                        response_text = f"❌ Invalid task number. You have {len(user_tasks)} tasks."
                except (ValueError, IndexError):
                    response_text = "❌ Please use the format: `delete [number]` (e.g., `delete 1`)"

        # 3. Handle "thanks" (the personality touch)
        elif any(word in msg_lower for word in ['thanks', 'thank you', 'thx', 'ty']):
            response_text = "My pleasure to help! 😊"

        # 4. Default to Gemini parsing for all other messages
        else:
            parsed_task = parse_message_with_gemini(incoming_msg)
            if parsed_task:
                user_tasks.append(parsed_task)
                all_tasks[from_number] = user_tasks
                save_tasks(all_tasks)
                
                deadline_display = f"_Due: {parsed_task.get('deadline', '')}_" if parsed_task.get('deadline') else ""
                project_name_display = parsed_task.get('project_name', '')
                project_display = f" | Project: *{project_name_display}*" if project_name_display else ""
                
                response_text = f"✅ *Task Added!*\n\n*{parsed_task['task_description']}*\n{deadline_display}{project_display}".strip()
            else:
                response_text = "Sorry, I didn't quite get that. Try:\n• Forwarding a task message\n• Typing `show my tasks`\n• Using `delete [number]`"
    except Exception as e:
        print(f"CRITICAL ERROR: Unhandled exception in whatsapp_webhook: {e}")
        response_text = "An unexpected error occurred. Please try again or contact support. 🚨"

    resp.message(response_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)