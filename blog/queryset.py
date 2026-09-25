from django.utils import timezone
from django.db import models

class PostQueryset(models.QuerySet):
    def published(self):
        return self.filter(is_verified=True, created_at__lte=timezone.now())