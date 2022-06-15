from django import forms
from .models import File_Profile
from django.forms import Textarea

#DataFlair #File_Upload
class File_Form(forms.ModelForm):
    class Meta:
        model = File_Profile
        # fields = '__all__'
        fields = ['fasta_file', 'job', 'email', 'textFile']
        widgets = {
            'textFile': Textarea(attrs={'rows':10, 'cols':80})
        }
