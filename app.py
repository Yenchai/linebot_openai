from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text1 = event.message.text
    # 定義用戶的個性資訊
    user_profile = {
        "occupation": "證券分析師",  # 用戶的職業
        "ability": "股票分析"         # 用戶的能力
    }
    # 呼叫 OpenAI 的 ChatCompletion API，並傳入用戶的個性資訊
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text1},
            {"role": "system", "content": user_profile}  # 將用戶個性資訊添加到請求中
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
