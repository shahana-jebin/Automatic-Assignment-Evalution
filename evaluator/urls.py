# from django.urls import path

# from . import views


# urlpatterns = [

#     path(
#         "",
#         views.home,
#         name="home"
#     ),

#     path(
#         "teacher/",
#         views.teacher_rubric,
#         name="teacher_rubric"
#     ),

#     path(
#         "student/",
#         views.student_upload,
#         name="student_upload"
#     ),

#     path(
#         "result/",
#         views.result,
#         name="result"
#     ),

#     path(
#         "download-csv/",
#         views.download_csv,
#         name="download_csv"
#     ),
# ]


from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "teacher/",
        views.teacher_rubric,
        name="teacher_rubric"
    ),

    path(
        "student/",
        views.student_upload,
        name="student_upload"
    ),

    path(
        "result/",
        views.result,
        name="result"
    ),

    path(
        "download-csv/",
        views.download_csv,
        name="download_csv"
    ),
]