from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    telegram_id = models.IntegerField(unique=True)
    phone_number = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AuthCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
