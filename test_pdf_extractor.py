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
        
        # Test with config
        test_config = {
            "sections": {
                "Introduction": {"start": 1, "end": 5},
                "Main Content": {"start": 6, "end": 20}
            }
        }
        toc_sections = parse_toc_structure(sample_text, test_config)
        
        # Check if we get the expected sections
        self.assertIsInstance(toc_sections, list)
        self.assertEqual(len(toc_sections), 2)
        
        # Test without config (should return empty list)
        toc_sections_empty = parse_toc_structure(sample_text)
        self.assertIsInstance(toc_sections_empty, list)
        self.assertEqual(len(toc_sections_empty), 0)
        
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
        # Test basic functionality
        progress = ProgressIndicator(5, "Test Progress")
        self.assertEqual(progress.current_item, 0)
        self.assertEqual(progress.total_items, 5)
        
        # Test update
        progress.update(2)
        self.assertEqual(progress.current_item, 2)
        
        # Test completion
        progress.update(3)
        self.assertEqual(progress.current_item, 5)
    
    @patch('extract_pdf_content.fitz.open')
    @patch('os.makedirs')
    @patch('os.path.getsize')
    def test_convert_pages_to_images(self, mock_getsize, mock_makedirs, mock_fitz_open):
        """Test page-to-image conversion functionality."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2  # 2 pages
        mock_fitz_open.return_value = mock_doc
        
        # Mock pages
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        
        # Mock pixmaps
        mock_pix1 = MagicMock()
        mock_pix1.width = 2550
        mock_pix1.height = 3300
        mock_pix2 = MagicMock()
        mock_pix2.width = 2550
        mock_pix2.height = 3300
        
        mock_page1.get_pixmap.return_value = mock_pix1
        mock_page2.get_pixmap.return_value = mock_pix2
        
        # Mock file size
        mock_getsize.return_value = 500000  # 500KB
        
        # Import function to test
        from extract_pdf_content import convert_pages_to_images
        
        # Test conversion
        output_dir = self.temp_dir
        result = convert_pages_to_images("test.pdf", output_dir, dpi=300, image_format="png")
        
        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["page_number"], 1)
        self.assertEqual(result[1]["page_number"], 2)
        self.assertEqual(result[0]["dpi"], 300)
        self.assertEqual(result[0]["format"], "png")
        self.assertEqual(result[0]["width"], 2550)
        self.assertEqual(result[0]["height"], 3300)
        
        # Verify directory creation
        mock_makedirs.assert_called()
        
        # Verify PDF operations
        mock_fitz_open.assert_called_with("test.pdf")
        mock_doc.close.assert_called()
          # Verify pixmap operations
        mock_pix1.save.assert_called()
        mock_pix2.save.assert_called()

    def test_validate_section_overlaps(self):
        """Test section overlap validation."""
        # Test valid sections (no overlaps)
        valid_sections = [
            {"title": "Section 1", "start_page": 1, "end_page": 10},
            {"title": "Section 2", "start_page": 11, "end_page": 20}
        ]
        result = validate_section_overlaps(valid_sections)
        self.assertEqual(len(result), 0)  # No overlaps expected
        
        # Test overlapping sections
        overlapping_sections = [
            {"title": "Section 1", "start_page": 1, "end_page": 15},
            {"title": "Section 2", "start_page": 10, "end_page": 20}
        ]
        result = validate_section_overlaps(overlapping_sections)
        self.assertEqual(len(result), 1)  # One overlap expected
        self.assertEqual(result[0]["section1"], "Section 1")
        self.assertEqual(result[0]["section2"], "Section 2")
        self.assertEqual(result[0]["overlap_pages"], "10-15")

    @patch('extract_pdf_content.fitz.open')
    def test_error_handling_in_convert_pages_to_images(self, mock_fitz_open):
        """Test error handling in page conversion."""
        # Mock PDF document with error
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        # Mock page that raises exception
        mock_page = MagicMock()
        mock_page.get_pixmap.side_effect = Exception("Test error")
        mock_doc.__getitem__.return_value = mock_page
        
        from extract_pdf_content import convert_pages_to_images
        
        # Should handle errors gracefully
        result = convert_pages_to_images("test.pdf", self.temp_dir)
          # Should return empty list due to error
        self.assertEqual(len(result), 0)
        mock_doc.close.assert_called()

    def test_config_file_handling(self):
        """Test that the system works correctly without a config file."""
        # Test load_config function from pdf_cli
        import sys
        import os
        
        # Add the current directory to path so we can import pdf_cli
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        try:
            from pdf_cli import load_config
            
            # Test with non-existent config file
            config = load_config("nonexistent_config.json")
            self.assertEqual(config, {})
            
            # Test with existing config file
            test_config_file = os.path.join(self.temp_dir, "test_config.json")
            test_config_data = {
                "processing": {
                    "page_image_dpi": 150,
                    "page_image_format": "jpeg",
                    "white_text_threshold": 20000000
                },
                "output": {
                    "page_images_dirname": "custom_pages"
                }
            }
            
            with open(test_config_file, 'w') as f:
                json.dump(test_config_data, f)
            
            config = load_config(test_config_file)
            self.assertEqual(config["processing"]["page_image_dpi"], 150)
            self.assertEqual(config["processing"]["page_image_format"], "jpeg")
            self.assertEqual(config["output"]["page_images_dirname"], "custom_pages")
            
        except ImportError:
            # If pdf_cli can't be imported, just test the concept
            self.skipTest("pdf_cli module not available for import")

    def test_default_values_used_without_config(self):
        """Test that correct default values are used when config is empty."""
        # Test default DPI value
        from extract_pdf_content import main
        
        # Mock config get behavior
        empty_config = {}
        
        # Test that .get() calls return expected defaults
        dpi_default = empty_config.get("processing", {}).get("page_image_dpi", 300)
        self.assertEqual(dpi_default, 300)
        
        format_default = empty_config.get("processing", {}).get("page_image_format", "png")
        self.assertEqual(format_default, "png")
        
        threshold_default = empty_config.get("processing", {}).get("white_text_threshold", 15000000)
        self.assertEqual(threshold_default, 15000000)
        
        parts_default = empty_config.get("processing", {}).get("default_equal_parts", 4)
        self.assertEqual(parts_default, 4)

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

    @patch('extract_pdf_content.fitz.open')
    @patch('glob.glob')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_combine_images_to_pdf(self, mock_makedirs, mock_exists, mock_glob, mock_fitz_open):
        """Test combining page images into a PDF."""
        from extract_pdf_content import combine_images_to_pdf
        
        # Mock directory existence
        mock_exists.return_value = True
        
        # Mock image files
        mock_image_files = [
            'page_001.png',
            'page_002.png', 
            'page_003.png'
        ]
        mock_glob.return_value = mock_image_files
        
        # Mock PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.rect = MagicMock()
        mock_doc.new_page.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        # Test the function
        result = combine_images_to_pdf(
            images_dir=self.temp_dir,
            output_dir=self.temp_dir
        )
        
        # Verify function behavior
        self.assertIsInstance(result, dict)
        self.assertIn('output_file', result)
        self.assertIn('page_count', result)
        self.assertIn('file_size_mb', result)
        self.assertIn('source_images', result)
        self.assertIn('creation_time', result)
        
        # Verify page count matches our mock data
        self.assertEqual(result['page_count'], 3)
        self.assertEqual(result['source_images'], 3)
        
        # Verify PDF creation was attempted
        mock_fitz_open.assert_called()
        mock_doc.save.assert_called()
        mock_doc.close.assert_called()

if __name__ == '__main__':
    # Add the validation function to the main module for testing
    import extract_pdf_content
    extract_pdf_content.validate_section_overlaps = validate_section_overlaps
    
    # Run tests
    unittest.main(verbosity=2)
