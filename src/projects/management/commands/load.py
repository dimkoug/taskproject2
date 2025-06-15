import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from companies.models import Company
from projects.calculate_critical_path import calculate_cpm
from projects.models import *





class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        User = get_user_model()
        Task.objects.all().delete()
        
        user = User.objects.filter(is_superuser=True).last()
        company,_ = Company.objects.get_or_create(name='test')
        company.profiles.add(user.profile)
        category,_ = Category.objects.get_or_create(company=company,name='test')
        project ,_ = Project.objects.get_or_create(category=category,name='test')
        start_date = timezone.now()
        data = [
            {
                'activity': 'a',
                "duration": 3,
                "predecessors": []
            },
            {
                'activity': 'b',
                "duration": 4,
                "predecessors": ['a']
            },
            {
                'activity': 'c',
                "duration": 2,
                "predecessors": ['a']
            },
            {
                'activity': 'd',
                "duration": 5,
                "predecessors": ['b']
            },
            {
                'activity': 'e',
                "duration": 1,
                "predecessors": ['c']
            },
            {
                'activity': 'f',
                "duration": 2,
                "predecessors": ['c']
            },
            {
                'activity': 'g',
                "duration": 4,
                "predecessors": ['d', 'e']
            },
            {
                'activity': 'h',
                "duration": 3,
                "predecessors": ['f', 'g']
            }
        ]
        for d in data:
            try:
                start_date = Task.objects.filter(project=project).last().start_date + datetime.timedelta(days=2)
            except:
                pass
            
            Task.objects.get_or_create(project=project,name=d['activity'],start_date=start_date,end_date=start_date+datetime.timedelta(days=d['duration']))
        
        for d in data:
            if len(d['predecessors']) > 0:
                task = Task.objects.get(project=project,name=d['activity'])
                pred_list = Task.objects.filter(project=project,name__in=d['predecessors'])
                for d in pred_list:
                    Predecessor.objects.get_or_create(to_task=task,from_task=d,start_type=Predecessor.SF)

        data = []
        tasks = Task.objects.prefetch_related('project__category__company__profiles','predecessors').filter(project__category__company__profiles=user.profile.pk,project_id=project.pk)
        for task in tasks:
            activity = {}
            activity['activity'] = task.name
            activity['early_start'] = activity['es'] = task.early_start
            activity['late_start'] = activity['ls'] = task.late_start
            activity['early_finish'] = activity['ef'] = task.early_finish
            activity['duration'] = task.duration
            activity['predecessors'] = []
            for pr in task.successor_tasks.all():
                activity['predecessors'].append(pr.from_task.name)
            data.append(activity)
        calculate_cpm(data, draw_graph=False, draw_gantt=False)
        
        
        self.stdout.write(
            self.style.SUCCESS('Successfully')
        )



