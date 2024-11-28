from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    checker_image = models.ImageField(
        upload_to="checker_images/", verbose_name="Checker Image"
    )

    def __str__(self):
        return self.username
