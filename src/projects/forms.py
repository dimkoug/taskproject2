from django import forms
from django.forms import inlineformset_factory
from core.forms import BootstrapForm, BootstrapFormSet


from .models import Category, Project, Task, Predecessor


class CategoryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','company')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)



class ProjectForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Project
        fields = ('category','parent','name','budget')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)



class TaskForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Task
        fields = ('project', 'name', 'start_date', 'end_date', 'budget')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)



class PredecessorForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Predecessor
        fields = ('from_task', 'to_task','start_type')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

class PredecessorForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Predecessor
        fields = ('from_task', 'to_task', 'start_type')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
    # def clean(self):
    #     cleaned_data = super().clean()
    #     from_task = cleaned_data.get('from_task')
    #     to_task = cleaned_data.get('to_task')
    #     start_type = cleaned_data.get('start_type')
        
    #     if not from_task or not to_task or not start_type:
    #         return cleaned_data  # Skip validation if required fields are missing

    #     from_start_date = from_task.start_date
    #     from_end_date = from_task.end_date
    #     to_start_date = to_task.start_date
    #     to_end_date = to_task.end_date

    #     if start_type == Predecessor.FS:
    #         if from_end_date.date() > to_start_date.date():
    #             self.add_error('to_task', f"FS: Parent end date {from_end_date} must be before child start date {to_start_date}.")
    #     elif start_type == Predecessor.SS:
    #         if to_start_date.date() != from_start_date.date():
    #             self.add_error('to_task', f"SS: Start dates must match ({from_start_date} vs {to_start_date}).")
    #     elif start_type == Predecessor.FF:
    #         if to_end_date.date() > from_end_date.date():
    #             self.add_error('to_task', f"FF: Child end date {to_end_date} must not be after parent end date {from_end_date}.")
    #     elif start_type == Predecessor.SF:
    #         if to_start_date.date() < from_end_date.date():
    #             self.add_error('to_task', f"SF: Child start date {to_start_date} must not be before parent end date {from_end_date}.")

    #     return cleaned_data











class PredecessorBootstrapFormSet(BootstrapFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # <--- capture request
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['request'] = self.request  # pass request to each form
        return kwargs
    
    def clean(self):
        print("clean")
        start_date = self.instance.start_date
        end_date = self.instance.end_date
        for form in self.forms:
            to_task = form.cleaned_data.get('to_task')
            if to_task:
                print(to_task)
                s_type = form.cleaned_data.get('start_type')
                c_start_date = to_task.start_date
                c_end_date = to_task.end_date
                if s_type == Predecessor.FS:
                    print("fs")
                    if end_date.date() > c_start_date.date():
                        form['to_task'].field.widget.attrs['class'] += ' is-invalid'
                        form.add_error("to_task", "{} {} cannot be used.".format(
                            "to_task", c_end_date))
            
                if s_type == Predecessor.SS:
                    print("ss")
                    if c_start_date.date() != start_date.date():
                        form['to_task'].field.widget.attrs['class'] += ' is-invalid'
                        form.add_error("to_task", "{} {} cannot be used.".format(
                            "to_task", c_start_date))
                if s_type == Predecessor.FF:
                    print("ff")
                    if c_end_date.date() > end_date.date():
                        form['to_task'].field.widget.attrs['class'] += ' is-invalid'
                        form.add_error("to_task", "{} {} cannot be used.".format(
                            "to_task", c_start_date))
                if s_type == Predecessor.SF:
                    print("sf")
                    if c_start_date.date() < end_date.date():
                        form['to_task'].field.widget.attrs['class'] += ' is-invalid'
                        form.add_error("to_task", "{} {} cannot be used.".format(
                            "to_task", c_start_date))




PredecessorFormSet = inlineformset_factory(Task, Predecessor, form=PredecessorForm, formset=PredecessorBootstrapFormSet,
                                           can_delete=True,
                                           fk_name='from_task')


class GanttFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Category"
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        required=False,
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        required=False,
        label="End Date"
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

