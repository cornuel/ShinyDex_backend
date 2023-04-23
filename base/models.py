from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_resized import ResizedImageField
from storages.backends.s3boto3 import S3Boto3Storage

import pyrebase

# Create your models here.
POKEDEX = "pokedex_img"
SHINY = "shiny_img"

class Pokemon(models.Model):
    def upload_to_pokedex(instance, filename):
        filename = str(instance.national_number) + "-" + instance.name_fr + "-pokedex" + ".webp"
        return '/'.join(['images', POKEDEX, filename])
    def upload_to_shiny(instance, filename):
        filename = str(instance.national_number) + "-" + instance.name_fr + "-shiny_sprite" + ".webp"
        return '/'.join(['images', SHINY, filename])
    
    ### SLUG
    slug = models.SlugField(null=True, max_length=40, unique=True)
    
    ### NUMBERS
    regional_number = models.IntegerField(unique=True)
    national_number = models.IntegerField(unique=True)
    
    ### NAMES
    name_fr = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    
    ### STATS
    stat_hp  = models.IntegerField()
    stat_atq = models.IntegerField()
    stat_def = models.IntegerField()
    stat_spa = models.IntegerField()
    stat_spd = models.IntegerField()
    stat_spe = models.IntegerField()
    stat_sum = models.IntegerField()
    
    ### TYPES
    TYPE_CHOICES = [
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
        ('vol', 'vol'),
        ('na', 'na'),
    ]
    type_1 = models.CharField(choices=TYPE_CHOICES, default='na', max_length=50)
    type_2 = models.CharField(choices=TYPE_CHOICES, default='na', max_length=50)
    
    ### IMAGES
    pokedex_img = ResizedImageField(storage=S3Boto3Storage(), force_format="WEBP", scale=0.5, quality=75, upload_to=upload_to_pokedex, blank=True)
    shiny_img = ResizedImageField(storage=S3Boto3Storage(), force_format="WEBP", quality=75, upload_to=upload_to_shiny, blank=True)
    
    def __str__(self):
        return ('#' + str(self.regional_number) + ' | ' + self.name_fr)
    
    @property
    def get_pokedex_url(self):
        if self.pokedex_img and hasattr(self.pokedex_img, 'url'):
            return self.pokedex_img
        else:
            return "/static/images/pokedex_img/0-unknown-pokedex.jpg"
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(str(self.national_number)+"-"+self.name_fr)
            
        return super(Pokemon, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ["regional_number"]
    
class ShinyHunter(models.Model):
    firebase_uid = models.CharField(max_length=255, unique=True)
    pkmn = models.ManyToManyField(Pokemon, related_name="shinyHunter")
    
    def __str__(self):
        return self.firebase_uid