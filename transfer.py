import logging
import random
import time
import math
import collections


class Transfer(object):
    def __init__(self, inventory):
        self.logger = logging.getLogger(__name__)
        self.inventory = inventory
        self.api = inventory.api
        self.pokemons = inventory.pokemons
        self.candies = inventory.candies
        self.pokedex = inventory.pokedex
        self.mincp = inventory.config.mincp

    def transfer_service(self, pokemon_id, name):
        print('Transferring %s... ' % name, end="")
        resp = self.api.release_pokemon(pokemon_id=pokemon_id)
        res = resp.get('responses', {}).get('RELEASE_POKEMON', {}).get('result', {0})
        if res == 1:
            print('DONE')
        else:
            print('FAILED')
        time.sleep(random.uniform(3.0, 6.0))

    def transfer_list(self, transfer_list):
        self.inventory.print_pokemons(transfer_list)
        if self.inventory.ask_question('Are you sure you want to transfer listed pokemons?'):
            for k, v in transfer_list.items():
                for p in v:
                    self.transfer_service(p['id'], k)
            self.inventory.get_inventory()

    def transfer_extras(self):
        transfer_list = collections.OrderedDict()
        min_keep = self.inventory.get_min_to_keep()
        can_evolve = 0
        for k, v in self.pokemons.items():
            count = len(v)
            pid = v[0]['pid']
            req_candies = self.pokedex[pid]['candy']
            my_candies = self.candies.get(pid, None)
            if not my_candies or not req_candies:
                continue
            can_evolve += my_candies // req_candies
            keeping = max(math.ceil(my_candies / req_candies), min_keep)

            if count > keeping:
                for poke in v[keeping:]:
                    if poke['cp'] < self.mincp:
                        transfer_list.setdefault(k, []).append(poke)

        if not transfer_list:
            print('\nNothing is available to transfer')
            return

        self.transfer_list(transfer_list)

    def transfer_duplicates(self):
        transfer_list = collections.OrderedDict()
        min_keep = max(0, self.inventory.get_min_to_keep())
        for k, v in self.pokemons.items():
            if len(v) > min_keep:
                for poke in v[min_keep:]:
                    if poke['cp'] < self.mincp:
                        transfer_list.setdefault(k, []).append(poke)
        self.transfer_list(transfer_list)

    def run(self):
        print('  TRANSFER MENU')
        print('  You will have a chance to approve the transfer list before actually transferring')
        print('  ---------')
        print('  1: Transfer all duplicates')
        print('  2: Transfer pokemons you cannot evolve(For example: If you have 36 pidgey candies, '
              'keep top 3; transfer the rest)')
        print('  0: Back')
        choice = int(input("\nEnter choice: "))
        if choice == 1:
            self.transfer_duplicates()
        elif choice == 2:
            self.transfer_extras()
        elif choice == 0:
            pass
        else:
            pass
