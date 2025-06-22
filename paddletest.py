import os
import fitz  # PyMuPDF
import uuid
import shutil
import json
from paddleocr import PPStructureV3

# Constants
TASKS_DIR = "tasks"
os.makedirs(TASKS_DIR, exist_ok=True)

# Initialize PPStructureV3 (document parsing model)
structure_engine = PPStructureV3(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device="cpu",  # use "gpu" if available
    text_recognition_model_name="en_PP-OCRv4_mobile_rec"  # English OCR model
)

# Step 0: Create task folder and copy PDF
def create_task_folder(input_pdf_path):
    task_id = str(uuid.uuid4())
    task_path = os.path.join(TASKS_DIR, task_id)
    os.makedirs(task_path, exist_ok=True)

    task_pdf_path = os.path.join(task_path, "Book.pdf")
    shutil.copy2(input_pdf_path, task_pdf_path)

    print(f"📁 Task created: {task_path}")
    return task_path, task_pdf_path

# Step 1: Extract images from PDF (one per page)
def extract_page_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pdf = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        image_path = os.path.join(output_folder, f"page_{page_num+1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    pdf.close()
    print(f"✅ Saved {len(image_paths)} page image(s) to {output_folder}")
    return image_paths

# Step 2: Run structure analysis on images
def run_structure_analysis(images, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for idx, image_path in enumerate(images, 1):
        print(f"[{idx}/{len(images)}] 📄 Parsing {os.path.basename(image_path)}...")
        try:
            results = structure_engine.predict(image_path)
            output_json = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(image_path))[0]}.json")
            results[0].save_to_json(output_json)
            print(f"   ✅ Saved structured data to {output_json}")
        except Exception as e:
            print(f"   ❌ Error on {image_path}: {e}")

# Full pipeline
def process_pdf_with_structure(input_pdf_path):
    task_path, task_pdf_path = create_task_folder(input_pdf_path)

    images_folder = os.path.join(task_path, "images")
    structure_folder = os.path.join(task_path, "structure_json")

    image_paths = extract_page_images(task_pdf_path, images_folder)
    run_structure_analysis(image_paths, structure_folder)

    print("\n🎉 All pages parsed. Check the 'structure_json' folder inside your task.")

# Entry point
if __name__ == "__main__":
    input_pdf = "Book.pdf"
    if os.path.exists(input_pdf):
        process_pdf_with_structure(input_pdf)
    else:
        print("❌ Input PDF file not found.")
