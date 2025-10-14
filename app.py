import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
JENKINS_URL = os.environ.get("JENKINS_URL")
JENKINS_USER = os.environ.get("JENKINS_USER")
JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_mention(body, say):
    event = body["event"]
    message_text = event["text"].split('>')[1].strip().lower()
    parts = message_text.split()
    
    command = parts[0] if parts else ""
    args = parts[1:]

    match command:
        case "build":
            if not args:
                say("Usage: `build <job-name>`")
                return
            job_name = args[0]
            say(f"Okay, triggering a build for '{job_name}'...")
            url = f"{JENKINS_URL}/job/{job_name}/build"
            try:
                response = requests.post(url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code == 201:
                    say(f"🚀 Successfully triggered job '{job_name}'.")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")

        case "get-last-build":
            if not args:
                say("Usage: `get-last-build <job-name>`")
                return
            job_name = args[0]
            say(f"🔎 Checking status for the last build of '{job_name}'...")
            url = f"{JENKINS_URL}/job/{job_name}/lastBuild/api/json"
            try:
                response = requests.get(url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('result', 'IN_PROGRESS')
                    say(f"Status of last build for '{job_name}' (#{data['number']}): **{result}**")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")

        case "abort-build":
            if len(args) < 2:
                say("Usage: `abort-build <job-name> <build-number>`")
                return
            job_name, build_number = args[0], args[1]
            say(f"Attempting to abort build #{build_number} for '{job_name}'...")
            url = f"{JENKINS_URL}/job/{job_name}/{build_number}/stop"
            try:
                response = requests.post(url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code in [200, 204]:
                    say(f"Successfully sent abort signal to build #{build_number}.")
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")

        case "get-build-logs":
            if len(args) < 2:
                say("Usage: `get-build-logs <job-name> <build-number>`")
                return
            job_name, build_number = args[0], args[1]
            say(f"Fetching logs for build #{build_number} of '{job_name}'...")
            url = f"{JENKINS_URL}/job/{job_name}/{build_number}/logText/progressiveText?start=0"
            try:
                response = requests.get(url, auth=(JENKINS_USER, JENKINS_TOKEN))
                if response.status_code == 200:
                    logs = response.text
                    app.client.files_upload_v2(
                        channel=event["channel"],
                        content=logs or "Build logs are empty.",
                        filename=f"{job_name}-{build_number}-logs.txt",
                        initial_comment=f"Here are the logs for *{job_name}* build *#{build_number}*:",
                        thread_ts=event["ts"]
                    )
                else:
                    say(f"🔥 Error! Jenkins returned status code: {response.status_code}.")
            except Exception as e:
                say(f"An error occurred: {e}")
        
        case _:
            say(f"Hello! I understand these commands:\n• `build <job-name>`\n• `get-last-build <job-name>`\n• `abort-build <job-name> <build-number>`\n• `get-build-logs <job-name> <build-number>`")

if __name__ == "__main__":
    print("BoltBot is running in Socket Mode...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
