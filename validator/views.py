from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ValidateEmailsSerializer, EmailValidationResultSerializer
from .tasks import validate_email_task
from .models import EmailValidationResult

class SubmitValidationView(APIView):
    def post(self, request):
        serializer = ValidateEmailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data["emails"]

        task_map = {}
        for email in emails:
            task = validate_email_task.delay(email)
            task_map[email] = task.id

        return Response({"submitted": len(emails), "task_map": task_map}, status=status.HTTP_202_ACCEPTED)

class GetResultsView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        task_id = request.query_params.get("task_id")

        qs = EmailValidationResult.objects.all().order_by("-created_at")
        if email:
            qs = qs.filter(email__iexact=email)
        if task_id:
            qs = qs.filter(task_id=task_id)

        serializer = EmailValidationResultSerializer(qs, many=True)
        return Response(serializer.data)
