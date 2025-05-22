import fitz  # PyMuPDF
import os
import json

PDF_PATH = os.path.join('..', 'server-compare', 'samples/sample-pdf-with-images.pdf')
OUTPUT_TEXT_PATH = 'extracted_text.txt'
IMAGES_DIR = 'extracted_images'
OUTPUT_JSON_PATH = 'extracted_content.json'

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def save_text(text, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)

def extract_images(pdf_path, images_dir):
    os.makedirs(images_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    images_info = []
    img_count = 0
    for page_num, page in enumerate(doc, start=1):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image['image']
            img_ext = base_image['ext']
            img_filename = f'image_p{page_num}_{img_index + 1}.{img_ext}'
            img_path = os.path.join(images_dir, img_filename)
            with open(img_path, 'wb') as img_file:
                img_file.write(img_bytes)
            # Placeholder for image description
            description = f"Image extracted from page {page_num}, index {img_index + 1}. (Description placeholder)"
            images_info.append({
                'file': img_filename,
                'page': page_num,
                'index': img_index + 1,
                'description': description
            })
            img_count += 1
    return images_info

def save_json(text, images_info, out_path):
    data = {
        'text': text,
        'images': images_info
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
