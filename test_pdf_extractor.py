#!/usr/bin/env python3
"""
Unit tests for PDF extractor functionality.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from extract_pdf_content import (
    validate_pdf_file, 
    PDFProcessingError,
    parse_toc_structure,
    fuzzy_match_section_titles,
    ProgressIndicator
)

class TestPDFExtractor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_pdf_file_not_found(self):
        """Test validation with non-existent file."""
        with self.assertRaises(PDFProcessingError) as context:
            validate_pdf_file("nonexistent.pdf")
        self.assertIn("PDF file not found", str(context.exception))
    
    def test_validate_pdf_file_wrong_extension(self):
        """Test validation with wrong file extension."""
        # Create a temporary txt file
        txt_file = os.path.join(self.temp_dir, "document.txt")
        with open(txt_file, 'w') as f:
            f.write("This is not a PDF")
        
        with self.assertRaises(PDFProcessingError) as context:
            validate_pdf_file(txt_file)
        self.assertIn("File is not a PDF", str(context.exception))
    
    def test_parse_toc_structure(self):
        """Test TOC structure parsing."""
        sample_text = "Sample PDF text content"
        toc_sections = parse_toc_structure(sample_text)
        
        # Check if we get the expected sections
        self.assertIsInstance(toc_sections, list)
        self.assertGreater(len(toc_sections), 0)
        
        # Check structure of first section
        first_section = toc_sections[0]
        self.assertIn("title", first_section)
        self.assertIn("start_page", first_section)
        self.assertIn("end_page", first_section)
        self.assertEqual(first_section["title"], "Message From Founders")
        self.assertEqual(first_section["start_page"], 3)
    
    def test_fuzzy_match_section_titles(self):
        """Test fuzzy matching of section titles."""
        # Sample text with page markers
        sample_text = """
        --- PAGE 3 ---
        Message From Our Founders
        This is the content of the message section.
        
        --- PAGE 5 ---
        General Information Section
        This contains general information.
        """
        
        toc_sections = [
            {"title": "Message From Founders", "start_page": 3, "end_page": 4},
            {"title": "General Information", "start_page": 5, "end_page": 31}
        ]
        
        refined_sections = fuzzy_match_section_titles(sample_text, toc_sections)
        
        self.assertEqual(len(refined_sections), 2)
        
        # Check that confidence scores are calculated
        for section in refined_sections:
            self.assertIn("match_confidence", section)
            self.assertIn("detected_page", section)
            # Confidence should be a number (int or float)
            self.assertIsInstance(section["match_confidence"], (int, float))
    
    def test_progress_indicator(self):
        """Test progress indicator functionality."""
        progress = ProgressIndicator(10, "Testing")
        
        # Test initialization
        self.assertEqual(progress.total_items, 10)
        self.assertEqual(progress.current_item, 0)
        self.assertEqual(progress.description, "Testing")
        
        # Test update
        progress.update(5)
        self.assertEqual(progress.current_item, 5)
        
        # Test completion
        progress.update(5)
        self.assertEqual(progress.current_item, 10)

class TestSectionOverlapValidation(unittest.TestCase):
    """Test section overlap validation functionality."""
    
    def test_validate_no_overlaps(self):
        """Test validation when sections don't overlap."""
        sections = [
            {"title": "Section 1", "start_page": 1, "end_page": 10},
            {"title": "Section 2", "start_page": 11, "end_page": 20},
            {"title": "Section 3", "start_page": 21, "end_page": 30}
        ]
        
        overlaps = validate_section_overlaps(sections)
        self.assertEqual(len(overlaps), 0)
    
    def test_validate_with_overlaps(self):
        """Test validation when sections overlap."""
        sections = [
            {"title": "Section 1", "start_page": 1, "end_page": 15},
            {"title": "Section 2", "start_page": 10, "end_page": 25},
            {"title": "Section 3", "start_page": 20, "end_page": 30}
        ]
        
        overlaps = validate_section_overlaps(sections)
        self.assertGreater(len(overlaps), 0)
        
        # Check that overlap details are provided
        overlap = overlaps[0]
        self.assertIn("section1", overlap)
        self.assertIn("section2", overlap)
        self.assertIn("overlap_pages", overlap)

def validate_section_overlaps(sections):
    """
    Validate that sections don't overlap inappropriately.
    
    Args:
        sections: List of section dictionaries with start_page and end_page
        
    Returns:
        List of overlap issues found
    """
    overlaps = []
    
    for i, section1 in enumerate(sections):
        for j, section2 in enumerate(sections[i+1:], i+1):
            # Check if sections overlap
            if (section1["start_page"] <= section2["end_page"] and 
                section2["start_page"] <= section1["end_page"]):
                
                overlap_start = max(section1["start_page"], section2["start_page"])
                overlap_end = min(section1["end_page"], section2["end_page"])
                
                overlaps.append({
                    "section1": section1["title"],
                    "section2": section2["title"],
                    "overlap_pages": f"{overlap_start}-{overlap_end}",
                    "overlap_size": overlap_end - overlap_start + 1
                })
    
    return overlaps

class TestMemoryOptimization(unittest.TestCase):
    """Test memory optimization features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('fitz.open')
    def test_document_cleanup(self, mock_fitz_open):
        """Test that PDF documents are properly closed."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1  # Mock document with 1 page
        mock_fitz_open.return_value = mock_doc
        
        # Import here to avoid issues with mocking
        from extract_pdf_content import validate_pdf_file
        
        # Create a temporary PDF file for testing
        test_pdf = os.path.join(self.temp_dir, "test.pdf")
        with open(test_pdf, 'w') as f:
            f.write("dummy pdf content")
        
        # This should properly close the document
        try:
            validate_pdf_file(test_pdf)
        except Exception:
            pass  # We expect some errors in test environment
        
        # Verify close was called
        mock_doc.close.assert_called()

if __name__ == '__main__':
    # Add the validation function to the main module for testing
    import extract_pdf_content
    extract_pdf_content.validate_section_overlaps = validate_section_overlaps
    
    # Run tests
    unittest.main(verbosity=2)
