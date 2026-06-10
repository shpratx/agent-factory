"""Unit tests for gr-L1-output-schema-validator."""
import sys, unittest, importlib.util
from pathlib import Path

# Load module from kebab-case directory
_spec = importlib.util.spec_from_file_location("_mod", r"/Users/prateeksharma/Documents/Santander/agent-factory/guardrails/gr-L1-output-schema-validator/guardrail.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
L1OutputSchemaValidatorGuardrail = _mod.L1OutputSchemaValidatorGuardrail

# Also add shared to path
sys.path.insert(0, str(Path(__file__).parents[3]))

class TestL1OutputSchemaValidatorGuardrail(unittest.TestCase):
    def setUp(self):
        self.gr = L1OutputSchemaValidatorGuardrail()
    def test_valid_list_passes(self):
        self.assertTrue(self.gr.evaluate([{"title":"T"}])["passed"])
    def test_non_list_fails(self):
        self.assertFalse(self.gr.evaluate("not a list")["passed"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
