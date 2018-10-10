import os
import json
import io

from azure.servicebus import ServiceBusService
from azure.servicebus import Message
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings

from flask import Flask, request, abort, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import settings

app = Flask(__name__)

host = os.getenv('HOST', 'http://localhost:8080')
if os.getenv('ENV') == "develpment":
    line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN, host)
elif os.getenv('ENV') == "production":
    line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

service_namespace = 'linebot-test'
sbs = ServiceBusService(service_namespace,
                        shared_access_key_name=settings.SHARED_ACCESS_KEY_NAME,
                        shared_access_key_value=settings.SHARED_ACCESS_KEY)

block_blob_service = BlockBlobService(
                        account_name=settings.BLOB_ACCOUNT_NAME,
                        account_key=settings.BLOB_ACCOUNT_KEY)
container_pic = "pic"
container_thumb = "thumb"

obachan_full = "https://Wild-Family.github.io/new-obachan-bot/images/obachan_full.jpg"
obachan_thumb = "https://Wild-Family.github.io/new-obachan-bot/images/obachan_thumb.jpg"
pic_url = "https://obachanbot.blob.core.windows.net/pic/"
thumb_url = "https://obachanbot.blob.core.windows.net/thumb/"

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
    if event.message.text in ['とって', '撮って', '取って', 'take a picture plz']:
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
    try:
        profile = line_bot_api.get_profile(user_id)
    except LineBotApiError:
        response = jsonify(user_id=user_id, message="user not found!")
        return response, 400

    line_bot_api.push_message(user_id, TextSendMessage(text=profile.display_name + "、今から撮るで！"))
    print(profile.display_name)

    return jsonify(user_id=user_id, display_name=profile.display_name, message="success!")

@app.route("/user/<user_id>/status")
def push_status(user_id):
    dialogue = request.args.get("dialogue")
    if dialogue is None:
        response = jsonify(user_id=user_id, dialogue=None, message="dialogue parameter is missing!")
        return response, 400

    line_bot_api.push_message(user_id, TextSendMessage(text=dialogue))

    return jsonify(user_id=user_id, dialogue=dialogue, message="success!")

@app.route("/user/<user_id>/post", methods=["GET", "POST"])
def post_pic(user_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pic' not in request.files:
            print('No file part')
            response = jsonify(user_id=user_id, message="pic parameter is missing!")
            return response, 400

        file = request.files['pic']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            image = file.read()
            settings = ContentSettings(content_type="image/jpeg")
            # create original pic blob and store it on azure storage
            block_blob_service.create_blob_from_bytes(container_pic, filename,  image, content_settings=settings)
            # create thumb
            pillow_obj = Image.open(io.BytesIO(image))
            pillow_obj.thumbnail((240, 240))
            thumb = io.BytesIO()
            pillow_obj.save(thumb, format="JPEG")
            # crate thumb blob and store it on azure storage
            block_blob_service.create_blob_from_bytes(container_thumb, filename, thumb.getvalue(), content_settings=settings)
            
            line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=pic_url + filename, preview_image_url=thumb_url + filename))

            line_bot_api.push_message(user_id, TextSendMessage(text="楽しんでや～！"))

            return jsonify(user_id=user_id, message="success!")
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=pic>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 8000))