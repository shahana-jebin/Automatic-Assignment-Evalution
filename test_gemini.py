from pathlib import Path

from evaluator.gemini_extractor import extract_text_from_pdf


pdf_path = Path("sample_handwritten.pdf")


with open(
    pdf_path,
    "rb"
) as file:

    class FakeUploadedFile:

        def __init__(self, file):
            self.file = file

        def seek(self, position):
            self.file.seek(position)

        def chunks(self):
            while True:
                chunk = self.file.read(8192)

                if not chunk:
                    break

                yield chunk


    uploaded_file = FakeUploadedFile(file)

    text = extract_text_from_pdf(
        uploaded_file
    )


print("\n")
print("==============================")
print("EXTRACTED TEXT")
print("==============================")
print(text)
