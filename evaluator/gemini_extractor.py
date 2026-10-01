import os
import time
import tempfile

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Current Flash models
MODELS_TO_TRY = [

    "gemini-3.8-flash",

    "gemini-3.7-flash",

    "gemini-3.6-flash",

]


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(pdf_file):

    """
    Send the original PDF to Gemini and
    extract the student's handwritten answer.
    """

    pdf_file.seek(0)


    # --------------------------------------------------------
    # Save Django uploaded PDF temporarily
    # --------------------------------------------------------

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ) as temp_file:

        for chunk in pdf_file.chunks():

            temp_file.write(chunk)

        temp_path = temp_file.name


    try:

        # ----------------------------------------------------
        # Upload PDF to Gemini
        # ----------------------------------------------------

        print(
            "Uploading PDF to Gemini..."
        )

        uploaded_file = client.files.upload(
            file=temp_path
        )


        print(
            "PDF uploaded successfully."
        )


        # ----------------------------------------------------
        # Transcription prompt
        # ----------------------------------------------------

        prompt = """

You are an expert handwritten-document
transcription system.

The attached PDF contains a student's
handwritten assignment.

Your task is to transcribe the student's
answer as accurately as possible.

IMPORTANT RULES:

1. Read every page of the PDF.

2. Transcribe the student's handwriting
   as accurately as possible.

3. Preserve the student's original meaning.

4. DO NOT summarize the answer.

5. DO NOT improve grammar.

6. DO NOT rewrite sentences.

7. DO NOT add information.

8. DO NOT remove meaningful information.

9. Preserve headings.

10. Preserve question numbers.

11. Preserve answer numbering.

12. Preserve paragraphs.

13. Preserve equations and symbols.

14. Preserve technical terms.

15. If a word is genuinely impossible
    to read, write [ILLEGIBLE].

16. Do not guess unreadable words.

17. Ignore decorative elements that are
    not part of the student's answer.

Return ONLY the transcribed assignment.

Do not evaluate the answer.

Do not summarize the answer.

Do not explain your transcription.

"""


        # ----------------------------------------------------
        # Try Gemini models
        # ----------------------------------------------------

        response = None

        last_error = None


        for model_name in MODELS_TO_TRY:

            for attempt in range(3):

                try:

                    print(
                        f"Using {model_name} "
                        f"(attempt {attempt + 1}/3)"
                    )


                    response = client.models.generate_content(

                        model=model_name,

                        contents=[
                            prompt,
                            uploaded_file
                        ]

                    )


                    print(
                        f"Success with {model_name}"
                    )


                    break


                except Exception as e:

                    last_error = e

                    print(
                        f"Gemini request failed: {e}"
                    )


                    if attempt < 2:

                        wait_time = 2 ** attempt


                        print(
                            f"Waiting "
                            f"{wait_time} seconds..."
                        )


                        time.sleep(
                            wait_time
                        )


            if response is not None:

                break


        # ----------------------------------------------------
        # All models failed
        # ----------------------------------------------------

        if response is None:

            raise RuntimeError(
                "Gemini failed after multiple "
                "attempts and models."
            ) from last_error


        # ----------------------------------------------------
        # Extract response text
        # ----------------------------------------------------

        extracted_text = (
            response.text
            or ""
        )


        return extracted_text.strip()


    finally:

        # ----------------------------------------------------
        # Delete temporary PDF
        # ----------------------------------------------------

        try:

            os.remove(
                temp_path
            )

        except OSError:

            pass
