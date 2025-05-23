# PDF Processing System

A comprehensive PDF content extraction and intelligent splitting system that can process large PDF documents into manageable sections.

## Features

- **Text Extraction**: Extract text content with white text filtering
- **Image Extraction**: Extract and convert images (CMYK to RGB support)
- **Equal Parts Splitting**: Split PDFs into equal-sized parts
- **Intelligent Section Splitting**: Use Table of Contents structure for smart splitting
- **Fuzzy String Matching**: Intelligent section detection with confidence scoring
- **JSON Metadata**: Complete extraction metadata and processing logs

## Installation

### Requirements

```bash
pip install PyMuPDF
```

### Dependencies

- `PyMuPDF (fitz)`: PDF processing
- `os`, `json`, `datetime`, `math`, `re`: Built-in Python libraries
- `difflib`: Fuzzy string matching

## Usage

### Basic Usage

```python
python extract_pdf_content.py
```

The script will process the PDF file specified in the main function and create:

1. **Text extraction** - `extracted_text.txt`
2. **Image extraction** - `extracted_images/` folder
3. **JSON metadata** - `extracted_content.json`
4. **Equal parts split** - Multiple PDF files (e.g., 4 equal parts)
5. **Section-based split** - PDF files based on Table of Contents structure

### Output Structure

```
processed_data/
├── extraction_YYYYMMDD_HHMMSS/
│   ├── extracted_text.txt
│   ├── extracted_images/
│   │   ├── image_001.png
│   │   └── ...
│   ├── extracted_content.json
│   ├── section_info.json
│   ├── 01_Section_Name_pages_X-Y.pdf
│   └── ...
└── equal_parts_YYYYMMDD_HHMMSS/
    ├── part_1_pages_1-N.pdf
    └── ...
```

## Configuration

### Section Definitions

The system uses predefined section definitions that can be customized:

```python
predefined_sections = {
    "Message From Founders": {"start": 3, "end": 4},
    "General Information": {"start": 5, "end": 31},
    "Sales": {"start": 32, "end": 78},
    "Business Location A": {"start": 79, "end": 92},
    "Business Location B": {"start": 93, "end": 96},
    "Miscellaneous": {"start": 97, "end": 112}
}
```

### Fuzzy Matching Threshold

Adjust the confidence threshold for section matching:

```python
# In fuzzy_match_section_titles function
similarity = SequenceMatcher(None, section_title.lower(), extracted_title.lower()).ratio()
if similarity > 0.6:  # 60% minimum threshold
```

### Text Color Filtering

Adjust the white text filtering threshold:

```python
if color > 15000000:  # Adjust threshold as needed
    continue  # Skip white/very light text
```

## API Reference

### Core Functions

#### `extract_text(pdf_path)`
Extracts text from PDF with page separators and filters out white text.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- `str`: Extracted text with page markers

#### `extract_images(pdf_path, output_dir)`
Extracts all images from PDF and saves them with metadata.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save images

**Returns:**
- `list`: Image metadata with filenames and properties

#### `split_pdf_into_equal_parts(pdf_path, output_dir, num_parts=4)`
Splits PDF into equal-sized parts.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save split files
- `num_parts` (int): Number of parts to split into (default: 4)

**Returns:**
- `list`: Paths to created PDF parts

#### `split_pdf_by_sections(pdf_path, output_dir, toc_structure)`
Splits PDF based on Table of Contents structure.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save section files
- `toc_structure` (dict): Section definitions with page ranges

**Returns:**
- `list`: Paths to created section files

## Examples

### Processing a Custom PDF

```python
# Modify the main function
if __name__ == "__main__":
    pdf_path = "path/to/your/document.pdf"
    
    # Extract text
    text = extract_text(pdf_path)
    
    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"processed_data/extraction_{timestamp}"
    
    # Save text
    save_text(text, output_dir)
    
    # Extract images
    image_metadata = extract_images(pdf_path, output_dir)
    
    # Split into equal parts
    equal_parts_dir = f"processed_data/equal_parts_{timestamp}"
    split_pdf_into_equal_parts(pdf_path, equal_parts_dir, num_parts=4)
```

### Custom Section Definitions

```python
custom_sections = {
    "Introduction": {"start": 1, "end": 10},
    "Chapter 1": {"start": 11, "end": 25},
    "Chapter 2": {"start": 26, "end": 40},
    "Appendix": {"start": 41, "end": 50}
}

toc_structure = parse_toc_structure(pdf_path, custom_sections)
split_pdf_by_sections(pdf_path, output_dir, toc_structure)
```

## Troubleshooting

### Common Issues

1. **White Text Not Filtered**: Adjust the color threshold in `extract_text()`
2. **Section Matching Fails**: Lower the similarity threshold in fuzzy matching
3. **Memory Issues**: Process large PDFs in smaller chunks
4. **Image Conversion Errors**: Ensure proper CMYK to RGB conversion

### Error Handling

The system includes basic error handling for:
- File not found errors
- PDF corruption issues
- Image format conversion problems
- Directory creation failures

## Performance Notes

- **Large PDFs**: The system can handle large documents but may require significant memory
- **Image Processing**: CMYK to RGB conversion adds processing time
- **Fuzzy Matching**: String similarity calculation scales with content size

## Contributing

To contribute improvements:

1. Add error handling for edge cases
2. Implement progress bars for long operations
3. Add support for password-protected PDFs
4. Optimize memory usage for very large files
5. Add unit tests for core functions

## License

This project is for internal use and processing of business documents.
