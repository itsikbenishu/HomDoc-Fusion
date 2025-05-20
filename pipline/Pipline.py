from Operation import Operation

class Pipeline:
    def __init__(self):
        self.operations = list()
        
    def add_oper(self, operation):
        if not isinstance(operation, Operation):
            raise TypeError(f"operation must be an instance of Operation, got {type(operation).__name__}")
        
        self.operations.append(operation)
    
    def init_context(self, context):
        if not isinstance(context, dict):
            raise TypeError(f"context must be a dictionary, got {type(context).__name__}")
        if len(self.operations) == 0:
            raise TypeError(f"not operations at pipeline")
        
        self.operations[0].set_context(context)
        
    def run(self, input):
        prev_context = dict()
        cur = input
        
        for operation in self.operations:
            operation.set_context(prev_context)
            cur = operation.run(cur)
            prev_context = operation.get_context()

