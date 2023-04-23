from functools import reduce
import django_filters
from django.db.models import Q
from base.models import Pokemon

class PokemonFilter(django_filters.FilterSet): 
    
    # Define a choice filter with a list of possible values
    type = django_filters.MultipleChoiceFilter(
        method="filter_by_types",
        choices = [
            ('acier', 'acier'),
            ('combat', 'combat'),
            ('dragon', 'dragon'),
            ('eau', 'eau'),
            ('electrik', 'electrik'),
            ('fee', 'fee'),
            ('feu', 'feu'),
            ('glace', 'glace'),
            ('insecte', 'insecte'),
            ('normal', 'normal'),
            ('plante', 'plante'),
            ('poison', 'poison'),
            ('psy', 'psy'),
            ('roche', 'roche'),
            ('sol', 'sol'),
            ('spectre', 'spectre'),
            ('tenebres', 'tenebres'),
            ('vol', 'vol')
        ],
        
        # return pokemon with both types
        # if set to true, return pokemon with both types
        conjoined = False
    )
    
    
    order_by = django_filters.OrderingFilter(fields=['regional_number', 'national_number', 'name_en', 'name_fr', 'stat_hp', 'stat_atq', 'stat_def', 'stat_spa', 'stat_spd', 'stat_spe'])
    
    class Meta:
        model = Pokemon
        # Custom filter
        fields = ['type']
        
    def filter_by_types(self, queryset, name, values):
        # Return the queryset filtered by the list of selected types
        return queryset.filter(reduce(lambda q, value: q & (Q(type_1=value) | Q(type_2=value)), values, Q()))