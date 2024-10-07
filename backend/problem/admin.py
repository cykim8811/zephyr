from django.contrib import admin
from .models import Problem

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_text')
    search_fields = ('id', 'text')

    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Text'
