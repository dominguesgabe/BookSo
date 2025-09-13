from django.contrib import admin

from .models import Book, Genre


class GenreInline(admin.StackedInline):
    model = Genre


class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "language", "page_number", "genres"]}),
        ("Date information", {"fields": ["publish_date"]}),
    ]
    readonly_fields = ["created_at"]


admin.site.register(Book)
admin.site.register(Genre)
