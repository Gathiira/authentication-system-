import uuid
from django.db import models

# Create your models here.

MESSAGE_STATUS = (
    ('PENDING', 'PENDING'),
    ('SENT', 'SENT')
)


class EmailNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.CharField(max_length=100)
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=MESSAGE_STATUS)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.subject)


class EmailRecipients(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.CharField(max_length=100)
    email_request = models.ForeignKey(
        EmailNotification, on_delete=models.CASCADE, related_name='email_repients')
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
