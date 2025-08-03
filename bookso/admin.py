from django.contrib import admin

# from django.contrib.auth.models import User
from .models import Book, Genre


class GenreInline(admin.StackedInline):
    model = Genre


class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "language", "page_number", "genres"]}),
        ("Date information", {"fields": ["publish_date"]}),
    ]
    readonly_fields = ["created_at"]


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
