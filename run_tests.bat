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
echo 4. Processing PDF with default settings (exact output directory)...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output test_output/with_images --parts 3 --no-timestamps
if %errorlevel% neq 0 (
    echo ❌ PDF processing failed!
    exit /b 1
)

echo.
echo 5. Processing PDF without images (exact output directory)...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output test_output/no_images --no-images --no-timestamps
if %errorlevel% neq 0 (
    echo ❌ PDF processing without images failed!
    exit /b 1
)

echo.
echo 6. Testing new timestamped subdirectory feature...
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output test_output/timestamped --no-images
if %errorlevel% neq 0 (
    echo ❌ Timestamped processing failed!
    exit /b 1
)

echo.
echo ✅ All tests completed successfully!
echo Check the 'test_output/' directory for organized test results.
echo   - test_output/with_images/ - Full processing with images (exact directory)
echo   - test_output/no_images/ - Processing without embedded images (exact directory)
echo   - test_output/timestamped/extraction_YYYYMMDD_HHMMSS/ - New timestamped subdirectory feature
echo.
echo Timestamped directory feature is now the DEFAULT behavior.
echo Use --no-timestamps to create exact output directories when needed.
pause
