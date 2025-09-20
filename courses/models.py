from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Student(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    enrollment_date = models.DateField(default=timezone.localdate)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Instructor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    hire_date = models.DateField(default=timezone.localdate)

    def __str__(self):
        return self.name


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    credits = models.PositiveSmallIntegerField()
    instructor = models.ForeignKey(
        Instructor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='courses'
    )

    def __str__(self):
        return f"{self.course_code} — {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrollment_date = models.DateField(default=timezone.localdate)
    grade = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course'
            )
        ]

    def clean(self):
        # Extra validation before DB constraint triggers
        if Enrollment.objects.exclude(pk=self.pk).filter(
            student=self.student,
            course=self.course
        ).exists():
            raise ValidationError('This student is already enrolled in this course.')

    def __str__(self):
        return f"{self.student} -> {self.course}"
