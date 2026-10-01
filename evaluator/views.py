# import json
# import os
# import uuid
# import csv

# from pathlib import Path

# from django.conf import settings
# from django.http import HttpResponse
# from django.shortcuts import render, redirect

# from .pdf_extractor import extract_text_from_pdf

# from .ai_model import (
#     extract_tokens,
#     split_paragraphs,
#     classify_section,
#     evaluate_introduction,
#     evaluate_explanation,
#     evaluate_conclusion,
#     evaluate_clarity,
#     evaluate_bibliography
# )


# # --------------------------------------------------
# # HOME
# # --------------------------------------------------

# def home(request):

#     return render(
#         request,
#         "home.html"
#     )


# # --------------------------------------------------
# # TEACHER RUBRIC
# # --------------------------------------------------

# def teacher_rubric(request):

#     if request.method == "POST":

#         topic = request.POST.get(
#             "topic",
#             ""
#         ).strip()

#         introduction = request.POST.get(
#             "introduction",
#             ""
#         ).strip()

#         conclusion = request.POST.get(
#             "conclusion",
#             ""
#         ).strip()

#         explanation_criteria = request.POST.getlist(
#             "explanation_criterion"
#         )

#         explanation_expected = request.POST.getlist(
#             "explanation_expected"
#         )

#         explanation_marks = request.POST.getlist(
#             "explanation_marks"
#         )

#         concepts = []

#         for i in range(
#             len(explanation_criteria)
#         ):

#             if (
#                 explanation_criteria[i].strip()
#                 and explanation_expected[i].strip()
#             ):

#                 concepts.append({
#                     "criterion":
#                         explanation_criteria[i].strip(),

#                     "expected":
#                         explanation_expected[i].strip(),

#                     "marks":
#                         float(explanation_marks[i])
#                 })

#         rubric = {

#             "topic": topic,

#             "Introduction": {
#                 "marks": 2,
#                 "expected": introduction
#             },

#             "Explanation of theory or idea": {
#                 "marks": 6,
#                 "concepts": concepts
#             },

#             "Overall clarity, style, structure and organization": {
#                 "marks": 3
#             },

#             "Clear Conclusion": {
#                 "marks": 2,
#                 "expected": conclusion
#             },

#             "Bibliography or Reference": {
#                 "marks": 2
#             }
#         }

#         rubric_id = str(uuid.uuid4())

#         rubric_path = (
#             Path(settings.MEDIA_ROOT)
#             / "rubrics"
#             / f"{rubric_id}.json"
#         )

#         with open(
#             rubric_path,
#             "w",
#             encoding="utf-8"
#         ) as file:

#             json.dump(
#                 rubric,
#                 file,
#                 indent=4
#             )

#         request.session["rubric_id"] = rubric_id

#         return redirect(
#             "student_upload"
#         )

#     return render(
#         request,
#         "teacher_rubric.html"
#     )


# # --------------------------------------------------
# # STUDENT UPLOAD
# # --------------------------------------------------

# def student_upload(request):

#     rubric_id = request.session.get(
#         "rubric_id"
#     )

#     if not rubric_id:

#         return redirect(
#             "teacher_rubric"
#         )

#     rubric_path = (
#         Path(settings.MEDIA_ROOT)
#         / "rubrics"
#         / f"{rubric_id}.json"
#     )

#     if not rubric_path.exists():

#         return redirect(
#             "teacher_rubric"
#         )

#     with open(
#         rubric_path,
#         "r",
#         encoding="utf-8"
#     ) as file:

#         rubric = json.load(file)

#     if request.method == "POST":

#         files = request.FILES.getlist(
#             "answer_sheets"
#         )

#         all_results = []

#         for pdf_file in files:

#             if not pdf_file.name.lower().endswith(
#                 ".pdf"
#             ):
#                 continue

#             text = extract_text_from_pdf(
#                 pdf_file
#             )

#             if not text:
#                 continue

#             # Tokens
#             tokens = extract_tokens(
#                 text
#             )

#             # Paragraph classification
#             paragraphs = split_paragraphs(
#                 text
#             )

#             section_analysis = []

#             for paragraph in paragraphs:

#                 section = classify_section(
#                     paragraph
#                 )

#                 section_analysis.append({
#                     "text": paragraph,
#                     "section":
#                         section["section"],
#                     "confidence":
#                         round(
#                             section["score"] * 100,
#                             2
#                         )
#                 })

#             # Introduction
#             introduction_result = (
#                 evaluate_introduction(
#                     text,
#                     rubric[
#                         "Introduction"
#                     ]["expected"]
#                 )
#             )

#             # Explanation
#             explanation_result = (
#                 evaluate_explanation(
#                     text,
#                     rubric[
#                         "Explanation of theory or idea"
#                     ]["concepts"]
#                 )
#             )

#             # Clarity
#             clarity_result = (
#                 evaluate_clarity(
#                     text
#                 )
#             )

#             # Conclusion
#             conclusion_result = (
#                 evaluate_conclusion(
#                     text,
#                     rubric[
#                         "Clear Conclusion"
#                     ]["expected"]
#                 )
#             )

#             # Bibliography
#             bibliography_result = (
#                 evaluate_bibliography(
#                     text
#                 )
#             )

#             total = (
#                 introduction_result["marks"]
#                 +
#                 explanation_result["marks"]
#                 +
#                 clarity_result["marks"]
#                 +
#                 conclusion_result["marks"]
#                 +
#                 bibliography_result["marks"]
#             )

#             total = min(
#                 15,
#                 round(total, 2)
#             )

#             percentage = round(
#                 (total / 15) * 100,
#                 2
#             )

#             result = {

#                 "student":
#                     Path(pdf_file.name).stem,

#                 "filename":
#                     pdf_file.name,

#                 "total":
#                     total,

#                 "percentage":
#                     percentage,

#                 "introduction":
#                     introduction_result,

#                 "explanation":
#                     explanation_result,

#                 "clarity":
#                     clarity_result,

#                 "conclusion":
#                     conclusion_result,

#                 "bibliography":
#                     bibliography_result,

#                 "tokens":
#                     tokens[:80],

#                 "token_count":
#                     len(tokens),

#                 "section_analysis":
#                     section_analysis,

#                 "extracted_text":
#                     text
#             }

#             all_results.append(
#                 result
#             )

#         # Sort students by marks
#         all_results.sort(
#             key=lambda x: x["total"],
#             reverse=True
#         )

#         result_id = str(uuid.uuid4())

#         result_path = (
#             Path(settings.MEDIA_ROOT)
#             / "results"
#             / f"{result_id}.json"
#         )

#         with open(
#             result_path,
#             "w",
#             encoding="utf-8"
#         ) as file:

#             json.dump(
#                 all_results,
#                 file,
#                 indent=4
#             )

#         request.session["result_id"] = result_id

#         return redirect(
#             "result"
#         )

#     return render(
#         request,
#         "student_upload.html",
#         {
#             "rubric": rubric
#         }
#     )


# # --------------------------------------------------
# # RESULT
# # --------------------------------------------------

# def result(request):

#     result_id = request.session.get(
#         "result_id"
#     )

#     if not result_id:

#         return redirect(
#             "student_upload"
#         )

#     result_path = (
#         Path(settings.MEDIA_ROOT)
#         / "results"
#         / f"{result_id}.json"
#     )

#     if not result_path.exists():

#         return redirect(
#             "student_upload"
#         )

#     with open(
#         result_path,
#         "r",
#         encoding="utf-8"
#     ) as file:

#         results = json.load(file)

#     return render(
#         request,
#         "result.html",
#         {
#             "results": results
#         }
#     )


# # --------------------------------------------------
# # CSV DOWNLOAD
# # --------------------------------------------------

# def download_csv(request):

#     result_id = request.session.get(
#         "result_id"
#     )

#     if not result_id:

#         return redirect(
#             "result"
#         )

#     result_path = (
#         Path(settings.MEDIA_ROOT)
#         / "results"
#         / f"{result_id}.json"
#     )

#     with open(
#         result_path,
#         "r",
#         encoding="utf-8"
#     ) as file:

#         results = json.load(file)

#     response = HttpResponse(
#         content_type="text/csv"
#     )

#     response[
#         "Content-Disposition"
#     ] = (
#         'attachment; filename="evaluation_results.csv"'
#     )

#     writer = csv.writer(response)

#     writer.writerow([
#         "Student",
#         "Introduction",
#         "Explanation",
#         "Clarity",
#         "Conclusion",
#         "Bibliography",
#         "Total",
#         "Percentage"
#     ])

#     for item in results:

#         writer.writerow([
#             item["student"],
#             item["introduction"]["marks"],
#             item["explanation"]["marks"],
#             item["clarity"]["marks"],
#             item["conclusion"]["marks"],
#             item["bibliography"]["marks"],
#             item["total"],
#             item["percentage"]
#         ])

#     return response

import json
import uuid
import csv

from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .gemini_extractor import extract_text_from_pdf

from .ai_model import (
    extract_tokens,
    evaluate_answer
)

from .rubric import (
    validate_rubric,
    calculate_total_marks,
    validate_total_marks
)


# ==================================================
# HOME
# ==================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# ==================================================
# TEACHER RUBRIC
# ==================================================

def teacher_rubric(request):

    if request.method == "POST":

        question = request.POST.get(
            "question",
            ""
        ).strip()

        introduction_marks = float(
            request.POST.get(
                "introduction_marks",
                0
            )
        )

        introduction_expected = request.POST.get(
            "introduction_expected",
            ""
        ).strip()

        explanation_criterion = request.POST.get(
            "explanation_criterion",
            ""
        ).strip()

        explanation_expected = request.POST.get(
            "explanation_expected",
            ""
        ).strip()

        explanation_marks = float(
            request.POST.get(
                "explanation_marks",
                0
            )
        )

        clarity_marks = float(
            request.POST.get(
                "clarity_marks",
                0
            )
        )

        conclusion_marks = float(
            request.POST.get(
                "conclusion_marks",
                0
            )
        )

        conclusion_expected = request.POST.get(
            "conclusion_expected",
            ""
        ).strip()

        bibliography_marks = float(
            request.POST.get(
                "bibliography_marks",
                0
            )
        )


        concepts = []

        if (
            explanation_criterion
            and explanation_expected
        ):

            concepts.append({

                "criterion":
                    explanation_criterion,

                "expected":
                    explanation_expected,

                "marks":
                    explanation_marks
            })


        rubric = {

            "question":
                question,

            "introduction": {

                "marks":
                    introduction_marks,

                "expected":
                    introduction_expected
            },

            "explanation": {

                "marks":
                    sum(
                        float(c["marks"])
                        for c in concepts
                    ),

                "concepts":
                    concepts
            },

            "clarity": {

                "marks":
                    clarity_marks
            },

            "conclusion": {

                "marks":
                    conclusion_marks,

                "expected":
                    conclusion_expected
            },

            "bibliography": {

                "marks":
                    bibliography_marks
            }
        }


        # Validate rubric

        if not validate_rubric(rubric):

            return render(
                request,
                "teacher_rubric.html",
                {
                    "error":
                        "Invalid rubric."
                }
            )


        # Check total marks

        total = calculate_total_marks(
            rubric
        )

        if total != 15:

            return render(
                request,
                "teacher_rubric.html",
                {
                    "error":
                        f"Rubric total is {total}. "
                        "Total must be 15 marks."
                }
            )


        # Save rubric

        rubric_id = str(
            uuid.uuid4()
        )

        rubric_directory = (
            Path(settings.MEDIA_ROOT)
            / "rubrics"
        )

        rubric_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        rubric_path = (
            rubric_directory
            / f"{rubric_id}.json"
        )


        with open(
            rubric_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                rubric,
                file,
                indent=4
            )


        request.session[
            "rubric_id"
        ] = rubric_id


        return redirect(
            "student_upload"
        )


    return render(
        request,
        "teacher_rubric.html"
    )


# ==================================================
# STUDENT PDF UPLOAD
# ==================================================

def student_upload(request):

    rubric_id = request.session.get(
        "rubric_id"
    )

    if not rubric_id:

        return redirect(
            "teacher_rubric"
        )


    rubric_path = (
        Path(settings.MEDIA_ROOT)
        / "rubrics"
        / f"{rubric_id}.json"
    )


    if not rubric_path.exists():

        return redirect(
            "teacher_rubric"
        )


    with open(
        rubric_path,
        "r",
        encoding="utf-8"
    ) as file:

        rubric = json.load(file)


    if request.method == "POST":

        files = request.FILES.getlist(
            "answer_sheets"
        )

        all_results = []


        for pdf_file in files:

            if not pdf_file.name.lower().endswith(
                ".pdf"
            ):
                continue


            # ======================================
            # EXTRACT PDF TEXT
            # ======================================

            text = extract_text_from_pdf(
                pdf_file
            )


            if not text:

                continue


            # ======================================
            # TOKENIZATION
            # ======================================

            tokens = extract_tokens(
                text
            )


            # ======================================
            # AI EVALUATION
            # ======================================

            evaluation = evaluate_answer(
                text,
                rubric
            )


            # ======================================
            # STORE RESULT
            # ======================================

            result = {

                "student":
                    Path(
                        pdf_file.name
                    ).stem,

                "filename":
                    pdf_file.name,

                "question":
                    rubric["question"],

                "token_count":
                    len(tokens),

                "tokens":
                    tokens[:80],

                "extracted_text":
                    text,

                "question_relevance":
                    evaluation[
                        "question_relevance"
                    ],

                "introduction":
                    evaluation[
                        "introduction"
                    ],

                "explanation":
                    evaluation[
                        "explanation"
                    ],

                "clarity":
                    evaluation[
                        "clarity"
                    ],

                "conclusion":
                    evaluation[
                        "conclusion"
                    ],

                "bibliography":
                    evaluation[
                        "bibliography"
                    ],

                "total":
                    evaluation["total"],

                "maximum":
                    evaluation["maximum"],

                "percentage":
                    evaluation["percentage"]
            }


            all_results.append(
                result
            )


        # Save results

        result_directory = (
            Path(settings.MEDIA_ROOT)
            / "results"
        )

        result_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        result_id = str(
            uuid.uuid4()
        )


        result_path = (
            result_directory
            / f"{result_id}.json"
        )


        with open(
            result_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                all_results,
                file,
                indent=4
            )


        request.session[
            "result_id"
        ] = result_id


        return redirect(
            "result"
        )


    return render(
        request,
        "student_upload.html",
        {
            "rubric": rubric
        }
    )


# ==================================================
# RESULT
# ==================================================

def result(request):

    result_id = request.session.get(
        "result_id"
    )

    if not result_id:

        return redirect(
            "student_upload"
        )


    result_path = (
        Path(settings.MEDIA_ROOT)
        / "results"
        / f"{result_id}.json"
    )


    if not result_path.exists():

        return redirect(
            "student_upload"
        )


    with open(
        result_path,
        "r",
        encoding="utf-8"
    ) as file:

        results = json.load(file)


    return render(
        request,
        "result.html",
        {
            "results":
                results
        }
    )


# ==================================================
# DOWNLOAD CSV
# ==================================================

def download_csv(request):

    result_id = request.session.get(
        "result_id"
    )

    if not result_id:

        return redirect(
            "result"
        )


    result_path = (
        Path(settings.MEDIA_ROOT)
        / "results"
        / f"{result_id}.json"
    )


    with open(
        result_path,
        "r",
        encoding="utf-8"
    ) as file:

        results = json.load(file)


    response = HttpResponse(
        content_type="text/csv"
    )


    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="evaluation_results.csv"'
    )


    writer = csv.writer(
        response
    )


    writer.writerow([

        "Student",

        "Question Relevance",

        "Introduction",

        "Explanation",

        "Clarity",

        "Conclusion",

        "Bibliography",

        "Total",

        "Percentage"
    ])


    for item in results:

        writer.writerow([

            item["student"],

            item[
                "question_relevance"
            ]["score"],

            item[
                "introduction"
            ]["marks"],

            item[
                "explanation"
            ]["marks"],

            item[
                "clarity"
            ]["marks"],

            item[
                "conclusion"
            ]["marks"],

            item[
                "bibliography"
            ]["marks"],

            item["total"],

            item["percentage"]
        ])


    return response