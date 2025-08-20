import jwt
from datetime import datetime, timedelta
from django.core.cache import cache
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from .models import *


class VerifyUserCodeView(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = CodeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            code = serializer.validated_data["code"]  # type: ignore
            user_data = cache.get(code)
            if not user_data:
                return Response({"msg": "Invalid code"}, status=400)

            User.objects.get_or_create(
                telegram_id=user_data["user_id"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone_number=user_data["phone_number"],
            )
            encoded = jwt.encode(
                {
                    "user_id": user_data["user_id"],
                    "phone_number": user_data["phone_number"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "exp": datetime.now() + timedelta(days=2),
                },
                "secret",
                algorithm="HS256",
            )
            return Response({"token": encoded})

        except Exception as e:
            return Response({"msg": f"Error {e}"})
