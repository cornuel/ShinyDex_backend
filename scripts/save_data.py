from base.models import Pokemon
import csv


def run():
        Pokemon.objects.all().save()
