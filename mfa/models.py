import uuid
from django.db import models

# Create your models here.

STATUS_TYPES = [
    ("REVOKED", 'REVOKED'),
    ("PENDING", 'PENDING'),
]


class CodeVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=500)
    send_to = models.CharField(max_length=500)
    code = models.IntegerField(blank=True, null=True)
    creation_date = models.DateTimeField()
    expiry_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    module = models.CharField(max_length=255)
