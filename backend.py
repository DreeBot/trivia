# server.py
import dumper
import random
import requests
import csv
import eventlet
import os
import socketio
import html

sio = socketio.Server(cors_allowed_origins=os.environ["FRONTEND_URL"])
app = socketio.WSGIApp(sio)

questions = []
round_count = 0
correct_answer = ''
players = {}
score = {}
participation = {}
time = 0
max_time = 15


def load_questions(set_type, set_id):
    global questions
    questions = [];
    if (set_type == "csv"):
        with open(f'{os.environ["DATA_PATH"]}{set_id}.csv', 'r') as file:
            reader = csv.reader(file)
            questions = list(reader)
    else:
        if (set_type == "otdb"):
            category = ""
            if (set_id != 'any'):
                category = f'&category={set_id}'
            request_uri = f'https://opentdb.com/api.php?amount={round_count}{category}&type=multiple'
            print(request_uri)
            response = requests.get(request_uri)
            response_data = response.json()
            if (response_data['response_code'] == 0):
                for otdb in response_data['results']:
                    question = [html.unescape(otdb['question']), html.unescape(otdb['correct_answer'])]
                    for incorrect in otdb['incorrect_answers']:
                        question.append(html.unescape(incorrect))
                    questions.append(question)
    random.shuffle(questions)  # Shuffle the questions

def start_round():
    global round_count, correct_answer, players, time
    print(f'Starting round {round_count}')
    if round_count > 0:
        question_data = questions[round_count % len(questions)]
        answers = question_data[1:]
        random.shuffle(answers)  # Shuffle the answers
        correct_answer = answers.index(question_data[1])+1
        print(f'Question: {question_data[0]}')
        print(f'Answer text: {question_data[1]}')
        print(f'Candidates:')
        print(f'  {answers[0]}')
        print(f'  {answers[1]}')
        print(f'  {answers[2]}')
        print(f'  {answers[3]}')
        print(f'Answer: {correct_answer}')
        sio.emit('question', {'question': question_data[0], 'answers': answers, 'round': round_count})
        players = {}
        round_count -= 1
        time = max_time
        eventlet.spawn(countdown_timer)
    else:
        sio.emit('end', {'score': score, 'participation': participation})

def countdown_timer():
    global time, round_count, players, correct_answer, score
    while time > 0:
        eventlet.sleep(1)
        print(f'Timer: {time}')
        sio.emit('timer', time)
        time -= 1

    correct_players = [name for name, answer in players.items() if answer == correct_answer]
    for player in correct_players:
        if player in score:
            score[player] += 1
        else:
            score[player] = 1

    for player in players:
        if player in participation:
            participation[player] += 1
        else:
            participation[player] = 1

    sio.emit('round', {'correct_answer': correct_answer, 'correct_players': correct_players, 'score': score, 'participation': participation})
    eventlet.sleep(5)
    start_round()

# Handle 'start_game' event
@sio.event
def start_game(sid, data):
    global round_count, max_time, score, participation
    set_id = data['set_id']
    set_type = data['set_type']
    round_count = int(data['rounds'])
    max_time = int(data['seconds'])
    score = {}
    participation = {}
    print(f'Received start_game event for {set_type} with set name: {set_id}')
    load_questions(set_type, set_id)
    start_round()

# Handle 'answer' event
@sio.event
def answer(sid, data):
    players[data['name']] = data['answer']
    print(f'Received answer event from {data["name"]} with answer: {data["answer"]}')

if __name__ == '__main__':
    # Create a WSGI server for the socket.io app
    socketio_server = eventlet.listen(('0.0.0.0', int(os.getenv("PORT", "5000"))))

    # Run the socket.io server
    eventlet.wsgi.server(socketio_server, app)

