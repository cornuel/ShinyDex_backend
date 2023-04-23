# from django.contrib import admin
# from .models import Pokemon, ShinyHunter

# # Register your models here.
# class PokemonAdmin(admin.ModelAdmin):
#     ### LIST_DISPLAY
#     list_display = ('__str__', 'type_1', 'type_2', 'stat_sum')
#     ### LIST_FILTERS
#     list_filter = ('type_1',)
#     ### FIELDSETS
#     fieldsets = (
#         ('Numbers', {
#             'fields': ('regional_number', 'national_number')
#         }),
#         ('Names', {
#             'fields': ('name_fr', 'name_en')
#         }),
        
#         ('Stats', {
#             'classes':('collapse',),
#             'fields': ['stat_hp', 
#                        'stat_atq', 
#                        'stat_def', 
#                        'stat_spa', 
#                        'stat_spd',
#                        'stat_spe',
#                        'stat_sum']
#         }),
#         ('Types', {
#             'classes':('collapse',),
#             'fields': ['type_1', 
#                        'type_2']
#         }),
#         ('Images', {
#             'classes':('collapse',),
#             'fields': ['pokedex_img', 
#                        'shiny_img']
#         })
#     )

# admin.site.register(Pokemon, PokemonAdmin)
# admin.site.register(ShinyHunter)