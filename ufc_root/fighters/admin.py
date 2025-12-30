from django.contrib import admin
from .models import WeightClass, Fighter

class FighterInline(admin.TabularInline):
    model = Fighter
    extra = 0
    fields = ("name", "rank",)
    readonly_fields = ("name", "rank",)

@admin.register(WeightClass)
class WeightClassAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [FighterInline]

@admin.register(Fighter)
class FighterAdmin(admin.ModelAdmin):
    list_display = ("name", "rank", "weight_class")
    list_filter = ("weight_class",)
    search_fields = ("name",)
