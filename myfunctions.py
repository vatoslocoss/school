import configparser
import logging
from logging import handlers
from systemd import journal
import json
from applications import Applications


def parse_conf(filename, conf_dict):
    config = configparser.ConfigParser()
    config.read(filename)

    for key in ['port', 'user', 'home', 'display', 'log_journal', 'log_file']:
        conf_dict[key] = config['server'][key]
    for key in ['log_journal', 'log_file']:
        conf_dict[key] = config.getboolean('server', key)
    if conf_dict['log_file']:
        conf_dict['log_path'] = config['server'].get('log_path', 'myserver.log')
    for app in config['apps']:
        Applications.add_application(app, **json.loads(config['apps'][app]))


def generate_conf(filename):
    config = configparser.ConfigParser()
    config['server'] = {'port': '5000',
                        'log_journal': 'yes',
                        'log_file': 'no',
                        'log_path': '/var/log/myserver.log',
                        'user': 'eddie',
                        'home': '/home/eddie',
                        'display': ':0'}

    Applications.add_application('kidepedia', 'kill', 'run_as_user', 'display',
                                 start='firefox /opt/kidepedia/kidepedia.html', kill='pkill firefox')
    Applications.add_application('tuxpaint', 'kill', 'run_as_user', 'display', start='tuxpaint',
                                 kill='pkill -9 tuxpaint')
    Applications.add_application('tuxmath', 'kill', 'run_as_user', 'display', start='tuxmath', kill='pkill -9 tuxmath')
    Applications.add_application('gcompris', 'kill', 'run_as_user', 'display', start='gcompris',
                                 kill='pkill -9 gcompris')
    Applications.add_application('screensaver', 'run_as_user', kill='xscreensaver-command -display :0 -deactivate')
    Applications.add_application('xserver', restart='service lightdm restart')
    Applications.add_application('epoptes', restart='/usr/sbin/epoptes-client')
    Applications.add_application('calc', 'display', start='galculator', kill='pkill galculator')
    Applications.add_application('echo', 'run_as_user', start='whoami')
    Applications.add_application('echo2', start='whoami')

    config['apps'] = {}
    p = Applications.get_all()
    for i in p:
        config['apps'][i] = json.dumps(p[i])

    with open(filename, 'w') as configfile:
        config.write(configfile)


def initialize_logger(logger, debug, log_to_journal, log_to_file, filename=None):
    logger.setLevel(logging.INFO)

    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
        logger.setLevel(logging.DEBUG)
    else:
        if log_to_journal:
            handler = journal.JournaldLogHandler()
            handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            handler.setLevel(logging.WARNING)
            logger.addHandler(handler)

        if log_to_file:
            handler = handlers.RotatingFileHandler(filename, maxBytes=1048576, backupCount=2)
            handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
            logger.addHandler(handler)

        if not logger.hasHandlers():
            logger.addHandler(logging.NullHandler())
