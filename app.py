import os
import json

from azure.servicebus import ServiceBusService
from azure.servicebus import Message

from flask import Flask, request, abort, jsonify
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import settings

app = Flask(__name__)

host = os.getenv('HOST', 'http://localhost:8080')
line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN, host)
handler = WebhookHandler(settings.CHANNEL_SECRET)

service_namespace = 'linebot-test'
sbs = ServiceBusService(service_namespace,
                        shared_access_key_name=settings.SHARED_ACCESS_KEY_NAME,
                        shared_access_key_value=settings.SHARED_ACCESS_KEY)

obachan_full = "https://rawgit.com/Wild-Family/new-obachan-bot/master/resource/obachan_full.jpg"
obachan_thumb = "https://rawgit.com/Wild-Family/new-obachan-bot/master/resource/obachan_thumb.jpg"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'とって':
        line_bot_api.reply_message(
            event.reply_token, [
                ImageSendMessage(original_content_url=obachan_full, preview_image_url=obachan_thumb),
                TextSendMessage(text="オバチャンに任せとき！")
            ]
        )
        sbs.create_queue('test')
        msg_dict = {
            'user_id': event.source.user_id
        }
        msg_json = json.dumps(msg_dict, indent=4)
        msg = Message(msg_json)
        sbs.send_queue_message('test', msg)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

@app.route("/user/<user_id>/start")
def start(user_id):
    profile = line_bot_api.get_profile(user_id)
    line_bot_api.push_message(user_id, TextSendMessage(text=profile.display_name + "、今から撮るで！"))
    print(profile.display_name)

    return jsonify(display_name=profile.display_name)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)