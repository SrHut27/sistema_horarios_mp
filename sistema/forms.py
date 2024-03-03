from django import forms
from .models import Aula

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['nome', 'dia_semana', 'hora', 'professor', 'turma']

    def clean(self):
        cleaned_data = super().clean()
        professor = cleaned_data.get('professor')
        
        if not professor:
            raise forms.ValidationError("Por favor, selecione um professor para a aula.")
        
        return cleaned_data