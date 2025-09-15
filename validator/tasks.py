from celery import shared_task, current_task
from .models import EmailValidationResult
from .utils import is_valid_format, get_mx_records, smtp_check, check_spf, check_dmarc, check_dkim

@shared_task(bind=True, soft_time_limit=60)
def validate_email_task(self, email):
    obj = EmailValidationResult.objects.create(email=email, task_id=self.request.id)

    try:
        obj.valid_format = is_valid_format(email)
        domain = email.split("@", 1)[1].lower()

        mxs = get_mx_records(domain)
        obj.mx_records = mxs

        smtp_result = {"deliverable": False}
        for _, mx in mxs:
            smtp_result = smtp_check(mx_host=mx, to_address=email)
            if smtp_result.get("deliverable"):
                break

        obj.smtp_deliverable = smtp_result.get("deliverable", False)
        obj.smtp_info = smtp_result

        obj.spf = check_spf(domain)
        obj.dmarc = check_dmarc(domain)
        obj.dkim = check_dkim(domain)

        obj.save()
    except Exception as e:
        obj.error = str(e)
        obj.save()
    return {"email": email, "task_id": self.request.id}
