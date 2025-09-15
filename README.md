# PingPlan 🤖✅

> Your personal AI assistant to conquer chaos in your WhatsApp group chats. Never miss a task or deadline again.

![Language](https://img.shields.io/badge/Language-Python-blue?style=for-the-badge)
![Framework](https://img.shields.io/badge/Framework-Flask-black?style=for-the-badge)
![API](https://img.shields.io/badge/API-Twilio-red?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge)

---

## The Problem: Information Overload
For college students, our lives are run on WhatsApp. But critical tasks, assignments, and deadlines from classes and project groups get buried under hundreds of messages every day. Manually tracking everything is stressful and leads to missed deadlines.

## The Solution: A Single Ping for Your Plan
**PingPlan** is an intelligent assistant that lives right inside WhatsApp. Instead of manually creating a to-do list, you simply **forward any message containing a task** to the PingPlan bot. Our AI does the rest, turning unstructured chat into an organized, actionable plan.

## 🚀 Live Demo
**This is the most important part of the README.** It's a quick showcase of PingPlan in action.

![update 2](https://github.com/user-attachments/assets/4c4c0e86-ff27-45ce-af11-bea994c0049b)




---

## ✨ Core Features

* **🧠 Intelligent Task Parsing:** Leverages Google's Gemini API to accurately extract task descriptions, deadlines, and project names from natural language messages.
* **📋 Centralized To-Do List:** Consolidates all your tasks from every chat into a single, easy-to-read list, accessible anytime.
* **📲 Simple WhatsApp Commands:** No new app to learn. Interact with your task list using simple commands like `show my tasks` and `delete [number]`.
* **😎 Flexible & Friendly:** Understands typos in commands (e.g., "show my task") and has a touch of personality.

---

## 🛠️ Tech Stack

* **Backend:** Python with the Flask web framework.
* **WhatsApp Integration:** Twilio API for WhatsApp.
* **Natural Language Processing:** Google Gemini Pro API.
* **Data Storage:** A simple and robust JSON file for persistent, user-specific task storage.
* **Development Tunneling:** Ngrok to expose the local server during development.

---

## ⚙️ Setup and Installation

To get a local copy up and running, follow these steps.

### Prerequisites
* Python 3.8+
* A Twilio account with the WhatsApp Sandbox configured.
* A Google Gemini API Key.
* `ngrok` installed and authenticated.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/thomasalex122/PingPlan.git](https://github.com/thomasalex122/PingPlan.git)
    cd PingPlan
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: Ensure you've created `requirements.txt` by running `pip freeze > requirements.txt`)*

4.  **Set up your environment variables:**
    * Create a file named `.env` in the root directory.
    * Add your Gemini API Key to this file:
        ```env
        GEMINI_API_KEY=AIzaSyAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        ```

5.  **Run the application:**
    ```sh
    flask run
    ```

6.  **Expose your local server with ngrok:**
    * In a new terminal window, run:
        ```sh
        ngrok http 5000
        ```
    * Copy the `https://...` forwarding URL.

7.  **Configure the Twilio Webhook:**
    * Go to your Twilio WhatsApp Sandbox settings.
    * Paste your ngrok URL into the "WHEN A MESSAGE COMES IN" field and add `/whatsapp` at the end.
    * Save the configuration.

---

## 📲 How to Use

* **Add a Task:** Forward any message containing a task to the PingPlan bot.
* **View Tasks:** Send `show my tasks` (or `show my task`).
* **Delete a Task:** Send `delete [number]` (e.g., `delete 1`).

---

## 💡 Future Vision

This MVP is just the beginning. The future of PingPlan includes:

* **⏰ Proactive Reminders:** The bot will intelligently schedule and send reminders before a task is due.
* **🚀 Live Deployment:** Move from the Twilio Sandbox to the full WhatsApp Business API with official "PingPlan" branding.
* **📅 Google Calendar Integration:** Automatically sync tasks with deadlines to the user's Google Calendar.

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
