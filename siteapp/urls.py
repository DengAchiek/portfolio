from django.urls import path

from .views import download_cv, home


urlpatterns = [
  path("", home, name="home"),
  path("cv/download/", download_cv, name="cv_download"),
]
