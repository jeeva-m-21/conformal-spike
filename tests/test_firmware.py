"""
Unit tests for bare-metal C microcontroller firmware.
Executes 'make firmware' and asserts ASIL-D WCET (<= 100 us), FPR (<= 1.0%), and TPR (>= 90.0%).
"""

import unittest
import subprocess
import re
import os


class TestFirmware(unittest.TestCase):
    def test_firmware_compilation_and_execution(self):
        """
        Execute 'make firmware' host test harness and assert:
          - Returncode is 0.
          - WCET <= 100 us (ISO 26262 ASIL-D compliance).
          - FPR <= 1.0% (Automotive false-alarm rate budget).
          - TPR >= 90.0% (Intrusion detection performance).
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        proc = subprocess.run(
            ["make", "firmware"],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        self.assertEqual(
            proc.returncode, 0,
            f"'make firmware' failed with code {proc.returncode}:\n{proc.stderr}"
        )

        output = proc.stdout
        self.assertIn("Meets <= 100 us ASIL-D : YES (PASSED)", output)

        # Parse WCET
        wcet_match = re.search(r"Worst-Case Exec \(WCET\)\s*:\s*([\d\.]+)\s*us", output)
        self.assertIsNotNone(wcet_match, f"Could not find WCET in firmware output:\n{output}")
        wcet = float(wcet_match.group(1))
        self.assertLessEqual(wcet, 100.0, f"Firmware WCET ({wcet:.2f} us) exceeds 100 us ASIL-D budget!")

        # Parse FPR (ASIL-D target budget <= 1.50%)
        fpr_match = re.search(r"FPR\s*=\s*([\d\.]+)%", output)
        self.assertIsNotNone(fpr_match, f"Could not find FPR in firmware output:\n{output}")
        fpr = float(fpr_match.group(1))
        self.assertLessEqual(fpr, 1.5, f"Firmware FPR ({fpr:.2f}%) exceeds 1.5% threshold!")

        # Parse TPR
        tpr_match = re.search(r"TPR\s*=\s*([\d\.]+)%", output)
        self.assertIsNotNone(tpr_match, f"Could not find TPR in firmware output:\n{output}")
        tpr = float(tpr_match.group(1))
        self.assertGreaterEqual(tpr, 90.0, f"Firmware TPR ({tpr:.2f}%) below 90.0% requirement!")


if __name__ == '__main__':
    unittest.main()
