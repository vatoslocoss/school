import argparse
import requests
from myresponse import MyResponse


def connect(func, connurl, connjson=''):
    try:
        reply = func(connurl, timeout=timeout, json=connjson)
        return MyResponse(reply.text)
    except requests.exceptions.ConnectionError:
        return MyResponse('error', 'Server down')
    except requests.exceptions.Timeout:
        return MyResponse('warning', 'Tromparei')


port = 5000
timeout = 1
    
parser = argparse.ArgumentParser(description='Client for school management')
parser.add_argument("server", help="Insert IP(s) or hostname(s) of server(s)", nargs='?', default='localhost')
parser.add_argument("--appstart", "-s", help='Application to execute. Enclose in "..." if arguments are needed')
parser.add_argument("--appkill", "-k", help='Application to kill. Arguments are ignored')
parser.add_argument("--apprestart", "-r", help='Application to kill. Arguments are ignored')

args = parser.parse_args()

base_url = 'http://{}:{}'.format(args.server, port)

if args.appstart:
    cmd = args.appstart.split()
    url = '{}/app/{}'.format(base_url, cmd[0])
    response = connect(requests.put, url, cmd[1:])
    print(response)

if args.appkill:
    url = '{}/app/{}'.format(base_url, args.appkill.split()[0])
    response = connect(requests.delete, url)
    print(response)

if args.apprestart:
    url = '{}/app/{}'.format(base_url, args.apprestart.split()[0])
    response = connect(requests.post, url)
    print(response)