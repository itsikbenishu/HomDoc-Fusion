import logging
import time
from pipeline.operation import Operation

logger = logging.getLogger(__name__)

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
        timings = []

        for operation in self._operations:
            operation.set_context(prev_context)
            start = time.perf_counter()
            cur = operation.run(cur)
            duration = time.perf_counter() - start
            prev_context = operation.get_context()

            op_name = operation.__class__.__name__
            subphases = prev_context.get(f"{op_name}_subphases")
            timings.append((op_name, duration, subphases))

        self._log_summary(timings)

        output = cur

        return output

    def _log_summary(self, timings):
        total = sum(duration for _, duration, _ in timings)
        lines = ["Pipeline summary:"]
        for name, duration, subphases in timings:
            line = f"  {name}: {duration:.2f}s"
            if subphases:
                breakdown = ", ".join(f"{k}={v:.2f}s" for k, v in subphases.items())
                line += f" ({breakdown})"
            lines.append(line)
        lines.append(f"  Total: {total:.2f}s")
        logger.info("\n".join(lines))
