from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from dotenv import load_dotenv
from parser_gemini import parse_message_with_gemini

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Task storage functions
def load_tasks():
    """
    Load tasks from tasks.json file.
    
    Returns:
        dict: Dictionary containing all user tasks, or empty dict if file doesn't exist
    """
    try:
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}")
        return {}

def save_tasks(tasks_data):
    """
    Save tasks to tasks.json file.
    
    Args:
        tasks_data (dict): Dictionary containing all user tasks to save
    """
    try:
        with open('tasks.json', 'w', encoding='utf-8') as file:
            json.dump(tasks_data, file, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving tasks: {e}")

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook endpoint to receive messages from Twilio WhatsApp integration
    """
    # Get the incoming message from Twilio
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Create Twilio response object
    resp = MessagingResponse()
    
    # Load existing tasks
    tasks = load_tasks()
    
    # Initialize user's task list if they don't exist
    if from_number not in tasks:
        tasks[from_number] = []
    
    # Handle different commands
    if not incoming_msg:
        response_text = "Please send me a message! I can help you manage your tasks."
    
    # Show tasks command
    elif any(keyword in incoming_msg.lower() for keyword in ['show my tasks', 'show tasks', 'list tasks', 'my tasks']):
        user_tasks = tasks[from_number]
        if not user_tasks:
            response_text = "You don't have any tasks yet! Forward me a message with a task to get started."
        else:
            response_text = "*Your Tasks:*\n\n"
            for i, task in enumerate(user_tasks, 1):
                deadline_text = f"_Due: {task['deadline']}_" if task['deadline'] != "Not specified" else "_No deadline specified_"
                response_text += f"{i}. *{task['task_description']}*\n   {deadline_text}\n   Project: {task['project_name']}\n\n"
            response_text += "Type 'delete [number]' to remove a task."
    
    # Delete task command
    elif incoming_msg.lower().startswith('delete '):
        try:
            # Extract task number
            task_num = int(incoming_msg.split()[1])
            user_tasks = tasks[from_number]
            
            if 1 <= task_num <= len(user_tasks):
                deleted_task = user_tasks.pop(task_num - 1)
                save_tasks(tasks)
                response_text = f"✅ Task deleted: *{deleted_task['task_description']}*"
            else:
                response_text = f"❌ Invalid task number. You have {len(user_tasks)} tasks. Use numbers 1-{len(user_tasks)}."
        except (ValueError, IndexError):
            response_text = "❌ Please use the format: 'delete [number]' (e.g., 'delete 1')"
    
    # Default: Try to parse as a task
    else:
        # Parse the message with Gemini
        parsed_task = parse_message_with_gemini(incoming_msg)
        
        if parsed_task:
            # Add task to user's list
            tasks[from_number].append(parsed_task)
            save_tasks(tasks)
            
            # Create confirmation message
            deadline_text = f"_Due: {parsed_task['deadline']}_" if parsed_task['deadline'] != "Not specified" else "_No deadline specified_"
            response_text = f"✅ *Task Added!*\n\n*{parsed_task['task_description']}*\n{deadline_text}\nProject: {parsed_task['project_name']}\n\nType 'show my tasks' to see all your tasks."
        else:
            # Fallback for parsing failures
            response_text = "Sorry, I didn't understand that. Try:\n• Forwarding a task message\n• Typing 'show my tasks'\n• Using 'delete [number]' to remove a task"
    
    # Add the response message
    resp.message(response_text)
    
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
