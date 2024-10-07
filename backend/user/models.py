from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import TextField
from problem.models import Problem

class Solution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    texts = TextField(default=list)

    def __str__(self):
        return f"{self.user.username}'s solution for {self.problem.id}"
