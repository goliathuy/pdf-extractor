#!/usr/bin/env python3
"""
Command-line interface for PDF extractor.
"""

import argparse
import os
import sys
import json
from extract_pdf_content import main as extract_main, validate_pdf_file, PDFProcessingError

def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Advanced PDF Content Extractor with Intelligent Section Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_cli.py document.pdf                    # Process with default settings
  python pdf_cli.py document.pdf --parts 6          # Split into 6 equal parts
  python pdf_cli.py document.pdf --output ./results  # Custom output directory
  python pdf_cli.py document.pdf --no-images        # Skip image extraction
  python pdf_cli.py document.pdf --config my_config.json  # Use custom config
  python pdf_cli.py --test                          # Run unit tests
  python pdf_cli.py --batch batch_files.txt         # Process multiple files
  python pdf_cli.py --analyze document.pdf          # Analyze PDF structure only
        """
    )
    
    parser.add_argument('pdf_file', nargs='?', help='Path to the PDF file to process')
    parser.add_argument('--output', '-o', help='Output directory for processed files')
    parser.add_argument('--parts', '-p', type=int, help='Number of equal parts to split into')
    parser.add_argument('--no-images', action='store_true', help='Skip image extraction')
    parser.add_argument('--no-sections', action='store_true', help='Skip intelligent section splitting')
    parser.add_argument('--config', '-c', default='config.json', help='Path to configuration file')
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    parser.add_argument('--validate', '-v', action='store_true', help='Only validate the PDF file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    parser.add_argument('--memory-stats', action='store_true', help='Show memory usage statistics')
    parser.add_argument('--batch', help='Process multiple PDF files from a text file (one file path per line)')
    parser.add_argument('--analyze', action='store_true', help='Analyze PDF structure and metadata only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without actual processing')
    parser.add_argument('--format', choices=['text', 'json', 'xml'], default='text', help='Output format for extracted content')
    parser.add_argument('--threshold', type=int, help='White text color threshold (override config)')
    
    return parser.parse_args()

def run_tests():
    """Run unit tests."""
    import unittest
    import test_pdf_extractor
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_pdf_extractor)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def validate_only(pdf_file):
    """Only validate the PDF file."""
    try:
        validate_pdf_file(pdf_file)
        print(f"✅ PDF file '{pdf_file}' is valid and ready for processing.")
        return 0
    except PDFProcessingError as e:
        print(f"❌ PDF validation failed: {e}")
        return 1

def show_memory_stats():
    """Show current memory usage statistics."""
    try:
        from extract_pdf_content import optimize_memory_usage
        stats = optimize_memory_usage()
        
        print("Memory Usage Statistics:")
        print(f"  RSS (Resident Set Size): {stats['rss_mb']:.1f} MB")
        print(f"  VMS (Virtual Memory Size): {stats['vms_mb']:.1f} MB")
        print(f"  Memory Percentage: {stats['percent']:.1f}%")
        print(f"  Available Memory: {stats['available_mb']:.1f} MB")
        
    except ImportError:
        print("Memory monitoring requires 'psutil' package. Install with: pip install psutil")

def process_batch(batch_file, config, **kwargs):
    """Process multiple PDF files from a batch file."""
    if not os.path.exists(batch_file):
        print(f"❌ Batch file not found: {batch_file}")
        return 1
    
    try:
        with open(batch_file, 'r') as f:
            pdf_files = [line.strip() for line in f.readlines() if line.strip()]
        
        if not pdf_files:
            print("❌ No PDF files found in the batch file.")
            return 1
        
        print(f"Found {len(pdf_files)} PDF files in batch file.")
        
        success_count = 0
        failed_files = []
        
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file}")
            
            if not os.path.exists(pdf_file):
                print(f"  ❌ File not found: {pdf_file}")
                failed_files.append(pdf_file)
                continue
            
            try:
                result = extract_main(pdf_path=pdf_file, config=config, **kwargs)
                if result:
                    print(f"  ✅ Successfully processed: {pdf_file}")
                    success_count += 1
                else:
                    print(f"  ❌ Failed to process: {pdf_file}")
                    failed_files.append(pdf_file)
            except Exception as e:
                print(f"  ❌ Error processing {pdf_file}: {e}")
                failed_files.append(pdf_file)
        
        print(f"\nBatch processing complete:")
        print(f"  ✅ Successfully processed: {success_count}/{len(pdf_files)} files")
        
        if failed_files:
            print(f"  ❌ Failed to process {len(failed_files)} files:")
            for failed in failed_files:
                print(f"    - {failed}")
        
        return 0 if not failed_files else 1
    
    except Exception as e:
        print(f"❌ Error processing batch: {e}")
        return 1

def analyze_pdf_structure(pdf_path):
    """Analyze the structure of a PDF file without extracting content."""
    from extract_pdf_content import validate_pdf_file
    
    try:
        validate_pdf_file(pdf_path)
        
        import fitz
        doc = fitz.open(pdf_path)
        
        # Get basic PDF info
        page_count = len(doc)
        metadata = doc.metadata
        toc = doc.get_toc()
        
        # Sample some pages to check for images and text
        sample_pages = min(5, page_count)
        pages_with_images = 0
        pages_with_text = 0
        text_sample = ""
        
        for i in range(sample_pages):
            page = doc[i]
            
            # Check for images
            if page.get_images():
                pages_with_images += 1
            
            # Check for text
            text = page.get_text()
            if text.strip():
                pages_with_text += 1
                if len(text_sample) < 500:  # Get a small sample
                    text_sample += text[:100] + "...\n"
        
        # Estimate content distribution
        if sample_pages > 0:
            image_percentage = (pages_with_images / sample_pages) * 100
            text_percentage = (pages_with_text / sample_pages) * 100
        else:
            image_percentage = text_percentage = 0
        
        # Print analysis
        print("\n📊 PDF Structure Analysis")
        print("=" * 50)
        print(f"📄 File: {pdf_path}")
        print(f"📚 Pages: {page_count}")
        
        if metadata:
            print("\n📝 Metadata:")
            for key, value in metadata.items():
                if value:
                    print(f"  {key}: {value}")
        
        if toc:
            print(f"\n📑 Table of Contents: {len(toc)} entries")
            for entry in toc[:5]:  # Show first 5 entries
                print(f"  {'  ' * (entry[0]-1)}- {entry[1]} (Page {entry[2]})")
            if len(toc) > 5:
                print(f"  ... and {len(toc) - 5} more entries")
        else:
            print("\n❌ No Table of Contents found")
        
        print("\n📊 Content Analysis:")
        print(f"  Estimated images coverage: {image_percentage:.1f}%")
        print(f"  Estimated text coverage: {text_percentage:.1f}%")
        
        print("\n📄 Text Sample:")
        if text_sample:
            lines = text_sample.split('\n')
            for line in lines[:3]:
                if line.strip():
                    print(f"  {line}")
        else:
            print("  No text found in sample pages")
        
        # Check if text might be white or hidden
        has_potential_hidden_text = False
        if sample_pages > 0:
            for i in range(min(3, sample_pages)):
                page = doc[i]
                dict_text = page.get_text("dict")
                
                for block in dict_text.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                color = span.get("color", 0)
                                if color > 15000000:  # Possible white text
                                    has_potential_hidden_text = True
                                    break
        
        if has_potential_hidden_text:
            print("\n⚠️ Warning: Document may contain hidden (white) text!")
        
        print("\n🔍 Processing Recommendations:")
        
        if not toc and page_count > 20:
            print("  • Consider using custom section detection (no TOC found)")
        
        if image_percentage > 70:
            print("  • Document is image-heavy - OCR may be needed for text")
        
        if has_potential_hidden_text:
            print("  • Enable white text filtering when extracting text")
        
        if page_count > 100:
            print("  • Consider splitting into smaller parts for processing")
        
        doc.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

def main():
    """Main CLI function."""
    args = parse_arguments()
    
    # Handle special commands
    if args.test:
        return run_tests()
    
    if args.memory_stats:
        show_memory_stats()
        if not args.pdf_file:
            return 0
    
    # Validate required arguments
    if not args.pdf_file:
        print("Error: PDF file argument is required (unless using --test)")
        return 1
    
    if not os.path.exists(args.pdf_file):
        print(f"Error: PDF file '{args.pdf_file}' not found.")
        return 1
    
    # Handle validation-only mode
    if args.validate:
        return validate_only(args.pdf_file)
    
    # Load configuration
    config = load_config(args.config)
      # Configure logging based on quiet flag
    if args.quiet:
        import logging
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Build kwargs for the main function
        kwargs = {
            'skip_images': args.no_images,
            'skip_sections': args.no_sections,
        }
        
        if args.output:
            kwargs['output_dir'] = args.output
        
        if args.parts:
            kwargs['num_parts'] = args.parts
        
        print(f"Processing PDF: {args.pdf_file}")
        print(f"Configuration: {args.config}")
        
        if args.output:
            print(f"Output directory: {args.output}")
        
        if args.parts:
            print(f"Equal parts: {args.parts}")
        
        if args.no_images:
            print("Image extraction: DISABLED")
        
        if args.no_sections:
            print("Section splitting: DISABLED")
        
        # Call the main function with parameters
        result = extract_main(pdf_path=args.pdf_file, config=config, **kwargs)
        
        # Display results if available
        if result:
            print(f"\n📊 Processing Results:")
            print(f"   📁 Output Directory: {result.get('output_dir', 'N/A')}")
            print(f"   🖼️  Images Extracted: {result.get('image_count', 0)}")
            print(f"   📝 Text Length: {result.get('text_length', 0):,} characters")
            print(f"   📄 Sections Created: {result.get('section_count', 0)}")
        
        print("\n✅ PDF processing completed successfully!")
        return 0
        
    except PDFProcessingError as e:
        print(f"❌ PDF processing failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
