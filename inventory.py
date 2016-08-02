import argparse
import logging
import json
import collections
from itertools import groupby

from pgoapi import PGoApi

from transfer import Transfer


class Inventory(object):
    def __init__(self):
        self.config = None
        self.api = None
        self.logger = logging.getLogger(__name__)
        self.pokedex = {}
        self.pokemons = collections.OrderedDict()
        self.candies = {}

    def init_config(self):
        self.logger.info("Initializing config...")
        parser = argparse.ArgumentParser()

        parser.add_argument("-a", "--auth", required=True, type=str)
        parser.add_argument("-u", "--username", type=str)
        parser.add_argument("-p", "--password", type=str)
        parser.add_argument("-t", "--token", type=str)
        parser.add_argument("-lat", "--latitude", required=True, type=float)
        parser.add_argument("-lon", "--longitude", required=True, type=float)

        self.config = parser.parse_args()

        if not (self.config.username and self.config.password) and not self.config.token:
            raise Exception("(username and password) or token is required")

        pokedex = json.load(open('pokedex.json'))
        for poke in pokedex:
            self.pokedex[int(poke['Number'])] = {
                "name": poke['Name'],
                "candy": poke.get('Next Evolution Requirements', {}).get('Amount', None)
            }

    def init_api(self):
        self.logger.info("Initializing api...")
        self.api = PGoApi()

        self.api.login(self.config.auth, self.config.username, self.config.password, self.config.latitude,
                       self.config.longitude, 10, app_simulation=False)

    def get_pokemons(self):
        self.logger.info("Getting pokemon list...")
        pokemon_list = []
        inventory = self.api.get_inventory()['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        for item in inventory:
            # pokemon
            if 'inventory_item_data' in item and 'pokemon_data' in item['inventory_item_data']:
                pokemon = item['inventory_item_data']['pokemon_data']

                if 'is_egg' in pokemon and pokemon['is_egg']:
                    continue

                id = pokemon['id']
                pid = pokemon['pokemon_id']
                name = self.pokedex[pid]['name']

                attack = pokemon.get('individual_attack', 0)
                defense = pokemon.get('individual_defense', 0)
                stamina = pokemon.get('individual_stamina', 0)
                iv_percent = (float(attack + defense + stamina) / 45.0) * 100.0

                nickname = pokemon.get('nickname', None)
                combat_power = pokemon.get('cp', 0)

                pokemon_list.append({
                    'id': id,
                    'pid': pid,
                    'name': name,
                    'nickname': nickname,
                    'cp': combat_power,
                    'attack': attack,
                    'defense': defense,
                    'stamina': stamina,
                    'iv': iv_percent
                })

            # candy
            if 'inventory_item_data' in item and 'candy' in item['inventory_item_data']:
                candy = item['inventory_item_data']['candy']
                self.candies[candy['family_id']] = candy['candy']

        # group by name and sort by iv
        pokemon_list = sorted(pokemon_list, key=lambda p: p['name'])
        for k, g in groupby(pokemon_list, key=lambda p: p['name']):
            self.pokemons[k] = sorted(g, key=lambda p: p['iv'], reverse=True)

    def print_pokemons(self, pokemon_list):
        print()
        for k, g in pokemon_list.items():
            for poke in g:
                print("%s %.2f%% (%s,%s,%s) CP %s %s" % (poke['name'], poke['iv'], poke['attack'], poke['defense'],
                                                         poke['stamina'], poke['cp'],
                                                         self.candies.get(poke['pid'], None)))
            print()

    def show_menu(self):
        print()
        print('  MAIN MENU')
        print('  ---------')
        print('  1: View Pokemon List')
        print('  2: Transfer Menu')
        print('  3: Evolve Menu')
        print('  0: Exit')
        choice = int(input("\nEnter choice: "))
        if choice == 1:
            self.print_pokemons(self.pokemons)
        elif choice == 2:
            Transfer(self).run()
        elif choice == 3:
            pass
        elif choice == 0:
            quit()
        else:
            quit()

    def run(self):
        self.init_config()
        self.init_api()
        self.get_pokemons()
        while True:
            self.show_menu()


if __name__ == '__main__':
    Inventory().run()
