import fitz  # PyMuPDF
import os
import json
import datetime
# import openai

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
        page_text = ''
        for block in page_dict.get("blocks", []):
            if block.get("type", 1) != 0:
                continue  # skip non-text blocks
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    color = span.get("color", 0)
                    if isinstance(color, int) and color >= 0xF0F0F0:
                        continue  # skip white/nearly white text
                    page_text += span.get("text", "")
                page_text += "\n"
        # Add image references for this page
        images = page.get_images(full=True)
        if images:
            for img_index, img in enumerate(images):
                img_ext = doc.extract_image(img[0])['ext']
                img_filename = f'image_p{i+1}_{img_index + 1}.{img_ext}'
                page_text += f'[[IMAGE: {img_filename}]]\n'
        # Add page separator and number
        text += f'\n--- PAGE {i+1} ---\n' + page_text.strip() + '\n'
    print(f"[INFO] Finished extracting text from {num_pages} pages (filtered for visible text, with page numbers and image refs).")
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

# def validate_text_chunk(chunk):
#     prompt = (
#         "Is the following text well-formed and coherent? "
#         "If not, suggest corrections or flag issues:\n\n" + chunk
#     )
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=500
#     )
#     return response['choices'][0]['message']['content']
# 
# # Split your extracted text and process each chunk

def save_json(text, images_info, out_path):
    print(f"[INFO] Saving combined text and image info to {out_path} ...")
    data = {
        'text': text,
        'images': images_info
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] JSON output saved successfully.")

def split_pdf_by_sections(pdf_path, output_dir):
    """
    Split the PDF into smaller PDFs by sections, using the Table of Contents (TOC) if available.
    Each section will be saved as a new PDF in output_dir, named by section title or number.
    """
    import re
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    toc = doc.get_toc(simple=True)  # [(level, title, page number), ...]
    if not toc:
        print("[WARN] No Table of Contents found in PDF. Cannot split by sections.")
        return []
    section_files = []
    for idx, (level, title, start_page) in enumerate(toc):
        # Only split at top-level sections (level==1)
        if level != 1:
            continue
        # Determine end page: next section's start - 1, or end of doc
        end_page = doc.page_count - 1
        for next_idx in range(idx+1, len(toc)):
            if toc[next_idx][0] == 1:
                end_page = toc[next_idx][2] - 2  # 0-based, previous page
                break
        # Clean title for filename
        safe_title = re.sub(r'[^\w\-]+', '_', title.strip())[:40]
        out_path = os.path.join(output_dir, f'section_{idx+1}_{safe_title}.pdf')
        section_doc = fitz.open()
        for p in range(start_page-1, end_page+1):
            section_doc.insert_pdf(doc, from_page=p, to_page=p)
        section_doc.save(out_path)
        section_files.append(out_path)
        print(f"[INFO] Saved section '{title}' (pages {start_page}-{end_page+1}) to {out_path}")
    return section_files

def find_section_starts(extracted_text, toc_entries):
    import re
    section_starts = []
    for entry in toc_entries:
        entry_norm = re.sub(r'[^A-Za-z0-9]+', '', entry).lower()
        found = False
        for match in re.finditer(r'--- PAGE (\d+) ---\n(.{0,300})', extracted_text, re.DOTALL):
            page_num = int(match.group(1))
            page_text = match.group(2)
            page_text_norm = re.sub(r'[^A-Za-z0-9]+', '', page_text).lower()
            # Allow partial match (at least 60% of entry_norm in page_text_norm)
            if entry_norm and len(entry_norm) > 5:
                match_len = sum(1 for c in entry_norm if c in page_text_norm)
                if match_len / len(entry_norm) > 0.6:
                    section_starts.append((entry, page_num))
                    found = True
                    break
            if entry_norm in page_text_norm:
                section_starts.append((entry, page_num))
                found = True
                break
        if not found:
            print(f"[WARN] Section '{entry}' not found in extracted text.")
    return section_starts

def split_pdf_by_section_titles(pdf_path, extracted_text_path, toc_entries, output_dir=None):
    """
    Split the PDF into smaller PDFs by searching for section titles in the extracted text.
    Each section will be saved as a new PDF in a timestamped output_dir, named by section title or number.
    """
    import re
    if output_dir is None:
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('procssed_data', f'sections_{now}')
    os.makedirs(output_dir, exist_ok=True)
    with open(extracted_text_path, 'r', encoding='utf-8') as f:
        extracted_text = f.read()
    section_starts = find_section_starts(extracted_text, toc_entries)
    if not section_starts:
        print("[WARN] No section starts found by title matching.")
        return []
    doc = fitz.open(pdf_path)
    section_files = []
    for idx, (title, start_page) in enumerate(section_starts):
        # The end page is the page before the next section's start, or the last page of the document
        if idx + 1 < len(section_starts):
            end_page = section_starts[idx+1][1] - 1  # inclusive, 0-based
        else:
            end_page = doc.page_count  # inclusive, 0-based
        safe_title = re.sub(r'[^\w\-]+', '_', title.strip())[:40]
        out_path = os.path.join(output_dir, f'section_{idx+1}_{safe_title}.pdf')
        section_doc = fitz.open()
        for p in range(start_page-1, end_page):
            if 0 <= p < doc.page_count:
                section_doc.insert_pdf(doc, from_page=p, to_page=p)
        if section_doc.page_count == 0:
            print(f"[WARN] Skipping section '{title}' (pages {start_page}-{end_page}): no pages found.")
            continue
        section_doc.save(out_path)
        section_files.append(out_path)
        print(f"[INFO] Saved section '{title}' (pages {start_page}-{end_page}) to {out_path}")
    print(f"[INFO] All section PDFs saved in: {output_dir}")
    return section_files

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

    # Example TOC entries (replace with your actual TOC list)
    toc_entries = [
        "Message From Founders",
        "General Information",
        "Sales",
        "Business Location A",
        "Business Location B",
        "Miscellaneous",
        # ... add more as needed ...
    ]
    print("Splitting PDF by detected section titles...")
    split_pdf_by_section_titles(PDF_PATH, OUTPUT_TEXT_PATH, toc_entries)

if __name__ == '__main__':
    main()
