from django.contrib import admin
from .models import Subject, ClassTeacherSubject
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Register Subject model in admin
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']
    # Removed filter_horizontal since Subject does not have direct M2M fields for classes/teachers

admin.site.register(Subject, SubjectAdmin)

# Register ClassTeacherSubject model in admin
class ClassTeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'teacher', 'subject')
    list_filter = ('class_obj', 'teacher', 'subject')

admin.site.register(ClassTeacherSubject, ClassTeacherSubjectAdmin)

# Adding Permissions to Admin
def add_permissions():
    content_type = ContentType.objects.get_for_model(Subject)
    Permission.objects.get_or_create(
        codename='can_assign_subject',
        name='Can assign subject to class teacher',
        content_type=content_type,
    )

add_permissions()
