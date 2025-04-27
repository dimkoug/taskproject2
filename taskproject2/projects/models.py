from django.db import models
from django.db.models import Min, Max
# Create your models here.
from django.core.exceptions import ValidationError
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
    category = models.ForeignKey("projects.Category", on_delete=models.CASCADE)
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
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    predecessors = models.ManyToManyField("self", through="Predecessor", through_fields=("from_task", "to_task"),symmetrical=False)
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=18, decimal_places=2,blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        default_related_name = 'tasks'
        verbose_name = 'task'
        verbose_name_plural = 'tasks'
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return self.name
    
    @property
    def duration(self):
        return (self.end_date - self.start_date).days

    @property
    def early_start(self):
        # Compute ES based on predecessors
        if self.predecessors.exists():
            return max(predecessor.to_task.early_finish for predecessor in self.predecessor_tasks.all())
        return 0

    @property
    def early_finish(self):
        return self.early_start + self.duration

    @property
    def late_finish(self):
        # Compute LF based on successors
        if self.successor_tasks.exists():
            return min(successor.from_task.late_start for successor in self.successor_tasks.all())
        return self.project.tasks.aggregate(Max('end_date'))['end_date__max']

    @property
    def late_start(self):
        return self.late_finish - self.duration

    @property
    def slack(self):
        return self.late_start - self.early_start


class Predecessor(Timestamped):
    FS, SS, FF ,SF = range(0,4)
    PREDECESSOR_CHOICES = [
        (FS, 'Finish to start'),
        (SS, 'Start to start'),
        (FF, 'Finish to finsish'),
        (SF, 'Start to finish'),
    ]
    from_task = models.ForeignKey("projects.Task", on_delete=models.CASCADE, related_name='predecessor_tasks')
    to_task = models.ForeignKey("projects.Task", on_delete=models.CASCADE, related_name='successor_tasks')
    start_type = models.IntegerField(choices=PREDECESSOR_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_task', 'to_task'], name="predecessors")
        ]
        indexes = [
            models.Index(fields=['from_task', 'to_task']),
            models.Index(fields=['start_type']),  # Add index for start_type
        ]
    def clean(self):
        super().clean()
        # Ensure tasks are not the same
        if self.from_task == self.to_task:
            raise ValidationError("A task cannot be its own predecessor.")

        # Validate based on start_type
        if self.start_type == self.FS:
            # Finish-to-Start: `to_task` start_date must be after `from_task` end_date
            if self.to_task.start_date <= self.from_task.end_date:
                raise ValidationError("For Finish-to-Start, the successor task must start after the predecessor task finishes.")
        elif self.start_type == self.SS:
            # Start-to-Start: `to_task` start_date must be after or equal to `from_task` start_date
            if self.to_task.start_date < self.from_task.start_date:
                raise ValidationError("For Start-to-Start, the successor task must start on or after the predecessor task starts.")
        elif self.start_type == self.FF:
            # Finish-to-Finish: `to_task` end_date must be after or equal to `from_task` end_date
            if self.to_task.end_date < self.from_task.end_date:
                raise ValidationError("For Finish-to-Finish, the successor task must finish on or after the predecessor task finishes.")
        elif self.start_type == self.SF:
            # Start-to-Finish: `to_task` end_date must be after `from_task` start_date
            if self.to_task.end_date <= self.from_task.start_date:
                raise ValidationError("For Start-to-Finish, the successor task must finish after the predecessor task starts.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures `clean()` is called before saving
        super().save(*args, **kwargs)

class CPMReport(Timestamped):
    name = models.CharField(max_length=255)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)


    class Meta:
        ordering = ['-created'] 

    def __str__(self):
        return self.name


class CPMReportData(Timestamped):
    cpmreport = models.ForeignKey("projects.CPMReport", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    es = models.IntegerField(default=0)
    ef = models.IntegerField(default=0)
    ls = models.IntegerField(default=0)
    lf = models.IntegerField(default=0)
    slack = models.IntegerField(default=0)
