from django.db import models

# Create your models here.
from core.models import Timestamped

class Category(Timestamped):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        default_related_name = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Project(Timestamped):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    budget = models.DecimalField(max_digits=18, decimal_places=2,blank=True, null=True)
    name = models.CharField(max_length=100)

    class Meta:
        default_related_name = 'projects'
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __str__(self):
        return self.name


class Task(Timestamped):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    predecessors = models.ManyToManyField("self", through="Predecessor", through_fields=("from_task", "to_task"),symmetrical=False)
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=18, decimal_places=2,blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        default_related_name = 'tasks'
        verbose_name = 'task'
        verbose_name_plural = 'tasks'

    def __str__(self):
        return self.name
    
    @property
    def duration(self):
        return (self.end_date - self.start_date).days


class Predecessor(Timestamped):
    FS, SS, FF ,SF = range(0,4)
    PREDECESSOR_CHOICES = [
        (FS, 'Finish to start'),
        (SS, 'Start to start'),
        (FF, 'Finish to finsish'),
        (SF, 'Start to finish'),
    ]
    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='predecessor_tasks')
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='successor_tasks')
    start_type = models.IntegerField(choices=PREDECESSOR_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_task', 'to_task'], name="predecessors")
        ]
        indexes = [
            models.Index(fields=['from_task', 'to_task']),
        ]

class CPMReport(Timestamped):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


    class Meta:
        ordering = ['-created'] 

    def __str__(self):
        return self.name


class CPMReportData(Timestamped):
    cpmreport = models.ForeignKey(CPMReport, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    es = models.IntegerField(default=0)
    ef = models.IntegerField(default=0)
    ls = models.IntegerField(default=0)
    lf = models.IntegerField(default=0)
    slack = models.IntegerField(default=0)
