from django.db import models
import uuid


class UploadFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    filename = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
