import json
import subprocess
import pwd
import os

class Error(Exception):
    """Base class for my exceptions."""
    def __init__(self, message):
        self.message = message


class InvalidApplicationError(Error):
    def __init__(self):
        super().__init__('Invalid Application')


class InvalidActionError(Error):
    def __init__(self, action):
        super().__init__('Invalid Action ({})'.format(action))


class Applications:
    __valid = {}

    def __init__(self, name, user, display):
        if name not in self.__valid:
            raise InvalidApplicationError
        else:
            for k, v in self.__valid[name].items():
                setattr(self, k, v)

        self.user = user
        self.display = display

    def execute(self, action, arguments=()):
        try:
            getattr(self, action)
        except AttributeError:
            raise InvalidActionError(action)

        def run_as_user(flag):
            if flag:
                def result():
                    p = pwd.getpwnam(self.user)
                    os.setgid(p.pw_gid)
                    os.setuid(p.pw_uid)
                return result
            else:
                pass

        try:
            if action == 'start' and 'display' in self.options:
                func = subprocess.Popen
            else:
                func = subprocess.run

            env = os.environ.copy()
            if 'display' in self.options:
                env['DISPLAY'] = self.display

            return func(getattr(self, action).split() + arguments,
                        preexec_fn=run_as_user('run_as_user' in self.options),
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env).returncode
        except OSError:
            raise Error('OS Error: Apllication not found')

    @classmethod
    def get_all(cls):
        return cls.__valid

    @classmethod
    def get_killable(cls):
        return [app for app in cls.__valid if 'kill' in cls.__valid[app]['options']]

    @classmethod
    def add_application(cls, name, *args, **kwargs):
        options = []
        cls.__valid[name] = {}

        for arg in args:
            options.append(arg)

        cls.__valid[name]['options'] = options

        for arg in kwargs:
            cls.__valid[name][arg] = kwargs[arg]

    @classmethod
    def load_apps(cls, json_apps):
        cls.__valid = json.loads(json_apps)
