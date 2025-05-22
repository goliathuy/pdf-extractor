import fitz  # PyMuPDF
import os
import json

PDF_PATH = os.path.join('..', 'server-compare', 'samples/sample-pdf-with-images.pdf')
OUTPUT_TEXT_PATH = 'extracted_text.txt'
IMAGES_DIR = 'extracted_images'
OUTPUT_JSON_PATH = 'extracted_content.json'

def extract_text(pdf_path):
    print(f"[INFO] Opening PDF for text extraction: {pdf_path}")
    doc = fitz.open(pdf_path)
    text = ''
    num_pages = doc.page_count
    for i in range(num_pages):
        print(f"[INFO] Extracting text from page {i+1}/{num_pages}...")
        page = doc.load_page(i)
        try:
            page_dict = page.get_text("dict")
        except Exception as e:
            print(f"[WARN] Could not get text dict for page {i+1}: {e}")
            continue
        for block in page_dict.get("blocks", []):
            if block.get("type", 1) != 0:
                continue  # skip non-text blocks
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    color = span.get("color", 0)
                    # PyMuPDF color is int: 0=black, 16777215=white (0xFFFFFF)
                    # We'll filter out white or nearly white text
                    if isinstance(color, int) and color >= 0xF0F0F0:
                        continue  # skip white/nearly white text
                    text += span.get("text", "")
                text += "\n"
    print(f"[INFO] Finished extracting text from {num_pages} pages (filtered for visible text).")
    return text

def save_text(text, out_path):
    print(f"[INFO] Saving extracted text to {out_path} ...")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"[INFO] Text saved successfully.")

def extract_images(pdf_path, images_dir):
    print(f"[INFO] Creating images output directory: {images_dir}")
    os.makedirs(images_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    images_info = []
    img_count = 0
    num_pages = doc.page_count
    for page_num in range(num_pages):
        print(f"[INFO] Scanning page {page_num+1}/{num_pages} for images...")
        page = doc.load_page(page_num)
        images = page.get_images(full=True)
        if not images:
            print(f"[INFO] No images found on page {page_num+1}.")
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image['image']
            img_ext = base_image['ext']
            img_filename = f'image_p{page_num+1}_{img_index + 1}.{img_ext}'
            img_path = os.path.join(images_dir, img_filename)
            print(f"[INFO] Saving image {img_filename} from page {page_num+1} ...")
            with open(img_path, 'wb') as img_file:
                img_file.write(img_bytes)
            # Placeholder for image description
            description = f"Image extracted from page {page_num+1}, index {img_index + 1}. (Description placeholder)"
            images_info.append({
                'file': img_filename,
                'page': page_num+1,
                'index': img_index + 1,
                'description': description
            })
            img_count += 1
    print(f"[INFO] Total images extracted: {img_count}")
    return images_info

def save_json(text, images_info, out_path):
    print(f"[INFO] Saving combined text and image info to {out_path} ...")
    data = {
        'text': text,
        'images': images_info
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] JSON output saved successfully.")

def main():
    print(f"Extracting text from {PDF_PATH} ...")
    text = extract_text(PDF_PATH)
    save_text(text, OUTPUT_TEXT_PATH)
    print(f"Text saved to {OUTPUT_TEXT_PATH}")

    print(f"Extracting images from {PDF_PATH} ...")
    images_info = extract_images(PDF_PATH, IMAGES_DIR)
    print(f"Extracted {len(images_info)} images to {IMAGES_DIR}")

    print(f"Saving combined output to {OUTPUT_JSON_PATH} ...")
    save_json(text, images_info, OUTPUT_JSON_PATH)
    print("Done.")

if __name__ == '__main__':
    main()
