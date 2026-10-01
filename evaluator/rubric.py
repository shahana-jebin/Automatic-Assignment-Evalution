# def validate_rubric(rubric):
#     required_criteria = [
#         "Introduction",
#         "Explanation of theory or idea",
#         "Overall clarity, style, structure and organization",
#         "Clear Conclusion",
#         "Bibliography or Reference"
#     ]

#     for criterion in required_criteria:
#         if criterion not in rubric:
#             return False

#     return True


# def calculate_total_marks(rubric):
#     total = 0

#     for item in rubric.values():
#         total += item["marks"]

#     return total


# # --------------------------------------------------
# # TEST VALID RUBRIC
# # --------------------------------------------------

# rubric = {
#     "Introduction": {
#         "marks": 2,
#         "expected": "Introduces the topic with definition and background."
#     },

#     "Explanation of theory or idea": {
#         "marks": 6,
#         "expected": "Explains the theory, concepts, working and important points."
#     },

#     "Overall clarity, style, structure and organization": {
#         "marks": 3
#     },

#     "Clear Conclusion": {
#         "marks": 2,
#         "expected": "Summarizes the main ideas and gives a final statement."
#     },

#     "Bibliography or Reference": {
#         "marks": 2
#     }
# }


# print("========== RUBRIC EVALUATION ==========")

# # Validate rubric
# if validate_rubric(rubric):
#     print("Rubric is VALID")
# else:
#     print("Rubric is INVALID")


# # Calculate total marks
# total = calculate_total_marks(rubric)

# print("Total Marks:", total)

# print("========================================")


def validate_rubric(rubric):
    """
    Validate the teacher's custom rubric.
    """

    required_fields = [
        "question",
        "introduction",
        "explanation",
        "clarity",
        "conclusion",
        "bibliography"
    ]

    for field in required_fields:
        if field not in rubric:
            return False

    # Check main marks
    if rubric["introduction"]["marks"] < 0:
        return False

    if rubric["explanation"]["marks"] < 0:
        return False

    if rubric["clarity"]["marks"] < 0:
        return False

    if rubric["conclusion"]["marks"] < 0:
        return False

    if rubric["bibliography"]["marks"] < 0:
        return False

    # Explanation concepts should have valid marks
    for concept in rubric["explanation"]["concepts"]:

        if not concept["criterion"].strip():
            return False

        if not concept["expected"].strip():
            return False

        if float(concept["marks"]) < 0:
            return False

    return True


def calculate_total_marks(rubric):

    total = 0

    total += float(rubric["introduction"]["marks"])
    total += float(rubric["explanation"]["marks"])
    total += float(rubric["clarity"]["marks"])
    total += float(rubric["conclusion"]["marks"])
    total += float(rubric["bibliography"]["marks"])

    return round(total, 2)


def validate_total_marks(rubric, expected_total=15):

    total = calculate_total_marks(rubric)

    return total == expected_total

#testing

if __name__ == "__main__":

    test_rubric = {

        "question":
            "Explain the functions of an Operating System.",

        "introduction": {
            "marks": 2,
            "expected":
                "Defines an operating system "
                "and gives basic background."
        },

        "explanation": {
            "marks": 6,

            "concepts": [

                {
                    "criterion":
                        "Process Management",

                    "expected":
                        "Explains how the operating "
                        "system manages processes.",

                    "marks": 1.5
                },

                {
                    "criterion":
                        "Memory Management",

                    "expected":
                        "Explains how the operating "
                        "system manages memory.",

                    "marks": 1.5
                },

                {
                    "criterion":
                        "File Management",

                    "expected":
                        "Explains how the operating "
                        "system manages files.",

                    "marks": 1
                },

                {
                    "criterion":
                        "Device Management",

                    "expected":
                        "Explains management of hardware "
                        "and input output devices.",

                    "marks": 1
                },

                {
                    "criterion":
                        "Security",

                    "expected":
                        "Explains protection and security "
                        "of system resources.",

                    "marks": 1
                }
            ]
        },

        "clarity": {
            "marks": 3
        },

        "conclusion": {
            "marks": 2,
            "expected":
                "Summarizes the main ideas "
                "and gives a final statement."
        },

        "bibliography": {
            "marks": 2
        }
    }

    print(
        "========== RUBRIC TEST =========="
    )

    print(
        "Rubric valid:",
        validate_rubric(test_rubric)
    )

    print(
        "Total marks:",
        calculate_total_marks(test_rubric)
    )

    print(
        "Total is 15:",
        validate_total_marks(test_rubric)
    )