import json
import requests
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo

import procedures
from serialize import marshal
from deserialize import unmarshal


app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
app.config["MONGO_URI"] = "mongodb://test:test1234@ds163905.mlab.com:63905/service-provider"
CORS(app)
mongo = PyMongo(app)

with open("services.json") as data_file:
    signature = json.load(data_file)

registry_url = "https://registry-service-provider.herokuapp.com"
server_url = 'http://5ddfd841.ngrok.io'


def register_rpc(service_sign):
    headers = {
        'Content-Type': 'application/json'
    }
    result = requests.post(registry_url + '/map', data=json.dumps(service_sign), headers=headers)

    if result.status_code != 200:
        print('ERROR: RPC Registration Failed')

    return result


def call_proc(proc_name, args):
    if proc_name == 'is_even':
        return procedures.is_even(*args)
    elif proc_name == 'find_count':
        return procedures.find_count(*args)
    elif proc_name == 'find_sum':
        return procedures.find_sum(*args)
    elif proc_name == 'add_account':
        return procedures.add_account(mongo, *args)
    elif proc_name == 'update':
        return procedures.update(mongo, *args)
    elif proc_name == 'get_account':
        return procedures.get_account(mongo, *args)


def check_duplicate(client_id, request_no):
    stored_result = mongo.db.responses.find_one({"ipAddress": client_id, "requestID": request_no})

    if stored_result:
        return True, stored_result['result']
    else:
        return False, 'No stored result'


def update_stored_result(client_id, request_no, result):
    stored_result = mongo.db.responses.find_one({'ipAddress': client_id})

    if stored_result:
        mongo.db.responses.update_one({'ipAddress': client_id}, {
            '$set': {
                'requestID': request_no,
                'result': result
            }
        })
    else:
        mongo.db.responses.insert_one({'ipAddress': client_id, 'requestID': request_no, 'result': result, 'service': ''})


def notify_registry():
    headers = {
        'data': json.dumps({'serverAddress': server_url})
    }

    result = requests.put(registry_url + '/completed', headers=headers)
    print(result.content)
    if result.status_code != 200:
        print('ERROR: Notify registry failed')


@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/active', methods=['GET'])
def active():
    return make_response(json.dumps({'result': True}))


@app.route('/', methods=['POST'])
def remote_call():
    data = request.get_json()
    client_ip = data['clientIp']
    request_id = data['requestID']
    is_duplicate, stored_result = check_duplicate(client_ip, request_id)

    if is_duplicate:
        return make_response(stored_result), 200

    proc_name = data["serviceName"]
    marshalled_args = sorted(data['parameters'], key=lambda x: x['parameterPosition'])
    proc_signature = signature[proc_name]
    proc_parameters = sorted(proc_signature['parameters'], key=lambda x: x['position'])
    args = []

    for i, arg in enumerate(marshalled_args):
        args.append(unmarshal(arg['parameterValue'], proc_parameters[i]['type']))

    result = call_proc(proc_name, args)
    print(result)
    marshalled_result = marshal(result, proc_signature['returnType'])
    json_response = json.dumps(marshalled_result)

    update_stored_result(client_ip, request_id, json_response)
    notify_registry()

    return make_response(json_response), 200


if __name__ == '__main__':
    # register_rpc(signature['get_account'])
    # register_rpc(signature['update'])
    app.run(debug=True, use_reloader=False)
