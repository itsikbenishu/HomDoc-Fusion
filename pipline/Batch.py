from Operation import Operation
class Batch(Operation):
    def __init__(self, operation):
        if not isinstance(operation, Operation):
            raise TypeError(f"operation must be an instance of Operation, got {type(operation).__name__}")
        self.context = operation.context
        self.operation = operation

    def run(self, input):
        data = input
        if not isinstance(data, list):
            raise TypeError("data at Batcg must be an list, got {type(data).__name__}")
        output = list()

        for elem in data:
            output.append(self.operation.run(elem))            

        return output

