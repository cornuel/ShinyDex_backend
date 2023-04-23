import json
import os
import csv

def create_pokemon_json():
    """
    Reads data from a CSV file and converts it into a list of Pokemon dictionaries.
    The dictionaries contain information about the Pokemon such as regional number,
    national number, name (in French and English), image URL, and various stats.
    The function then writes the list of dictionaries to a JSON file.
    """
    
    # Open the CSV file
    with open('data.csv') as file:
        # Create a CSV reader
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        # Create an empty list to store the Pokemon data
        pokemon_list = []

        # Loop through each row in the CSV file
        for row in reader:
            # Get the image URL
            s3_url = f'https://shinyhuntclone.s3.eu-west-3.amazonaws.com/images/pokedex_img/{row[2]}-{row[3]}-pokedex.webp'

            # Create a dictionary with the Pokemon data
            pokemon = {
                'regional_number': int(row[1]),
                'national_number': int(row[2]),
                'name_fr': row[3],
                'name_en': row[4],
                'pokedex_img': s3_url,
                'stat_hp': int(row[5]),
                'stat_atq': int(row[6]),
                'stat_def': int(row[7]),
                'stat_spa': int(row[8]),
                'stat_spd': int(row[9]),
                'stat_spe': int(row[10]),
                'stat_sum': int(row[11]),
                'type_1': row[12],
                'type_2': row[13],
            }

            # Add the Pokemon data to the list
            pokemon_list.append(pokemon)

    # Write the Pokemon data to a JSON file
    with open('pokemon.json', 'w') as file:
        json.dump(pokemon_list, file)
        
create_pokemon_json()