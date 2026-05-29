from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'excerpt', 'author', 'is_published', 'tags')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image'),
            'classes': ('collapse',),
        }),
    )
