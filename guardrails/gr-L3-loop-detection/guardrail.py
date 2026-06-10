"""gr-L3-loop-detection: Detect and kill infinite loops and runaway execution"""
import time


class L3LoopDetectionGuardrail:
    name = "gr-L3-loop-detection"
    layer = "L3"
    triggers_on = ["runtime"]

    def __init__(self, max_iterations=50, timeout_seconds=300, max_recursion_depth=10):
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.max_recursion_depth = max_recursion_depth
        self.iteration_count = 0
        self.start_time = None

    def start(self):
        self.iteration_count = 0
        self.start_time = time.time()

    def check_iteration(self, depth=0) -> dict:
        self.iteration_count += 1
        violations = []

        if self.iteration_count > self.max_iterations:
            violations.append({"rule": "max-iterations", "detail": f"Exceeded {self.max_iterations} iterations", "action": "block", "severity": "critical"})

        if self.start_time and (time.time() - self.start_time) > self.timeout_seconds:
            violations.append({"rule": "timeout", "detail": f"Exceeded {self.timeout_seconds}s timeout", "action": "block", "severity": "critical"})

        if depth > self.max_recursion_depth:
            violations.append({"rule": "recursion-depth", "detail": f"Exceeded max recursion depth {self.max_recursion_depth}", "action": "block", "severity": "high"})

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        return self.check_iteration()
