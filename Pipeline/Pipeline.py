from Operation import Operation

class Pipeline:
    def __init__(self):
        self._operations = list()
        
        
    def add_oper(self, operation):
        if not isinstance(operation, Operation):
            raise TypeError(f"operation must be an instance of Operation, got {type(operation).__name__}")
        
        self._operations.append(operation)
    
    def init_context(self, context):
        if not isinstance(context, dict):
            raise TypeError(f"context must be a dictionary, got {type(context).__name__}")
        if len(self._operations) == 0:
            raise TypeError(f"not operations at pipeline")
        
        self._operations[0].set_context(context)
        
    def run(self, input=None):
        prev_context = dict()
        cur = input
        
        for operation in self._operations:
            operation.set_context(prev_context)
            cur = operation.run(cur)
            prev_context = operation.get_context()

