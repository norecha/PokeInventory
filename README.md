# PokeInventory
There are many tools but I couldn't find a simple tool to mass transfer with respect to candies/evolutions. With this script you can:

- Transfer
  - Transfer all duplicates
  - Transfer pokemons you cannot evolve(For example: If you have 36 pidgey candies, keep top 3; transfer the rest)
    - It will only transfer pokemons at first evolution
- Evolve
  - (Pop a lucky egg optionally) Evolve everything you can
    - It will only evolve pokemons at first evolution
- Rename above certain IV
 
Note: When sorting pokemons of same type IV is prioritized over CP. You can optionally pass -cp argument to specify not to transfer anything above certain cp which is 1000 by default.

## Installation

### Requirements
- Python 3
- pip
- git

### Guide
```
git clone -b master https://github.com/norecha/PokeInventory.git
cd PokeInventory
pip install -r requirements.txt (Might need to sudo)
python inventory.py -a AUTH_SERVICE -u USERNAME -p PASSWORD -lat LAT -lon LON [-cp MINCP]

Help:
python inventory.py --help
```

## Credits
- [tejado](https://github.com/tejado) for the API
- [PokemonGO-IV-Renamer](https://github.com/Boren/PokemonGO-IV-Renamer) for base
