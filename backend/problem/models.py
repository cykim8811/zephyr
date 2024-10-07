from django.db import models

class Problem(models.Model):
    text = models.TextField()
    prompt = models.TextField()
    id = models.CharField(max_length=32, primary_key=True)

    def __str__(self):
        return self.id