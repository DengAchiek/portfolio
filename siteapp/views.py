from django.http import HttpResponse
from django.shortcuts import render

from .content import build_portfolio_context, get_portfolio_page
from .pdf import build_cv_pdf


def home(request):
  context = build_portfolio_context(get_portfolio_page())
  return render(request, "siteapp/home.html", context)


def download_cv(request):
  context = build_portfolio_context(get_portfolio_page())
  pdf_bytes = build_cv_pdf(
    profile=context["profile"],
    focus_areas=context["focus_areas"],
    strengths=context["strengths"],
    skills=context["skills"],
    experience=context["experience"],
    education=context["education"],
    projects=context["projects"],
    certifications=context["certifications"],
  )
  response = HttpResponse(pdf_bytes, content_type="application/pdf")
  response["Content-Disposition"] = f'attachment; filename="{context["profile"]["cv_filename"]}"'
  return response
