import sys
import json
import requests

from serialize import marshal
from deserialize import unmarshal
from check import check_arg


registry_url = "https://registry-service-provider.herokuapp.com"

client_ip_request = requests.get('http://myip.dnsomatic.com/')
client_ip = client_ip_request.content.decode().split(',')
client_ip = client_ip[0]
print(client_ip)
print()


def get_signature(proc_name):
    headers = {
        "data": json.dumps({"serviceName": proc_name})
    }
    result = requests.get(registry_url + "/service-provider", headers=headers)

    return json.loads(result.content)


def rpc_call(proc_name, *args):
    proc_signature = get_signature(proc_name)
    proc_parameters = sorted(proc_signature['parameters'], key=lambda x: x['parameterPosition'])
    payload = {
        "serviceName": proc_name,
        "parameters": [],
        "clientIp": client_ip
    }

    with open('config_vars.txt', 'r+') as f:
        request_no = int(f.read())
        payload['requestID'] = request_no

    for i, arg in enumerate(args):
        if check_arg(arg, proc_parameters[i]['parameterType']):
            param_body = {
                "parameterPosition": i + 1,
                "parameterValue": marshal(arg, proc_parameters[i]['parameterType'])
            }
            payload["parameters"].append(param_body)
        else:
            sys.exit("ERROR: Value of passed argument does not match type specified in remote procedure signature")

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        result = requests.post(proc_signature['serverAddress'], data=json.dumps(payload), headers=headers)
    except requests.Timeout as e:
        return rpc_call(proc_name, *args)

    with open('config_vars.txt', 'r+') as f:
        f.seek(0)
        f.write(str(payload['requestID'] + 1))
        f.truncate()

    unmarshalled_result = unmarshal(json.loads(result.content), proc_signature['returnType'])

    return unmarshalled_result
