from celery import shared_task
from django.utils import timezone
import time
from PIL import Image as PILImage
from .models import ProcessingJob
from io import BytesIO
from uuid import uuid4
from django.core.files.base import ContentFile



@shared_task
def resize_image_task(job_id):
    job = ProcessingJob.objects.get(id=job_id)
    job.status = "processing"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        time.sleep(5)

        width = job.parameters["width"]
        height = job.parameters["height"]

        with PILImage.open(job.image.file) as image:
            resized_image = image.resize((width, height))

            output = BytesIO()

            image_format = image.format or "PNG"

            if image_format == "JPEG" and resized_image.mode not in ("RGB", "L"):
                resized_image = resized_image.convert("RGB")

            resized_image.save(output, format=image_format)

            output.seek(0)

        extension = {
            "JPEG": "jpg",
            "PNG": "png",
            "WEBP": "webp",
        }.get(image_format, image_format.lower())

        filename = f"resized_{uuid4().hex}.{extension}"

        job.result_file.save(
            filename,
            ContentFile(output.read()),
            save=False,
        )

        job.status = "completed"
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "result_file",
                "status",
                "finished_at",
            ]
        )

    except Exception as error:
        job.status = "failed"
        job.error_message = str(error)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at",
            ]
        )



@shared_task
def convert_image_task(job_id):
    job = ProcessingJob.objects.get(id=job_id)
    job.status = "processing"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        time.sleep(5)

        output_format = job.parameters["format"].upper()

        with PILImage.open(job.image.file) as image:

            if output_format == "JPEG" and image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            output = BytesIO()

            image.save(output, format=output_format)

            output.seek(0)

        extension = {
            "JPEG": "jpg",
            "PNG": "png",
            "WEBP": "webp",
        }.get(output_format, output_format.lower())

        filename = f"converted_{uuid4().hex}.{extension}"

        job.result_file.save(
            filename,
            ContentFile(output.read()),
            save=False,
        )

        job.status = "completed"
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "result_file",
                "status",
                "finished_at",
            ]
        )

    except Exception as error:
        job.status = "failed"
        job.error_message = str(error)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at",
            ]
        )



@shared_task
def grayscale_image_task(job_id):
    job = ProcessingJob.objects.get(id=job_id)

    job.status = "processing"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        time.sleep(5)

        with PILImage.open(job.image.file) as image:

            grayscale_image = image.convert("L")

            output = BytesIO()

            grayscale_image.save(
                output,
                format="PNG"
            )

            output.seek(0)

        filename = f"grayscale_{uuid4().hex}.png"

        job.result_file.save(
            filename,
            ContentFile(output.read()),
            save=False,
        )

        job.status = "completed"
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "result_file",
                "status",
                "finished_at",
            ]
        )

    except Exception as error:

        job.status = "failed"
        job.error_message = str(error)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at",
            ]
        )



@shared_task
def compress_image_task(job_id):
    job = ProcessingJob.objects.get(id=job_id)
    job.status = "processing"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        time.sleep(5)

        quality = job.parameters["quality"]

        with PILImage.open(job.image.file) as image:

            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            output = BytesIO()

            image.save(
                output,
                format="JPEG",
                quality=quality
            )

            output.seek(0)

        filename = f"compressed_{uuid4().hex}.jpg"

        job.result_file.save(
            filename,
            ContentFile(output.read()),
            save=False,
        )

        job.status = "completed"
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "result_file",
                "status",
                "finished_at",
            ]
        )

    except Exception as error:

        job.status = "failed"
        job.error_message = str(error)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at",
            ]
        )
        