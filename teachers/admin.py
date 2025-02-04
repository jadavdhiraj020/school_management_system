from django.contrib import admin
from teachers.models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'subject_list', 'phone', 'address')
    search_fields = ['user__username', 'user__email', 'subject__name']
    list_filter = ('subject',)
    ordering = ('user__first_name',)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def subject_list(self, obj):
        return ", ".join([str(s) for s in obj.subject.all()])
    subject_list.short_description = 'Subjects'

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'admin'
