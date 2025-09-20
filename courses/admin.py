from django.contrib import admin
from django.db.models import Count
from .models import Student, Instructor, Course, Enrollment


class StudentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email')
    list_filter = ('department',)
    list_display = ('name', 'email', 'department', 'enrollment_date')


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ('student', 'enrollment_date', 'grade')
    # If you expect thousands of students, uncomment:
    # raw_id_fields = ('student',)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'instructor', 'enrolled_students')
    search_fields = ('course_code', 'title', 'instructor__name')
    inlines = (EnrollmentInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate with enrolled count to avoid N+1 queries
        return qs.annotate(_enrolled_count=Count('enrollments'))

    def enrolled_students(self, obj):
        return getattr(obj, '_enrolled_count', obj.enrollments.count())
    enrolled_students.short_description = 'Enrolled Students'
    enrolled_students.admin_order_field = '_enrolled_count'


class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'courses_count')
    search_fields = ('name', 'email')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_courses_count=Count('courses'))

    def courses_count(self, obj):
        return getattr(obj, '_courses_count', obj.courses.count())
    courses_count.short_description = 'Courses Taught'
    courses_count.admin_order_field = '_courses_count'


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'grade')
    search_fields = (
        'student__name', 'student__email',
        'course__course_code', 'course__title'
    )

    def save_model(self, request, obj, form, change):
        # Run model.clean() before saving
        obj.full_clean()
        super().save_model(request, obj, form, change)


# Register models with admin
admin.site.register(Student, StudentAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
