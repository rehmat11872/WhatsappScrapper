from django.db import models

# Create your models here.
class UserBrowser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    browser_instance_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.browser_instance_id}"