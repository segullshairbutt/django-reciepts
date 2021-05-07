from django.urls import path

from invoices.views import IndexView, generate_pdf


urlpatterns = [
    path("", IndexView.as_view()),
    path("pdf", generate_pdf)
]
