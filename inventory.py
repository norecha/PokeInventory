import argparse
import logging
import json
import collections
from itertools import groupby

from pgoapi import PGoApi

from renamer import Renamer
from transfer import Transfer
from evolve import Evolve


class Inventory(object):
    def __init__(self):
        self.ITEM_LUCKY_EGG = 301
        self.config = None
        self.api = None
        self.logger = logging.getLogger(__name__)
        self.pokedex = {}
        self.pokemons = collections.OrderedDict()
        self.candies = {}
        self.lucky_egg_count = 0

    def init_config(self):
        self.logger.info("Initializing config...")
        parser = argparse.ArgumentParser()

        parser.add_argument("-a", "--auth", required=True, type=str)
        parser.add_argument("-u", "--username", type=str)
        parser.add_argument("-p", "--password", type=str)
        parser.add_argument("-t", "--token", type=str)
        parser.add_argument("-lat", "--latitude", required=True, type=float)
        parser.add_argument("-lon", "--longitude", required=True, type=float)
        parser.add_argument("-cp", "--mincp", type=int, default=1000, help="Min CP to keep regardless of IV"
                                                                           " during transfers. Default=1000")

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

    def get_inventory(self):
        self.logger.info("Getting pokemon list...")
        pokemon_list = []
        inventory = self.api.get_inventory()['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        for item in inventory:
            inventory_item_data = item['inventory_item_data']

            if not inventory_item_data:
                continue

            # pokemon
            if 'pokemon_data' in inventory_item_data:
                pokemon = inventory_item_data['pokemon_data']

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
            if 'candy' in inventory_item_data:
                candy = inventory_item_data['candy']
                self.candies[candy['family_id']] = candy.get('candy', 0)

            # lucky egg
            if 'item' in inventory_item_data and inventory_item_data['item']['item_id'] == self.ITEM_LUCKY_EGG:
                self.lucky_egg_count = inventory_item_data['item'].get('count', 0)

        # group by name and sort by iv
        pokemon_list = sorted(pokemon_list, key=lambda p: p['name'])
        for k, g in groupby(pokemon_list, key=lambda p: p['name']):
            self.pokemons[k] = sorted(g, key=lambda p: p['iv'], reverse=True)

    def print_pokemons(self, pokemon_list):
        print()
        for k, g in pokemon_list.items():
            for poke in g:
                print("%s %.2f%% (%s,%s,%s) CP-%s %s" % (poke['name'], poke['iv'], poke['attack'], poke['defense'],
                                                         poke['stamina'], poke['cp'],
                                                         self.candies.get(poke['pid'], None)))
            print()

    @staticmethod
    def ask_question(msg):
        resp = input('\n%s (y/n) ' % msg).lower()
        if resp == 'y' or resp == 'yes':
            return True
        else:
            return False

    @staticmethod
    def get_min_to_keep(explanation=""):
        return int(input('How many pokemon you want to keep minimum?\n' +
                         explanation))

    def show_menu(self):
        print()
        print('  MAIN MENU')
        print('  ---------')
        print('  1: View Pokemon List')
        print('  2: Transfer Menu')
        print('  3: Evolve Menu')
        print('  4: Rename Menu')
        print('  0: Exit')
        choice = int(input("\nEnter choice: "))
        if choice == 1:
            self.print_pokemons(self.pokemons)
        elif choice == 2:
            Transfer(self).run()
        elif choice == 3:
            Evolve(self).run()
        elif choice == 4:
            Renamer(self).run()
        elif choice == 0:
            quit()
        else:
            quit()

    def run(self):
        self.init_config()
        self.init_api()
        self.get_inventory()
        while True:
            self.show_menu()


if __name__ == '__main__':
    Inventory().run()
