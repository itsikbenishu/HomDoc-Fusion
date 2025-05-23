
class Operation:
    def __init__(self):
        self.context = dict()


    def run(self, input):
        data = input
        output = data
        return output

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context

