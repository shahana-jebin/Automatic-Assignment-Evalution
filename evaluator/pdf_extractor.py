import pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io


def preprocess_image(image):

    # Convert to grayscale
    image = image.convert("L")

    # Improve contrast
    image = ImageEnhance.Contrast(image).enhance(2)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    return image


def extract_text_from_pdf(pdf_file):

    pdf_file.seek(0)

    document = pymupdf.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in document:

        # Try normal PDF text extraction
        page_text = page.get_text().strip()

        if page_text:
            text += page_text + "\n"

        else:

            # Convert page to high-resolution image
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(3, 3)
            )

            image_bytes = pixmap.tobytes("png")

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            # Image preprocessing
            image = preprocess_image(image)

            # OCR
            ocr_text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            )

            text += ocr_text + "\n"

    document.close()

    return text.strip()