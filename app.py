from flask import Flask
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

app = Flask(__name__)

# 设置 GPT 的个性信息（职业、能力）
gpt_personality = {
    "occupation": "证券分析师",
    "ability": "股票分析"
}

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
    messages = [
        {"role": "user", "content": text1},
        {"role": "system", "content": gpt_personality}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            temperature=0.5,
        )
        ret = response['choices'][0]['message']['content'].strip()
    except openai.error.InvalidRequestError as e:
        ret = 'OpenAI 请求无效错误：{}'.format(e)
    except Exception as e:
        ret = '发生错误：{}'.format(e)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
