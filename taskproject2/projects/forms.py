from django import forms
from django.forms import inlineformset_factory
from core.forms import BootstrapForm, BootstrapFormSet


from .models import Category, Project, Task, Predecessor


class CategoryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','company')


class ProjectForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Project
        fields = ('category','parent','company', 'name','budget')


class TaskForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Task
        fields = ('project', 'name', 'start_date', 'end_date', 'budget')


class PredecessorForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Predecessor
        fields = ('from_task', 'to_task','start_type')


class PredecessorBootstrapFormSet(BootstrapFormSet):
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
