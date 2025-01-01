from django.db import models

# Create your models here.
class Timestamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(Timestamped):
    name = models.CharField(max_length=255)
    profiles = models.ManyToManyField("profiles.Profile")


    class Meta:
        default_related_name = 'companies'
        verbose_name = 'company'
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name