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

    def transfer(self, pokemon_id, name):
        print('Transferring %s' % name)
        self.api.release_pokemon(pokemon_id=pokemon_id)
        time.sleep(random.uniform(3.0, 6.0))

    def transfer_extras(self):
        transfer_list = collections.OrderedDict()
        min_keep = self.get_min_to_keep()
        can_evolve = 0
        for k, v in self.pokemons.items():
            count = len(v)
            pid = v[0]['pid']
            req_candies = self.pokedex[pid]['candy']
            my_candies = self.candies.get(pid, None)
            if not my_candies or not req_candies:
                continue
            can_evolve += my_candies // req_candies
            print('You can evolve %d %s(s)' % (my_candies // req_candies, k))
            keeping = max(math.ceil(my_candies / req_candies), min_keep)

            if count > keeping:
                print('Going to transfer %d %s(s)' % (count - keeping, k))
                transfer_list[k] = v[keeping:]

        print('\nYou can evolve %d pokemons' % can_evolve)
        if not transfer_list:
            print('\nNothing is available to transfer')
            return

        self.inventory.print_pokemons(transfer_list)
        if Transfer.are_you_sure('transfer listed pokemons'):
            for k, v in transfer_list.items():
                for p in v:
                    self.transfer(p['id'], k)
            self.inventory.get_pokemons()

    @staticmethod
    def get_min_to_keep():
        return int(input('How many pokemon you want to keep minimum?\n' +
                         'For example: If you have 36 pidgey candies, normally you keep 3; transfer the rest.\n' +
                         'But if your minimum is 4, you will keep 4, transfer the rest:\n'))

    @staticmethod
    def are_you_sure(msg):
        resp = input('\nAre you sure you want to %s? (y/n) ' % msg).lower()
        if resp == 'y' or resp == 'yes':
            return True
        else:
            return False

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
            pass
        elif choice == 2:
            self.transfer_extras()
        elif choice == 0:
            pass
        else:
            pass
