# server.py

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
messages = []
message_id = 0
user_count = 0


@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the Flask Messenger!'})


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({
        'messages': messages,
        'message_count': len(messages),
        'user_count': user_count
    })


@app.route('/message', methods=['POST'])
def add_message():
    global message_id
    message = request.form.get('message')
    message_id += 1
    messages.append({'id': message_id, 'content': message})
    return jsonify({'id': message_id})


@app.route('/messages/<int:last_message_id>', methods=['GET'])
def get_new_messages(last_message_id):
    new_messages = [message for message in messages if message['id'] > last_message_id]
    return jsonify({'messages': new_messages})


@app.route('/user', methods=['POST'])
def increment_user_count():
    global user_count
    user_count += 1
    return jsonify({'user_count': user_count})


@app.route('/user', methods=['DELETE'])
def decrement_user_count():
    global user_count
    user_count -= 1
    return jsonify({'user_count': user_count})


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'user_count': user_count,
        'message_count': len(messages),
        'status': 'Ok!',
    })


@app.route('/command', methods=['POST'])
def process_command():
    command = request.form.get('command')
    response = {}

    if command == '\\help':
        response['message'] = 'Welcome to the messenger! Here are the available commands:\n' \
                              '\\help - Show this help message.\n' \
                              '\\anonymous - Send an anonymous message.\n' \
                              '\\stats - Show user and message statistics.'

    elif command == '\\anonymous':
        response['message'] = 'You are sending an anonymous message. Enter your message after the command.'

    elif command == '\\stats':
        response['message'] = f'Number of users: {user_count}\nNumber of messages: {len(messages)}'

    elif command == '\\time':
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response['message'] = f'Current time: {current_time}'

    else:
        response['message'] = 'Unknown command. Type \\help for a list of available commands.'

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)