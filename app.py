import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- Read all environment variables ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
JENKINS_URL = os.environ.get("JENKINS_URL")
JENKINS_USER = os.environ.get("JENKINS_USER")
JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")

# --- Initialize the Slack App ---
app = App(token=SLACK_BOT_TOKEN)

# --- This is our main command handler ---
@app.event("app_mention")
def handle_mention(body, say):
    message_text = body["event"]["text"]
    # We get a list of words after the bot's mention, e.g., ['build', 'api-test-build']
    parts = message_text.split('>')[1].strip().lower().split()
    
    # The first word is the command itself
    command = parts[0] if parts else ""

    # --- Logic for the "build" command ---
    if command == "build":
        if len(parts) >= 2:
            job_name = parts[1]
            say(f"✅ Okay, triggering a build for '{job_name}'...")
            jenkins_job_url = f"{JENKINS_URL}/job/{job_name}/build"
            try:
                response = requests.post(jenkins_job_url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code == 201:
                    say(f"🚀 Successfully triggered job '{job_name}'.")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")
        else:
            say("Usage: `build <job-name>`")

    # --- NEW: Logic for the "get-last-build" command ---
    elif command == "get-last-build":
        if len(parts) >= 2:
            job_name = parts[1]
            say(f"🔎 Checking status for the last build of '{job_name}'...")
            jenkins_job_url = f"{JENKINS_URL}/job/{job_name}/lastBuild/api/json"
            try:
                response = requests.get(jenkins_job_url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('result', 'IN_PROGRESS')
                    duration_ms = data.get('duration', 0)
                    duration_s = duration_ms / 1000
                    say(f"Status of last build for '{job_name}' (#{data['number']}): **{result}** (Duration: {duration_s:.2f}s)")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")
        else:
            say("Usage: `get-last-build <job-name>`")

    # --- Default reply if no command is matched ---
    else:
        say(f"Hello! I understand the following commands:\n• `build <job-name>`\n• `get-last-build <job-name>`")

# --- Starts your app using Socket Mode ---
if __name__ == "__main__":
    print("🤖 BoltBot is running in Socket Mode...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
