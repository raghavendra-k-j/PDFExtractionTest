import os
import fitz  # PyMuPDF
import pytesseract
import uuid
import shutil
import time
import json
from PIL import Image

TASKS_DIR = "tasks"
os.makedirs(TASKS_DIR, exist_ok=True)

# Generate unique task directory
def create_task_folder(input_pdf_path):
    task_id = str(uuid.uuid4())
    task_path = os.path.join(TASKS_DIR, task_id)
    os.makedirs(task_path, exist_ok=True)

    # Copy input PDF into task folder
    task_pdf_path = os.path.join(task_path, "Book.pdf")
    shutil.copy2(input_pdf_path, task_pdf_path)

    print(f"📁 Task created: {task_path}")
    return task_path, task_pdf_path

# Step 1: Extract raw text
def extract_text(pdf_path, output_txt_path):
    pdf = fitz.open(pdf_path)
    all_text = [page.get_text() for page in pdf]
    pdf.close()
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    print(f"✅ Text extracted to {output_txt_path}")

# Step 2: Extract images and build JSON map
def extract_images(pdf_path, images_folder, json_path):
    os.makedirs(images_folder, exist_ok=True)
    pdf = fitz.open(pdf_path)
    image_meta_list = []
    img_counter = 0

    for page_num, page in enumerate(pdf):
        images = page.get_images(full=True)
        for img_index, img_info in enumerate(images):
            xref = img_info[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            img_uuid = str(uuid.uuid4())
            filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
            path = os.path.join(images_folder, filename)
            with open(path, "wb") as f:
                f.write(image_bytes)

            image_meta_list.append({
                "id": img_uuid,
                "filename": filename,
                "path": path
            })

            img_counter += 1

    pdf.close()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(image_meta_list, f, indent=4)

    print(f"✅ Extracted {img_counter} image(s) to {images_folder}")
    print(f"🗂️ Image metadata written to {json_path}")

# Step 3: Run OCR and append results with timings
def run_ocr(image_meta_list, ocr_output_path):
    total_elapsed = 0.0
    with open(ocr_output_path, "a", encoding="utf-8") as ocr_file:
        for idx, img in enumerate(image_meta_list, 1):
            print(f"[{idx}/{len(image_meta_list)}] 🖼️ Processing {img['filename']}...")
            start = time.time()
            try:
                text = pytesseract.image_to_string(Image.open(img["path"]))
                elapsed = time.time() - start
                total_elapsed += elapsed

                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                ms = int((elapsed - int(elapsed)) * 1000)

                ocr_file.write(f"\n--- OCR Result for {img['filename']} ---\n")
                ocr_file.write(f"UUID: {img['id']}\n")
                ocr_file.write(f"Time taken: {minutes}m {seconds}s ({ms}ms)\n\n")
                ocr_file.write(text + "\n")

                print(f"   ✅ Done in {minutes}m {seconds}s ({ms}ms)")
            except Exception as e:
                print(f"   ❌ Error processing {img['filename']}: {e}")

    total_min = int(total_elapsed // 60)
    total_sec = int(total_elapsed % 60)
    total_ms = int((total_elapsed - int(total_elapsed)) * 1000)
    print(f"\n🕒 Total OCR time: {total_min}m {total_sec}s ({total_ms}ms)")

# 🚀 Full Pipeline
def process_pdf(input_pdf_path):
    task_path, task_pdf_path = create_task_folder(input_pdf_path)
    extract_text(task_pdf_path, os.path.join(task_path, "contents.txt"))
    images_folder = os.path.join(task_path, "images")
    json_path = os.path.join(task_path, "images.json")
    extract_images(task_pdf_path, images_folder, json_path)

    # Read image metadata and run OCR
    with open(json_path, "r", encoding="utf-8") as f:
        image_meta_list = json.load(f)
    run_ocr(image_meta_list, os.path.join(task_path, "ocr.txt"))

# 🟢 Entry point
if __name__ == "__main__":
    # 🔁 Replace this with your actual file path
    input_pdf = "Book.pdf"
    if os.path.exists(input_pdf):
        process_pdf(input_pdf)
    else:
        print("❌ Input PDF file not found.")
