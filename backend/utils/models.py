from django.db import models


class PrivacyStatement(models.Model):
    file = models.FileField(upload_to="utils/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class CookieStatement(models.Model):
    file = models.FileField(upload_to="utils/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
