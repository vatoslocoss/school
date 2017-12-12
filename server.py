from flask import Flask, request
from myfunctions import initialize_logger, parse_conf, generate_conf
from applications import Applications, Error
from myresponse import MyResponse
import argparse
import sys
import logging

parser = argparse.ArgumentParser(description='Server process for school management')
parser.add_argument("--config", "-c", help='Configuration file', nargs='?', default='server.conf')
parser.add_argument("--debug", "-d", action="store_true", help='Run in debug mode (Default loggin is disabled)')
parser.add_argument("--createconf", help='Generate default config file')
args = parser.parse_args()

if args.createconf:
    generate_conf(args.createconf)
    quit(0)

conf = {}    # dictionary to keep all configuration values
try:
    parse_conf(args.config, conf)
except:
    sys.exit('Error in configuration file: {}'.format(args.config))

logger = logging.getLogger('MyServer')
initialize_logger(logger, args.debug, conf['log_journal'], conf['log_file'], conf.get('log_path'))

server = Flask(__name__)

app_action = {'POST': 'restart', 'PUT': 'start', 'DELETE': 'kill'}


@server.route('/app', defaults={'application': None}, methods=['DELETE'])    # kill all applications with kill option
@server.route('/app/<application>', methods=['POST', 'PUT', 'DELETE'])
def handle_app(application):
    logger.info('Received request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
    if not application:
        try:
            for name in Applications.get_killable():
                app = Applications(name, conf['user'], conf['display'])
                app.execute(app_action[request.method], [])
            logger.info('Served request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
            return MyResponse('success', 'Applications killed').make_response()
        except Error as e:
            logger.warning('Invalid request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
            return MyResponse('error', e.message).make_response()
    try:
        app = Applications(application, conf['user'], conf['display'])
        p = app.execute(app_action[request.method], list(request.json))
        logger.info('Served request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
        return MyResponse(app_action[request.method], p).make_response()
    except Error as e:
        logger.warning('Invalid request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
        return MyResponse('error', e.message).make_response()


@server.errorhandler(404)     # Invalid url
@server.errorhandler(405)     # Invalid method for url
def page_not_found():
    logger.warning('Invalid request from {} ({} {})'.format(request.remote_addr, request.method, request.path))
    return MyResponse('error', 'Invalid request').make_response()


if __name__ == '__main__':
    server.run(debug=True)
