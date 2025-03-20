#...

import time
import random
from flask import Flask, request, jsonify

from services.waha import Waha
from bot.ai_bot import AIBot

#...

app = Flask(__name__)


@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json

    print(f'EVENTO RECEBIDO: {data}')

    waha = Waha()
    ai_bot = AIBot()

    chat_id = data['payload']['from']
    received_message = data['payload']['body']

    waha.start_typing(chat_id=chat_id)
    time.sleep(random.randint(3, 10))

    response = ai_bot.invoke(question=received_message)
    waha.send_message(
        chat_id=chat_id,
        # message='To away, esta resposta é automática gerada com python, respondo depois...',
        message=response,
    )
    waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
