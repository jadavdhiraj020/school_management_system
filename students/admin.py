from django.contrib import admin
from .models import Student

# Register Student model in admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'phone', 'address', 'class_obj')
    search_fields = ['user__username', 'user__email', 'class_obj__name']  # Searching by user info and class name
    list_filter = ('class_obj',)  # Filtering by Class
    ordering = ('user',)  # Sorting by user name
    readonly_fields = ('enrollment_date',)  # Making enrollment date readonly

    # Adding custom permissions for student model
    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'admin':
            return True
        return False


admin.site.register(Student, StudentAdmin)
