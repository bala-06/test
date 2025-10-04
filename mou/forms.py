from django import forms
from .models import MOU, Department, Outcome, Event



class MOUFilterForm(forms.Form):
    title = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Search by Title', 'class': 'form-control'})
    )
    organization_name = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Search by Organization', 'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    outcome = forms.ModelChoiceField(
        queryset=Outcome.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All'), ('draft', 'Draft'), ('active', 'Active'), ('expired', 'Expired')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
class MOUForm(forms.ModelForm):
    department = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    outcome = forms.ModelMultipleChoiceField(
        queryset=Outcome.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    class Meta:
        model = MOU
        fields = [
            'title','organization_name', 'department', 'start_date', 'end_date', 'document', 'status',
            'mou_coordinator_name', 'mou_coordinator_mobile', 'mou_coordinator_email',
            'staff_coordinator_name', 'staff_coordinator_mobile', 'staff_coordinator_email',
            'outcome', 'payment_paid',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'department': forms.SelectMultiple(attrs={'placeholder': 'Select Department'}),
            'organization_name': forms.TextInput(attrs={'placeholder': 'Enter Organization Name'}),
            'outcome': forms.SelectMultiple(attrs={'placeholder': 'Select Outcomes'}),
            'mou_coordinator_name': forms.TextInput(attrs={'placeholder': 'Enter Coordinator Name'}),
            'mou_coordinator_mobile': forms.TextInput(attrs={'placeholder': 'Enter Mobile Number'}),
            'mou_coordinator_email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
            'staff_coordinator_name': forms.TextInput(attrs={'placeholder': 'Enter Staff Name'}),
            'staff_coordinator_mobile': forms.TextInput(attrs={'placeholder': 'Enter Mobile Number'}),
            'staff_coordinator_email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
            'payment_paid': forms.NumberInput(attrs={'placeholder': 'Enter payment amount'}),
}
