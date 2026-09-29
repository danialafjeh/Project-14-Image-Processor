from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from PIL import Image as PILImage
from .models import Image, ProcessingJob
from .tasks import (
    resize_image_task, 
    convert_image_task, 
    grayscale_image_task,
    compress_image_task
)

# Create your views here.

def home_page(request):
    return render(request, 'main_page.html', {})



def processing_page(request, job_id):
    job = get_object_or_404(ProcessingJob, id=job_id)
    return render(request, "processing.html", {"job":job})



def processing_status(request, job_id):
    job = get_object_or_404(ProcessingJob, id=job_id)

    data = {
        "status": job.status,
    }

    if job.status == "completed":
        data["result_url"] = job.result_file.url

    if job.status == "failed":
        data["error"] = job.error_message

    return JsonResponse(data)



def resize_image_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        width = request.POST.get("width")
        height = request.POST.get("height")

        if not image_file:
            messages.error(request, "Please upload an image.", extra_tags="resize")
            return redirect("home")

        try:
            image = PILImage.open(image_file)
            image.verify()
        except Exception:
            messages.error(request, "The uploaded file is not a valid image.", extra_tags="resize")
            return redirect("home")

        try:
            width = int(width)
            height = int(height)
        except (TypeError, ValueError):
            messages.error(request, "Width and height must be valid numbers.", extra_tags="resize")
            return redirect("home")

        if width <= 0 or height <= 0:
            messages.error(request, "Width and height must be greater than zero.", extra_tags="resize")
            return redirect("home")

        image_file.seek(0)

        image = Image.objects.create(file=image_file)
        job = ProcessingJob.objects.create(
            image=image,
            operation="resize",
            parameters={
                "width": width,
                "height": height,
            },
        )

        resize_image_task.delay(job.id)

        return redirect("processing", job_id=job.id)
    else:
        return redirect("home")



def convert_image_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        output_format = request.POST.get("format")

        if not image_file:
            messages.error(request, "Please upload an image.", extra_tags="convert")
            return redirect("home")

        try:
            image = PILImage.open(image_file)
            image.verify()
        except Exception:
            messages.error(request, "The uploaded file is not a valid image.", extra_tags="convert")
            return redirect("home")
        
        allowed_formats = ["jpeg", "png", "webp"]

        if output_format not in allowed_formats:
            messages.error(request, "Invalid output format.", extra_tags="convert")
            return redirect("home")

        image_file.seek(0)

        image = Image.objects.create(file=image_file)
        job = ProcessingJob.objects.create(
            operation="convert",
            image=image,
            parameters={
                "format": output_format,
            },
        )

        convert_image_task.delay(job.id)

        return redirect("processing", job_id=job.id)
    else:
        return redirect("home")



def grayscale_image_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")

        if not image_file:
            messages.error(request, "Please upload an image.", extra_tags="grayscale")
            return redirect("home")

        try:
            image = PILImage.open(image_file)
            image.verify()
        except Exception:
            messages.error(request, "The uploaded file is not a valid image.", extra_tags="grayscale")
            return redirect("home")

        image_file.seek(0)

        image = Image.objects.create(file=image_file)
        job = ProcessingJob.objects.create(
            operation="grayscale",
            image=image,
            parameters={}
        )

        grayscale_image_task.delay(job.id)

        return redirect("processing", job_id=job.id)
    else:
        return redirect("home")



def compress_image_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        quality = request.POST.get("quality")

        if not image_file:
            messages.error(request, "Please upload an image.", extra_tags="compress")
            return redirect("home")

        try:
            image = PILImage.open(image_file)
            image.verify()
        except Exception:
            messages.error(request, "The uploaded file is not a valid image.", extra_tags="compress")
            return redirect("home")

        try:
            quality = int(quality)
        except (TypeError, ValueError):
            messages.error(request, "Invalid quality value.", extra_tags="compress")
            return redirect("home")

        if not 1 <= quality <= 100:
            messages.error(request, "Quality must be between 1 and 100.", extra_tags="compress")
            return redirect("home")

        image = Image.objects.create(file=image_file)
        job = ProcessingJob.objects.create(
            operation="compress",
            image=image,
            parameters={
                "quality": quality,
            },
        )

        compress_image_task.delay(job.id)

        return redirect("processing", job_id=job.id)
    else:
        return redirect("home")