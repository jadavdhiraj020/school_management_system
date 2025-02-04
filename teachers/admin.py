from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from teachers.models import Teacher
from django.contrib.auth.models import Permission


# Register Teacher model in admin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'phone', 'email', 'address')
    search_fields = ['user__username', 'user__email', 'subject__name']  # Searching by user info and subject
    list_filter = ('subject',)  # Filtering by subject
    ordering = ('user',)  # Sorting by user name

    # Adding custom permissions for teacher model
    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'admin':
            return True
        return False


admin.site.register(Teacher, TeacherAdmin)


# Adding Permissions to Admin (if necessary for future permissions control)
def add_permissions():
    # Adding custom permission to allow admin to manage subjects for teachers
    permission, created = Permission.objects.get_or_create(
        codename='can_assign_teacher',
        name='Can assign teacher to class',
        content_type=ContentType.objects.get_for_model(Teacher),
    )
    permission, created = Permission.objects.get_or_create(
        codename='can_view_teacher',
        name='Can view teacher details',
        content_type=ContentType.objects.get_for_model(Teacher),
    )


add_permissions()
