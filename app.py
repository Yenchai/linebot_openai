from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 設置計數器初始值
message_counter = 0

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    global message_counter  # 修改計數器的值
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    message_counter += 1  # 每次處理請求時，增加計數器的值
    print("計數器值:", message_counter)  # 輸出計數器的值
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter  # 訪問計數器的值
    text1 = event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text1}
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))
    message_counter += 1  # 每次處理時，增加計數器的值
    print("計數器值:", message_counter)  # 輸出計數器的值

if __name__ == '__main__':
    app.run()
