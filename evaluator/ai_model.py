# from sentence_transformers import SentenceTransformer, util
# from transformers import pipeline
# import re


# # --------------------------------------------------
# # LOAD AI MODELS ONCE
# # --------------------------------------------------

# semantic_model = SentenceTransformer(
#     "all-MiniLM-L6-v2"
# )

# nli_model = pipeline(
#     "text-classification",
#     model="cross-encoder/nli-deberta-v3-base"
# )


# # --------------------------------------------------
# # TOKENIZATION
# # --------------------------------------------------

# def extract_tokens(text):
#     tokens = semantic_model.tokenizer.tokenize(text)

#     return tokens


# # --------------------------------------------------
# # SPLIT TEXT INTO PARAGRAPHS
# # --------------------------------------------------

# def split_paragraphs(text):

#     paragraphs = re.split(r'\n\s*\n', text)

#     paragraphs = [
#         p.strip()
#         for p in paragraphs
#         if p.strip()
#     ]

#     return paragraphs


# # --------------------------------------------------
# # SPLIT TEXT INTO SENTENCES
# # --------------------------------------------------

# def split_sentences(text):

#     sentences = re.split(
#         r'(?<=[.!?])\s+',
#         text
#     )

#     sentences = [
#         s.strip()
#         for s in sentences
#         if s.strip()
#     ]

#     return sentences


# # --------------------------------------------------
# # SEMANTIC SIMILARITY
# # --------------------------------------------------

# def semantic_similarity(student_text, expected_text):

#     if not student_text.strip():
#         return 0.0

#     if not expected_text.strip():
#         return 0.0

#     student_embedding = semantic_model.encode(
#         student_text,
#         convert_to_tensor=True,
#         normalize_embeddings=True
#     )

#     expected_embedding = semantic_model.encode(
#         expected_text,
#         convert_to_tensor=True,
#         normalize_embeddings=True
#     )

#     similarity = util.cos_sim(
#         student_embedding,
#         expected_embedding
#     ).item()

#     similarity = max(
#         0.0,
#         min(1.0, similarity)
#     )

#     return similarity


# # --------------------------------------------------
# # FIND BEST MATCH
# # --------------------------------------------------

# def find_best_semantic_match(student_sentences, expected_text):

#     if not student_sentences:
#         return {
#             "score": 0,
#             "sentence": ""
#         }

#     best_score = 0
#     best_sentence = ""

#     expected_embedding = semantic_model.encode(
#         expected_text,
#         convert_to_tensor=True,
#         normalize_embeddings=True
#     )

#     student_embeddings = semantic_model.encode(
#         student_sentences,
#         convert_to_tensor=True,
#         normalize_embeddings=True
#     )

#     similarities = util.cos_sim(
#         student_embeddings,
#         expected_embedding
#     )

#     for index, value in enumerate(similarities):

#         score = max(
#             0.0,
#             min(1.0, float(value.item()))
#         )

#         if score > best_score:
#             best_score = score
#             best_sentence = student_sentences[index]

#     return {
#         "score": best_score,
#         "sentence": best_sentence
#     }

# # --------------------------------------------------
# # NLI CORRECTNESS CHECK
# # --------------------------------------------------

# def check_correctness(student_sentence, expected_sentence):

#     if not student_sentence or not expected_sentence:
#         return {
#             "label": "neutral",
#             "score": 0.0
#         }

#     result = nli_model(
#         {
#             "text": expected_sentence,
#             "text_pair": student_sentence
#         }
#     )

#     # Handle both dictionary and list outputs
#     if isinstance(result, list):
#         result = result[0]

#     label = result["label"].lower()
#     score = float(result["score"])

#     return {
#         "label": label,
#         "score": score
#     }

# # --------------------------------------------------
# # SECTION CLASSIFICATION
# # --------------------------------------------------

# SECTION_DESCRIPTIONS = {

#     "Introduction":
#         "introduces the topic, gives a definition, background and purpose",

#     "Explanation":
#         "explains the theory, idea, concepts, working, features and important points",

#     "Conclusion":
#         "summarizes the main ideas and gives a final statement about the topic"
# }


# def classify_section(paragraph):

#     if not paragraph.strip():
#         return {
#             "section": "Unknown",
#             "score": 0
#         }

#     paragraph_embedding = semantic_model.encode(
#         paragraph,
#         convert_to_tensor=True,
#         normalize_embeddings=True
#     )

#     best_section = "Explanation"
#     best_score = 0

#     for section, description in SECTION_DESCRIPTIONS.items():

#         description_embedding = semantic_model.encode(
#             description,
#             convert_to_tensor=True,
#             normalize_embeddings=True
#         )

#         score = util.cos_sim(
#             paragraph_embedding,
#             description_embedding
#         ).item()

#         score = max(
#             0,
#             min(1, score)
#         )

#         if score > best_score:
#             best_score = score
#             best_section = section

#     return {
#         "section": best_section,
#         "score": best_score
#     }


# # --------------------------------------------------
# # INTRODUCTION EVALUATION
# # --------------------------------------------------

# def evaluate_introduction(text, expected):

#     paragraphs = split_paragraphs(text)

#     if not paragraphs:
#         return {
#             "marks": 0,
#             "similarity": 0,
#             "matched_text": ""
#         }

#     # Give more importance to beginning paragraphs
#     candidates = paragraphs[:3]

#     result = find_best_semantic_match(
#         candidates,
#         expected
#     )

#     marks = result["score"] * 2

#     return {
#         "marks": round(marks, 2),
#         "similarity": round(result["score"] * 100, 2),
#         "matched_text": result["sentence"]
#     }


# # --------------------------------------------------
# # CONCLUSION EVALUATION
# # --------------------------------------------------

# def evaluate_conclusion(text, expected):

#     paragraphs = split_paragraphs(text)

#     if not paragraphs:
#         return {
#             "marks": 0,
#             "similarity": 0,
#             "matched_text": ""
#         }

#     # Give more importance to ending paragraphs
#     candidates = paragraphs[-3:]

#     result = find_best_semantic_match(
#         candidates,
#         expected
#     )

#     marks = result["score"] * 2

#     return {
#         "marks": round(marks, 2),
#         "similarity": round(result["score"] * 100, 2),
#         "matched_text": result["sentence"]
#     }


# # --------------------------------------------------
# # EXPLANATION EVALUATION
# # --------------------------------------------------

# def evaluate_explanation(text, concepts):

#     sentences = split_sentences(text)

#     results = []

#     total_marks = 0

#     for concept in concepts:

#         criterion = concept["criterion"]
#         expected = concept["expected"]
#         maximum_marks = float(concept["marks"])

#         match = find_best_semantic_match(
#             sentences,
#             expected
#         )

#         correctness = check_correctness(
#             match["sentence"],
#             expected
#         )

#         semantic_score = match["score"]

#         # Basic correctness adjustment
#         if correctness["label"] == "contradiction":
#             final_score = 0

#         else:
#             final_score = semantic_score

#         marks = final_score * maximum_marks

#         total_marks += marks

#         results.append({
#             "criterion": criterion,
#             "maximum": maximum_marks,
#             "similarity": round(
#                 semantic_score * 100,
#                 2
#             ),
#             "correctness": correctness["label"],
#             "marks": round(marks, 2),
#             "matched_text": match["sentence"]
#         })

#     return {
#         "marks": round(total_marks, 2),
#         "details": results
#     }


# # --------------------------------------------------
# # CLARITY / STRUCTURE
# # --------------------------------------------------

# def evaluate_clarity(text):

#     paragraphs = split_paragraphs(text)
#     sentences = split_sentences(text)

#     if not sentences:
#         return {
#             "marks": 0,
#             "details": "No readable text found."
#         }

#     score = 0

#     # Sentence organization
#     if len(sentences) >= 3:
#         score += 1

#     # Paragraph organization
#     if len(paragraphs) >= 2:
#         score += 1

#     # Reasonable sentence length
#     average_length = (
#         sum(len(s.split()) for s in sentences)
#         / len(sentences)
#     )

#     if 5 <= average_length <= 40:
#         score += 1

#     score = min(score, 3)

#     return {
#         "marks": score,
#         "details": (
#             "Evaluated using sentence organization, "
#             "paragraph organization and readability."
#         )
#     }


# # --------------------------------------------------
# # BIBLIOGRAPHY
# # --------------------------------------------------

# def evaluate_bibliography(text):

#     reference_words = [
#         "reference",
#         "references",
#         "bibliography",
#         "journal",
#         "doi",
#         "www.",
#         "http",
#         "author"
#     ]

#     text_lower = text.lower()

#     found = 0

#     for word in reference_words:

#         if word in text_lower:
#             found += 1

#     if found >= 3:
#         marks = 2

#     elif found >= 1:
#         marks = 1

#     else:
#         marks = 0

#     return {
#         "marks": marks
#     }
    
#  # --------------------------------------------------
# # TESTING WITH SAMPLE PDF
# # --------------------------------------------------

# from pdf_extractor import extract_text_from_pdf

# pdf_path = "sample.pdf"

# with open(pdf_path, "rb") as pdf_file:

#     # STEP 1: Extract text from PDF
#     extracted_text = extract_text_from_pdf(pdf_file)

# print("\n========== PDF EXTRACTION ==========")
# print(extracted_text)

# # STEP 2: Tokenize extracted PDF text
# tokens = extract_tokens(extracted_text)

# print("\n========== TOKENIZATION ==========")
# print("Total Tokens:", len(tokens))
# print("First 50 Tokens:")
# print(tokens[:50])

# # STEP 3: Split extracted text into sentences
# sentences = split_sentences(extracted_text)

# print("\n========== SENTENCES ==========")
# print(sentences)

# # STEP 4: Split extracted text into paragraphs
# paragraphs = split_paragraphs(extracted_text)

# print("\n========== PARAGRAPHS ==========")
# print(paragraphs)

# print("\n========== TEST COMPLETED ==========")



from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import re


# ==================================================
# LOAD AI MODELS
# ==================================================

semantic_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

nli_model = pipeline(
    "text-classification",
    model="cross-encoder/nli-deberta-v3-base"
)


# ==================================================
# TOKENIZATION
# ==================================================

def extract_tokens(text):

    if not text.strip():
        return []

    tokens = semantic_model.tokenizer.tokenize(text)

    return tokens


# ==================================================
# SPLIT PARAGRAPHS
# ==================================================

def split_paragraphs(text):

    paragraphs = re.split(
        r'\n\s*\n',
        text
    )

    paragraphs = [
        p.strip()
        for p in paragraphs
        if p.strip()
    ]

    return paragraphs


# ==================================================
# SPLIT SENTENCES
# ==================================================

def split_sentences(text):

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    sentences = [
        s.strip()
        for s in sentences
        if s.strip()
    ]

    return sentences


# ==================================================
# SEMANTIC SIMILARITY
# ==================================================

def semantic_similarity(student_text, expected_text):

    if not student_text.strip():
        return 0.0

    if not expected_text.strip():
        return 0.0

    student_embedding = semantic_model.encode(
        student_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    expected_embedding = semantic_model.encode(
        expected_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarity = util.cos_sim(
        student_embedding,
        expected_embedding
    ).item()

    similarity = max(
        0.0,
        min(1.0, similarity)
    )

    return similarity


# ==================================================
# FIND BEST SEMANTIC MATCH
# ==================================================

def find_best_semantic_match(
    student_sentences,
    expected_text
):

    if not student_sentences:
        return {
            "score": 0.0,
            "sentence": ""
        }

    if not expected_text.strip():
        return {
            "score": 0.0,
            "sentence": ""
        }

    expected_embedding = semantic_model.encode(
        expected_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    student_embeddings = semantic_model.encode(
        student_sentences,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        student_embeddings,
        expected_embedding
    )

    best_score = 0.0
    best_sentence = ""

    for index, value in enumerate(similarities):

        score = float(value.item())

        score = max(
            0.0,
            min(1.0, score)
        )

        if score > best_score:

            best_score = score

            best_sentence = student_sentences[index]

    return {
        "score": best_score,
        "sentence": best_sentence
    }


# ==================================================
# NLI CORRECTNESS CHECK
# ==================================================

def check_correctness(
    student_sentence,
    expected_sentence
):

    if not student_sentence or not expected_sentence:

        return {
            "label": "neutral",
            "score": 0.0
        }

    result = nli_model(
        {
            "text": expected_sentence,
            "text_pair": student_sentence
        }
    )

    if isinstance(result, list):
        result = result[0]

    label = result["label"].lower()

    score = float(result["score"])

    return {
        "label": label,
        "score": score
    }


# ==================================================
# QUESTION RELEVANCE
# ==================================================

def evaluate_question_relevance(
    text,
    question
):

    sentences = split_sentences(text)

    if not sentences:
        return {
            "score": 0.0,
            "matched_text": ""
        }

    result = find_best_semantic_match(
        sentences,
        question
    )

    return {
        "score": round(result["score"] * 100, 2),
        "matched_text": result["sentence"]
    }


# ==================================================
# INTRODUCTION
# ==================================================

def evaluate_introduction(
    text,
    expected,
    maximum_marks
):

    paragraphs = split_paragraphs(text)

    if not paragraphs:

        return {
            "marks": 0,
            "similarity": 0,
            "matched_text": ""
        }

    candidates = paragraphs[:3]

    result = find_best_semantic_match(
        candidates,
        expected
    )

    marks = result["score"] * float(maximum_marks)

    return {
        "marks": round(marks, 2),
        "similarity": round(
            result["score"] * 100,
            2
        ),
        "matched_text": result["sentence"]
    }


# ==================================================
# EXPLANATION
# ==================================================

def evaluate_explanation(
    text,
    concepts
):

    sentences = split_sentences(text)

    results = []

    total_marks = 0.0

    for concept in concepts:

        criterion = concept["criterion"]

        expected = concept["expected"]

        maximum_marks = float(
            concept["marks"]
        )

        match = find_best_semantic_match(
            sentences,
            expected
        )

        correctness = check_correctness(
            match["sentence"],
            expected
        )

        semantic_score = match["score"]

        # Contradiction receives zero
        if correctness["label"] == "contradiction":

            final_score = 0.0

        else:

            final_score = semantic_score

        marks = (
            final_score *
            maximum_marks
        )

        total_marks += marks

        results.append({

            "criterion": criterion,

            "maximum": maximum_marks,

            "similarity": round(
                semantic_score * 100,
                2
            ),

            "correctness":
                correctness["label"],

            "marks":
                round(marks, 2),

            "matched_text":
                match["sentence"]
        })

    return {

        "marks":
            round(total_marks, 2),

        "details":
            results
    }


# ==================================================
# CLARITY / STRUCTURE
# ==================================================

def evaluate_clarity(
    text,
    maximum_marks
):

    paragraphs = split_paragraphs(text)

    sentences = split_sentences(text)

    if not sentences:

        return {
            "marks": 0,
            "details": "No readable text found."
        }

    score = 0

    if len(sentences) >= 3:
        score += 1

    if len(paragraphs) >= 2:
        score += 1

    average_length = (
        sum(
            len(s.split())
            for s in sentences
        )
        / len(sentences)
    )

    if 5 <= average_length <= 40:
        score += 1

    score = min(score, 3)

    marks = (
        score / 3
    ) * float(maximum_marks)

    return {

        "marks":
            round(marks, 2),

        "details":
            "Evaluated using sentence organization, "
            "paragraph organization and readability."
    }


# ==================================================
# CONCLUSION
# ==================================================

def evaluate_conclusion(
    text,
    expected,
    maximum_marks
):

    paragraphs = split_paragraphs(text)

    if not paragraphs:

        return {
            "marks": 0,
            "similarity": 0,
            "matched_text": ""
        }

    candidates = paragraphs[-3:]

    result = find_best_semantic_match(
        candidates,
        expected
    )

    marks = (
        result["score"] *
        float(maximum_marks)
    )

    return {

        "marks":
            round(marks, 2),

        "similarity":
            round(result["score"] * 100, 2),

        "matched_text":
            result["sentence"]
    }


# ==================================================
# BIBLIOGRAPHY
# ==================================================

def evaluate_bibliography(
    text,
    maximum_marks
):

    reference_words = [

        "reference",
        "references",
        "bibliography",
        "journal",
        "doi",
        "www.",
        "http",
        "author"
    ]

    text_lower = text.lower()

    found = 0

    for word in reference_words:

        if word in text_lower:

            found += 1

    if found >= 3:

        marks = float(maximum_marks)

    elif found >= 1:

        marks = float(maximum_marks) / 2

    else:

        marks = 0.0

    return {

        "marks":
            round(marks, 2)
    }


# ==================================================
# COMPLETE ANSWER EVALUATION
# ==================================================

def evaluate_answer(
    text,
    rubric
):

    question_result = evaluate_question_relevance(
        text,
        rubric["question"]
    )

    introduction_result = evaluate_introduction(
        text,
        rubric["introduction"]["expected"],
        rubric["introduction"]["marks"]
    )

    explanation_result = evaluate_explanation(
        text,
        rubric["explanation"]["concepts"]
    )

    clarity_result = evaluate_clarity(
        text,
        rubric["clarity"]["marks"]
    )

    conclusion_result = evaluate_conclusion(
        text,
        rubric["conclusion"]["expected"],
        rubric["conclusion"]["marks"]
    )

    bibliography_result = evaluate_bibliography(
        text,
        rubric["bibliography"]["marks"]
    )

    total = (

        introduction_result["marks"]

        + explanation_result["marks"]

        + clarity_result["marks"]

        + conclusion_result["marks"]

        + bibliography_result["marks"]
    )

    maximum = (

        float(rubric["introduction"]["marks"])

        + float(rubric["explanation"]["marks"])

        + float(rubric["clarity"]["marks"])

        + float(rubric["conclusion"]["marks"])

        + float(rubric["bibliography"]["marks"])
    )

    total = min(
        total,
        maximum
    )

    percentage = 0

    if maximum > 0:

        percentage = (
            total / maximum
        ) * 100

    return {

        "question":
            rubric["question"],

        "question_relevance":
            question_result,

        "introduction":
            introduction_result,

        "explanation":
            explanation_result,

        "clarity":
            clarity_result,

        "conclusion":
            conclusion_result,

        "bibliography":
            bibliography_result,

        "total":
            round(total, 2),

        "maximum":
            round(maximum, 2),

        "percentage":
            round(percentage, 2)
    }