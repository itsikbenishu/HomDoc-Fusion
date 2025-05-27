from Pipeline.Operation import Operation

class Batch(Operation):
    def __init__(self, operation):
        if not isinstance(operation, Operation):
            raise TypeError(f"operation must be an instance of Operation, got {type(operation).__name__}")
        super().__init__()  
        self._context = operation._context
        self._operation = operation

    def run(self, input):
        data = input
        if not isinstance(data, list):
            raise TypeError("data at Batcg must be an list, got {type(data).__name__}")
        output = list()

        for elem in data:
            output.append(self._operation.run(elem))            

        return output

