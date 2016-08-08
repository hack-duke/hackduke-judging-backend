from flask import Flask, request, jsonify
from judging_sessions import SimpleSession
from redis_store import redis

app = Flask(__name__)

########

@app.route("/")
def hello():
    return "Hello World!"

curr_session = None

@app.route("/init", methods = ['POST'])
def init_judge_session():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()

    if 'num_alts' not in json_args:
        result['error'] = 'Not enough args'
    else:
        num_alts = json_args['num_alts']
        try:
            num_alts = int(num_alts)
        except ValueError:
            result['error'] = 'Not an integer num_alts'
            return jsonify(result)
        if num_alts <= 0:
            result['error'] = 'Not a positive num_alts'
            return jsonify(result)
        global curr_session
        curr_session = SimpleSession(num_alts)
        result['error'] = ''
    return jsonify(result)

@app.route('/get_decision', methods = ['POST'])
def get_decision():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()
    if curr_session is None:
        result['error'] = 'Need to init first!'
        return jsonify(result)
    if 'judge_id' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id = json_args['judge_id']
    a,b = curr_session.get_decision(judge_id)
    result['choice_a'] = a
    result['choice_b'] = b
    return jsonify(result)

@app.route('/perform_decision', methods = ['POST'])
def perform_decision():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()

    if curr_session is None:
        result['error'] = 'Need to init first!'
        return jsonify(result)
    if 'judge_id' not in json_args or 'favored' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id, favored = json_args['judge_id'], json_args['favored']
    result['error'] = curr_session.perform_decision(judge_id, favored)
    return jsonify(result)

@app.route('/results')
def results():
    result = dict()
    if curr_session is None:
        result['error'] = 'Need to init first!'
        return result
    result['votes'] = curr_session.get_results()
    result['error'] = ''
    return jsonify(result)

if __name__ == "__main__":
    app.run()

