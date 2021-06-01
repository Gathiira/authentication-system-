import uuid
from django.db import models


class SMSMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=100)
    message = models.TextField()
    MESSAGE_STATUS = (
        ('Pending', 'Pending'),
        ('Unsent', 'Unsent'),
        ('Cancelled', 'Cancelled'),
        ('Sent', 'Sent')
    )
    status = models.CharField(max_length=50, choices=MESSAGE_STATUS)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
