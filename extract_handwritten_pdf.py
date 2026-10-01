import io
import re
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pymupdf  # PyMuPDF
from PIL import Image

# ----------------------------- CONFIG -----------------------------
RENDER_DPI = 200                 # Higher DPI helps handwriting OCR
MIN_NATIVE_TEXT_CHARS = 40       # If page has less than this, run OCR
USE_EASYOCR = False               # Set False to force Tesseract only
EASYOCR_LANGS = ["en"]
TESSERACT_LANG = "eng"
# ----------------------------- /CONFIG ----------------------------


# --------------------------- OCR ENGINES --------------------------
_easyocr_reader = None


def _get_easyocr_reader():
    """Lazy-load EasyOCR (slow first call)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        # gpu=False -> runs on CPU; set True if you have CUDA
        _easyocr_reader = easyocr.Reader(EASYOCR_LANGS, gpu=False, verbose=False)
    return _easyocr_reader


def ocr_with_easyocr(image: np.ndarray) -> str:
    """Run EasyOCR on a preprocessed BGR/gray numpy image."""
    reader = _get_easyocr_reader()
    # EasyOCR accepts numpy arrays (BGR or gray)
    results = reader.readtext(image, detail=0, paragraph=True)
    return "\n".join(results).strip()


def ocr_with_tesseract(image: np.ndarray) -> str:
    """Run Tesseract with handwriting-friendly settings."""
    import pytesseract

    # PSM 6: assume a single uniform block of text (good for assignments)
    # PSM 4: single column of text of variable sizes
    # PSM 11: sparse text (fallback)
    best = ""
    for psm in (6, 4, 11):
        try:
            txt = pytesseract.image_to_string(
                image,
                lang=TESSERACT_LANG,
                config=f"--oem 3 --psm {psm}",
            ).strip()
        except Exception:
            txt = ""
        if len(txt) > len(best):
            best = txt
    return best


def ocr_image(image: np.ndarray) -> str:
    """Try EasyOCR first, then Tesseract; return the longer result."""
    results = []

    if USE_EASYOCR:
        try:
            results.append(ocr_with_easyocr(image))
        except Exception as e:
            print(f"  [warn] EasyOCR failed: {e}", file=sys.stderr)

    try:
        results.append(ocr_with_tesseract(image))
    except Exception as e:
        print(f"  [warn] Tesseract failed: {e}", file=sys.stderr)

    if not results:
        return ""
    return max(results, key=len)


# ------------------------- IMAGE PREPROCESS -----------------------
def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    image: BGR or grayscale numpy array
    returns: binarized grayscale numpy array suitable for OCR
    """
    # 1. Convert to grayscale
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 2. Denoise (preserve strokes)
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # 3. Upscale small images (helps OCR on handwriting)
    h, w = gray.shape
    if max(h, w) < 1500:
        scale = 1500 / max(h, w)
        gray = cv2.resize(
            gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )

    # 4. Adaptive threshold (handles uneven lighting on scans)
    binary = cv2.adaptiveThreshold(
        gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    # 5. Deskew using the dominant text angle
    binary = _deskew(binary)

    # 6. Light morphological opening to remove speckles
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return binary


def _deskew(binary: np.ndarray) -> np.ndarray:
    """Estimate skew from text pixels and rotate to correct it."""
    # Invert so text = white
    inv = 255 - binary
    coords = np.column_stack(np.where(inv > 0))
    if coords.shape[0] < 50:
        return binary

    angle = cv2.minAreaRect(coords)[-1]
    # Normalize angle to [-45, 45]
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    if abs(angle) < 0.5:  # already straight
        return binary

    h, w = binary.shape
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(
        binary, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


# ---------------------------- PDF LOGIC ---------------------------
def _page_to_image(page: pymupdf.Page, dpi: int = RENDER_DPI) -> np.ndarray:
    """Render a PDF page to a BGR numpy image at the given DPI."""
    zoom = dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:                       # RGBA
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:                     # RGB
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # grayscale stays as-is
    return img


def _clean_native_text(text: str) -> str:
    """Tidy up native PDF text (collapse repeated whitespace etc.)."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a (possibly handwritten/scanned) PDF.
    Returns the full document text.
    """
    doc = pymupdf.open(pdf_path)
    output_chunks = []

    for page_num, page in enumerate(doc, start=1):
        print(f"[page {page_num}] processing...", file=sys.stderr)

        # --- 1. Try the embedded text layer first -----------------
        native = _clean_native_text(page.get_text("text"))

        # Pages with a real digital text layer have lots of chars.
        if len(native) >= MIN_NATIVE_TEXT_CHARS:
            output_chunks.append(
                f"===== Page {page_num} =====\n{native}\n"
            )
            continue

        # --- 2. Otherwise, OCR the rendered image -----------------
        img = _page_to_image(page, dpi=RENDER_DPI)
        processed = preprocess_for_ocr(img)
        ocr_text = ocr_image(processed)

        # If OCR gave us almost nothing, keep whatever native text existed.
        if len(ocr_text) < 5 and native:
            ocr_text = native

        output_chunks.append(
            f"===== Page {page_num} =====\n{ocr_text.strip()}\n"
        )

    doc.close()
    return "\n".join(output_chunks).strip()


# ------------------------------ CLI -------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_handwritten_pdf.py <input.pdf> [output.txt]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).is_file():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    text = extract_text_from_pdf(pdf_path)

    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
        Path(out_path).write_text(text, encoding="utf-8")
        print(f"Saved to {out_path}")
    else:
        print(text)


if __name__ == "__main__":
    main()
