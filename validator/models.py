from django.db import models

class EmailValidationResult(models.Model):
    email = models.EmailField()
    valid_format = models.BooleanField(default=False)
    mx_records = models.JSONField(null=True, blank=True)
    smtp_deliverable = models.BooleanField(default=False)
    smtp_info = models.JSONField(null=True, blank=True)
    spf = models.CharField(max_length=32, null=True, blank=True)
    dmarc = models.CharField(max_length=32, null=True, blank=True)
    dkim = models.CharField(max_length=32, null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    task_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)