from django.contrib import admin
from .models import Solution

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'truncated_texts')
    list_filter = ('user', 'problem')
    search_fields = ('user__username', 'problem__id', 'texts')
    raw_id_fields = ('user', 'problem')

    def truncated_texts(self, obj):
        return obj.texts[:50] + '...' if len(obj.texts) > 50 else obj.texts
    truncated_texts.short_description = 'Texts'
