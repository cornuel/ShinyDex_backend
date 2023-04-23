from base.models import Pokemon
import csv
import os
from re import sub
from django.core.files import File
from storages.backends.s3boto3 import S3Boto3Storage
import boto3

s3 = boto3.client('s3')

def run():
    with open('data.csv') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        Pokemon.objects.all().delete()

        image_name = "/home/near/Script_load/pokedex/0-unknown-pokedex.png"
        for row in reader:
            # print(row)
            
            s3_url = f'https://shinyhuntclone.s3.eu-west-3.amazonaws.com/images/pokedex_img/{row[2]}-{row[3]}-pokedex.webp'
            
            # get the path/directory
            folder_dir = '/home/near/Script_load/pokedex/'
            for image in os.listdir(folder_dir):
                # check if the image ends with png
                if (image.endswith(".png")):
                    if row[2] in image:
                        image_name=(folder_dir + image)
                        reopen = open(image_name, 'rb')
                        pokedex_file = File(reopen)

            pkmn = Pokemon(regional_number=row[1],
                national_number=row[2],
                name_fr=row[3],
                name_en=row[4],
                stat_hp=row[5],
                stat_atq=row[6],
                stat_def=row[7],
                stat_spa=row[8],
                stat_spd=row[9],
                stat_spe=row[10],
                stat_sum=row[11],
                type_1=row[12],
                type_2=row[13],
                pokedex_img=s3_url,
            )
            pkmn.save()
