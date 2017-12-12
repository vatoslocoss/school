import json
from flask import jsonify


class MyResponse(object):
    __actions = ('start', 'kill')
    __success = {'start': 'Application started',
                 'kill': 'Application terminated'}
    __fail = {'kill': 'Application was not running'}

    def __init__(self, *args):
        """MyResponse instance is made from 2 attributes: code, comment.
        In order to create object you can call init with 3 ways:
        1. MyResponse(instance_code_value, instance_comment_value)
        2. MyResponse(action_name, return_code)
        3. MyResponse(json_returned_by_server) """

        if len(args) == 2:
            if args[0] in self.__actions:
                self.code = 'success'
                if args[1] == 0:
                    self.comment = self.__success[args[0]]
                else:
                    self.comment = self.__fail.get(args[0], 'Unknown runtime error')
            else:
                self.code = args[0]
                self.comment = args[1]
        else:       # parse server response
            try:
                r = json.loads(args[0])
                self.code = r['code']
                self.comment = r['comment']
            except:
                self.code = 'error'
                self.comment = 'invalid server answer'

    def __str__(self):
        return 'Result : {}\nInfo   : {}'.format(self.code, self.comment)

    def make_response(self):
        return jsonify({'code': self.code, 'comment': self.comment})
