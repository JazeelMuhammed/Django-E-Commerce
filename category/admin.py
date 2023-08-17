from django.contrib import admin
from .models import League, Club

# Register your models here.


class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'img',)
    prepopulated_fields = {'slug': ('name',)}


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'img', 'league')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(League, LeagueAdmin)
admin.site.register(Club, ClubAdmin)
