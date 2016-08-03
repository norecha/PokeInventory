import logging
import random
import time


class Renamer(object):
    def __init__(self, inventory):
        self.logger = logging.getLogger(__name__)
        self.inventory = inventory
        self.api = inventory.api
        self.pokemons = inventory.pokemons
        self.candies = inventory.candies
        self.pokedex = inventory.pokedex

    def rename_service(self, pokemon_id, nickname):
        print('Renaming %s... ' % nickname, end="")
        resp = self.api.nickname_pokemon(pokemon_id=pokemon_id, nickname=nickname)
        res = resp.get('responses', {}).get('NICKNAME_POKEMON', {}).get('result', {0})
        if res == 1:
            print('DONE')
        else:
            print('FAILED')
        time.sleep(random.uniform(3.0, 6.0))

    def rename(self, cutoff):
        for k, g in self.pokemons.items():
            for p in g:
                if p['iv'] >= cutoff and not p['nickname']:
                    nick = p['name'][:8] + "_" + str(int(p['iv']))
                    self.rename_service(p['id'], nick)

    def run(self):
        cutoff = int(input('What is the cutoff IV% to rename? '))
        self.rename(cutoff)
