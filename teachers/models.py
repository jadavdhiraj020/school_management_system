from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
