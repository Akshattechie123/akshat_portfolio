from django import forms
from .models import ContactMessage, ProjectBrief

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]

class BriefForm(forms.ModelForm):
    class Meta:
        model = ProjectBrief
        fields = ["full_name", "email", "phone", "company", "title", "project_type", "goal",
                  "target_users", "features", "reference_links", "budget", "timeline", "constraints"]
