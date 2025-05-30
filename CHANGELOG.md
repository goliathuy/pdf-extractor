# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-05-30

### Fixed
- **Hardcoded Business Sections Issue** - Fixed inappropriate business section detection in resume PDFs
- **Configuration-Based Section Detection** - Modified `parse_toc_structure` to read sections from config.json
- **Smart Section Processing** - Added logic to skip section splitting when no sections are defined in configuration
- **UTF-8 BOM Issues** - Resolved JSON configuration file encoding problems that caused processing errors
- **Test Function Compatibility** - Updated test suite to handle new function signatures

### Changed
- `parse_toc_structure` function now accepts optional config parameter
- Section splitting now dynamically reads from configuration instead of hardcoded values
- Enhanced logging to indicate when section splitting is skipped for non-business documents

## [1.0.0] - 2025-05-30

### Added
- **Comprehensive PDF Processing System** - Complete extraction and splitting functionality
- **Text Extraction** with white text filtering and color threshold configuration
- **Image Extraction** with CMYK to RGB conversion support
- **Page-to-Image Conversion** at 300 DPI with PNG format output
- **Intelligent Section Splitting** using TOC analysis and fuzzy string matching
- **Equal Parts Splitting** for dividing PDFs into equal-sized segments
- **Selective Extraction Modes** for high-performance single-function operations:
  - Text-only mode (50x faster - ~0.4 seconds vs ~20+ seconds)
  - Images-only mode (10-20x faster)
  - Page-images-only mode (3-5x faster)
- **Image-to-PDF Combination** for reconstructing PDFs from page images
- **CLI Interface** with comprehensive options and help system
- **JSON Metadata Export** with complete processing information
- **Progress Tracking** with Unicode console support for Windows
- **Memory Optimization** with proper cleanup and garbage collection
- **Configuration System** via JSON config file
- **Sample PDF Files** for testing and demonstration
- **Comprehensive Test Suite** with pytest integration
- **Timestamped Output Organization** for organized results

### Features
- **Performance Optimizations**:
  - Text-only: ~0.4 seconds (50x faster)
  - Images-only: ~1-2 seconds (10-20x faster) 
  - Page-images-only: ~4-6 seconds (3-5x faster)
  - Skip options for memory and time savings
- **Quality Assurance**:
  - 300 DPI image conversion verified with 112-page test document
  - Proper zero-padded naming convention (page_XXX.png)
  - Robust error handling and validation
  - Windows console encoding compatibility
- **Developer Experience**:
  - Comprehensive CLI help and examples
  - Detailed logging and processing summaries
  - Memory usage monitoring and optimization
  - Section overlap validation and reporting

### Technical Details
- **Supported Python Versions**: 3.8+
- **Key Dependencies**: PyMuPDF (fitz), Pillow, difflib, psutil
- **Image Formats**: PNG, JPEG support for page conversion
- **PDF Standards**: Full PyMuPDF compatibility
- **Operating Systems**: Windows, macOS, Linux
- **Performance**: Successfully tested with 112-page, 43MB PDF documents

### Installation Notes
- Package installation may show dependency conflict warnings with Streamlit and other packages
- These conflicts are harmless and do not affect PDF processing functionality
- The system works correctly with newer versions of Pillow (11.x) and packaging (25.x)
- Conflicts occur due to other packages having stricter version requirements
