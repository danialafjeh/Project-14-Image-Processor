from django.db import models

# Create your models here.

class Image(models.Model):
    file = models.ImageField(upload_to="images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)



class ProcessingJob(models.Model):
    OPS_CHOICES = [
        ("resize", "Resize"),
        ("convert", "Convert"),
        ("grayscale", "Grayscale"),
        ("compress", "Compress"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="jobs")
    operation = models.CharField(max_length=20, choices=OPS_CHOICES)
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result_file = models.ImageField(upload_to="processed/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
