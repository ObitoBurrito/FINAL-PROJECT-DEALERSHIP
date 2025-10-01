from django.contrib import admin
from .models import CarMake, CarModel


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'established_year')
    search_fields = ('name', 'country')
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'type', 'year', 'dealer_id')
    list_filter = ('make', 'type', 'year')
    search_fields = ('name', 'make__name')
