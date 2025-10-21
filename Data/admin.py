from django.contrib import admin
from .models import *

@admin.register(Measuring)
class MeasuringAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'road_photo', 'road_width', 'street_name', 'is_deleated',
        'latitude_position', 'longtiude_position', 'measurment_time', 'measurment_duration'
    ]
    list_filter = ['user', 'measurment_time','is_deleated']
    search_fields = [
         'user__username', 'latitude_position', 'longtiude_position', 'street_name',
        'latitude_start', 'longtiude_start', 'latitude_end', 'longtiude_end'
    ]

    readonly_fields = []

    fieldsets = (
        (None, {
            'fields': ('user', 'road_photo', 'road_width', 'street_name', 'is_deleated')
        }),
        ('Location - Current', {
            'fields': ('latitude_position', 'longtiude_position'),
        }),
        ('Location - Start Point', {
            'fields': ('latitude_start', 'longtiude_start'),
        }),
        ('Location - End Point', {
            'fields': ('latitude_end', 'longtiude_end'),
        }),
        ('Time and Duration', {
            'fields': ('measurment_time', 'measurment_duration'),
        }),
    )


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Intensivity)
class IntensivityAdmin(admin.ModelAdmin):
    list_display = ['transport', 'measuring', 'quanity']
    list_filter = ['transport', 'measuring']
    search_fields = ['transport__name', 'measuring__measurment_time']


@admin.register(PublicTransport)
class PublicTransportAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(PublicTransportNumber)
class PublicTransportNumberAdmin(admin.ModelAdmin):
    list_display = ['public_transport', 'number']
    list_filter = ['public_transport']
    search_fields = ['public_transport__name', 'number']


@admin.register(PeopleInPublicTransport)
class PeopleInPublicTransportAdmin(admin.ModelAdmin):
    list_display = ['public_transport_number', 'measuring', 'time', 'entering_people', 'leaving_people']
    list_filter = ['public_transport_number', 'measuring', 'time']
    search_fields = ['public_transport_number__public_transport__name', 'measuring__measurment_time']