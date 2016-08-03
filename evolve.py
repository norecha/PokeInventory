import time
import random
import logging
import collections


class Evolve(object):
    def __init__(self, inventory):
        self.logger = logging.getLogger(__name__)
        self.inventory = inventory
        self.api = inventory.api
        self.pokemons = inventory.pokemons
        self.candies = inventory.candies
        self.pokedex = inventory.pokedex

    def evolve_service(self, pokemon_id, name):
        print('Evolving %s... ' % name, end="")
        resp = self.api.evolve_pokemon(pokemon_id=pokemon_id)
        res = resp.get('responses', {}).get('EVOLVE_POKEMON', {}).get('result', {0})
        if res == 1:
            print('DONE')
        else:
            print('FAILED')
        time.sleep(random.uniform(3.0, 6.0))

    def evolve_all(self):
        evolve_list = collections.OrderedDict()
        min_keep = self.inventory.get_min_to_keep()
        will_evolve_total = 0
        for k, v in self.pokemons.items():
            count = len(v)
            pid = v[0]['pid']
            req_candies = self.pokedex[pid]['candy']
            my_candies = self.candies.get(pid, None)
            if not my_candies or not req_candies:
                continue
            can_evolve = my_candies // req_candies
            remaining_after_evolve = count - can_evolve
            will_remain = max(remaining_after_evolve, min(min_keep, count))
            will_evolve = count - will_remain
            will_evolve_total += will_evolve
            print('You will evolve %d %s(s)' % (will_evolve, k))

            if will_evolve > 0:
                evolve_list[k] = v[:will_evolve]

        print('\nYou can evolve %d pokemon(s)' % will_evolve_total)
        if not evolve_list:
            print('\nNothing is available to evolve')
            return

        self.inventory.print_pokemons(evolve_list)
        if self.inventory.ask_question('Are you sure you want to evolve listed pokemon(s) '
                                       '(if yes, you will have an option to use a lucky egg)'):
            self.ask_lucky_egg()

            for k, v in evolve_list.items():
                for p in v:
                    self.evolve_service(p['id'], k)

            self.inventory.get_inventory()

    def ask_lucky_egg(self):
        print('You have %d lucky egg(s)' % self.inventory.lucky_egg_count)
        if self.inventory.lucky_egg_count > 0 and self.inventory.ask_question('Do you want to use a lucky egg?'):
            try:
                resp = self.api.use_item_xp_boost(item_id=self.inventory.ITEM_LUCKY_EGG)
                res = resp.get('responses', {}).get('USE_ITEM_XP_BOOST', {}).get('result', {0})
                if res == 1:
                    print('Popped a lucky egg')
                else:
                    raise ValueError('Unable to use a lucky egg, try without it, maybe you already have one active')
            except Exception as e:
                print('Exception: Unable to use a lucky egg, try without it, maybe you already have one active')
                raise e

    def run(self):
        print('  EVOLVE MENU')
        print('  You will have a chance to approve the evolve list before actually evolving')
        print('  ---------')
        print('  1: Evolve everything available using minimum candy')
        print('  0: Back')
        choice = int(input("\nEnter choice: "))
        if choice == 1:
            self.evolve_all()
        elif choice == 0:
            pass
        else:
            pass
