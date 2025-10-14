import os
import re
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- Read all environment variables from your .env file ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
JENKINS_URL = os.environ.get("JENKINS_URL")
JENKINS_USER = os.environ.get("JENKINS_USER")
JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")

# --- Initialize the Slack App ---
app = App(token=SLACK_BOT_TOKEN)

# --- This is now our ONLY message listener ---
@app.event("app_mention")
def handle_mention(body, say):
    # Get the text from the message, removing the bot's mention
    message_text = body["event"]["text"]
    command_text = message_text.split('>')[1].strip() # This gets the text after "@YourBotName"

    # --- Check if the command starts with "build" ---
    if command_text.lower().startswith("build"):
        # Try to get the job name after the word "build"
        parts = command_text.split()
        if len(parts) > 1:
            job_name = parts[1]
            say(f"✅ Okay, I'm triggering a build for the '{job_name}' job in Jenkins...")

            # Construct the Jenkins job URL for triggering a build
            jenkins_job_url = f"{JENKINS_URL}/job/{job_name}/build"

            try:
                # Make the API call to Jenkins with your credentials
                response = requests.post(jenkins_job_url, auth=(JENKINS_USER, JENKINS_TOKEN))
                
                # Check if the request was successful (HTTP 201 Created)
                if response.status_code == 201:
                    say(f"🚀 Successfully triggered job '{job_name}'.")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}. Details: {response.text}")
            except Exception as e:
                say(f"An error occurred while contacting Jenkins: {e}")
        else:
            say("You need to tell me which job to build! Example: `build api-test-build`")
    
    # --- If it's not a build command, give a default reply ---
    else:
        say("Hello! I am ready to work. Try the command `build api-test-build`")

# --- Starts your app using Socket Mode ---
if __name__ == "__main__":
    print("🤖 BoltBot is running in Socket Mode...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
