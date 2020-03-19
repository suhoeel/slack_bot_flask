from app import app
from flask import request, jsonify, Response, json
from slackeventsapi import SlackEventAdapter

import os
import slack
import requests

@app.route('/slack', methods=['GET', 'POST'])
def verifyUrl():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        challenge = request.args.get('challenge')
        return Response(challenge, mimetype='application/x-www-form-urlencoded')
    # data = request.get_json()
    # challenge = data['challenge']
    if "event" in slack_event:
        event_type = slack_event['event']['type']
        return event_handler(event_type, slack_event)
    return Response(404)

@app.route('/')
def verifyCode():
    code = request.args.get('code')
    r = requests.post(url="https://slack.com/api/oauth.v2.access", data={'client_id':'463946765123.1009420232567', 'client_secret':'07ffbd10ddcc260a0fe58c496f6f4a68', 'code':code})
    data = r.text
    print(data)
    return 'auth success'


@app.route('/send')
def webhook():
    r = requests.post(url="https://hooks.slack.com/services/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", json={'text': '현중박'}, headers={'Content-Type': 'application/json'})
    print(r.text)
    return 'send msg'

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = slack.WebClient(token=slack_bot_token)

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    print("a")
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        slack_client.api_call("chat.postMessage", channel=channel, text=message)

    # 이벤트 핸들하는 함수
def event_handler(event_type, slack_event):
    print(event_type)
    print(slack_event)
    if event_type == "app_mention":
        channel = slack_event['event']['channel']
        text = "이제부터 시작이다."
        slack_client.chat_postMessage(channel=channel, text=text)
        return 'wow'
    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return Respnose(401)
    
# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    print("b")
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.api_call("chat.postMessage", channel=channel, text=text)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))




