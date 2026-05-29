import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.face_helper as face_helper

class TestFaceHelper(unittest.TestCase):
    """
    Unit test suite validating OpenCV frame decoding and face-matching logic.
    """
    
    def test_decode_invalid_base64(self):
        """
        Tests that invalid base64 image strings gracefully return None instead of raising exceptions.
        """
        img = face_helper.decode_base64_image("invalid_base64_string")
        self.assertIsNone(img)
        
    def test_process_empty_frame(self):
        """
        Tests that empty image frames return empty matched lists.
        """
        faces = face_helper.process_frame(None, [])
        self.assertEqual(len(faces), 0)

if __name__ == '__main__':
    unittest.main()
