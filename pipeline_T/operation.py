
class Operation:
    def __init__(self):
        self._context = dict()


    def run(self, input=None):
        data = input
        output = data
        return output

    def get_context(self):
        return self._context

    def set_context(self, context):
        self._context = context

