@echo off
echo Testing PDF Extractor System
echo =============================

echo.
echo 1. Running unit tests...
python pdf_cli.py --test
if %errorlevel% neq 0 (
    echo ❌ Unit tests failed!
    exit /b 1
)

echo.
echo 2. Checking memory usage...
python pdf_cli.py --memory-stats

echo.
echo 3. Validating PDF file...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --validate
if %errorlevel% neq 0 (
    echo ❌ PDF validation failed!
    exit /b 1
)

echo.
echo 4. Processing PDF with default settings...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output test_output --parts 3
if %errorlevel% neq 0 (
    echo ❌ PDF processing failed!
    exit /b 1
)

echo.
echo 5. Processing PDF without images...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output test_output_no_images --no-images
if %errorlevel% neq 0 (
    echo ❌ PDF processing without images failed!
    exit /b 1
)

echo.
echo ✅ All tests completed successfully!
echo Check the 'test_output' and 'test_output_no_images' directories for results.
pause
