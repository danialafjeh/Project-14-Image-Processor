from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_page, name='home'),
    path("resize/", views.resize_image_view, name="resize"),
    path("convert/", views.convert_image_view, name="convert"),
    path("grayscale/", views.grayscale_image_view, name="grayscale"),
    path("compress/", views.compress_image_view, name='compress'),
    path("processing/<int:job_id>/", views.processing_page, name="processing"),
    path("processing/<int:job_id>/status/", views.processing_status, name="processing_status")
]
