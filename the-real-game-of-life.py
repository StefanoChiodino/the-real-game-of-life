import dataclasses
import datetime
import math
import random

from typing import List, Tuple

import pyxel

COST_OF_REPRODUCTION: float = 0.3
MAX_AGE: int = 1000
MIN_CREATURE_STARVATION_WILL_ACCEPT_FOOD: float = 0.3


@dataclasses.dataclass
class Specie:
    colour: int
    speed: float


@dataclasses.dataclass
class Creature:
    specie: Specie
    x: float
    y: float
    direction: float
    starvation: float = float(0)
    age: float = 0


class App:
    def __init__(self):
        pool_of_colours: List[int] = [
            pyxel.COLOR_BLACK,
            pyxel.COLOR_NAVY,
            pyxel.COLOR_PURPLE,
            # pyxel.COLOR_GREEN,
            pyxel.COLOR_BROWN,
            pyxel.COLOR_DARK_BLUE,
            pyxel.COLOR_LIGHT_BLUE,
            # pyxel.COLOR_WHITE,
            pyxel.COLOR_RED,
            pyxel.COLOR_ORANGE,
            pyxel.COLOR_YELLOW,
            pyxel.COLOR_LIME,
            pyxel.COLOR_CYAN,
            pyxel.COLOR_GRAY,
            pyxel.COLOR_PINK,
            pyxel.COLOR_PEACH,
        ]
        random.shuffle(pool_of_colours)
        self.creatures = []
        for _ in range(5):
            specie: Specie = Specie(colour=pool_of_colours.pop(), speed=random.randint(1, 5) / 5)
            for _ in range(20):
                creature = Creature(
                    specie,
                    x=float(random.randint(0, 119)),
                    y=float(random.randint(0, 119)),
                    direction=float(random.randint(0, 360)),
                )
                self.creatures.append(creature)
        self.foods: List[Tuple[int, int]] = []
        for _ in range(200):
            self.spawn_food()

        pyxel.init(120, 120, title="The Real Game of Life", quit_key=pyxel.KEY_Q)
        pyxel.run(self.update, self.draw)

    def spawn_food(self):
        new_food: Tuple[int, int] = random.randint(0, 119), random.randint(0, 119)
        while new_food in self.foods:
            new_food: Tuple[int, int] = random.randint(0, 119), random.randint(0, 119)
        self.foods.append(new_food)

    def update_creature(self, creature: Creature):
        # Direction.
        creature.direction += random.randint(-1, 1)
        creature.direction = (creature.direction + 360) % 360

        # Position
        creature.x += math.cos(creature.direction) * creature.specie.speed
        creature.y += math.sin(creature.direction) * creature.specie.speed
        creature.x = max(creature.x, 0)
        creature.y = max(creature.y, 0)
        creature.x = min(creature.x, 119)
        creature.y = min(creature.y, 119)

        # Food.
        creature.starvation += creature.specie.speed / 300
        if creature.starvation > MIN_CREATURE_STARVATION_WILL_ACCEPT_FOOD:
            for food in self.foods:
                if int(creature.x) == food[0] and int(creature.y) == food[1]:
                    self.foods.remove(food)
                    creature.starvation = 0
                    break

        # Age.
        creature.age += 1

    def can_reproduce(self, creature: Creature) -> bool:
        return creature.starvation + COST_OF_REPRODUCTION < 1 and creature.age > 100

    def update(self):
        start = datetime.datetime.now()
        dead_creatures: List[Creature] = []
        for creature in self.creatures:
            self.update_creature(creature)
            if creature.starvation == 1 or creature.age >= MAX_AGE:
                dead_creatures.append(creature)
                print(f"Dead because starvation: {creature.starvation == 1}, age: {creature.age >= MAX_AGE}")
        for dead_creature in dead_creatures:
            self.creatures.remove(dead_creature)

        # Mating.
        new_creatures: List[Creature] = []
        for i, creature in enumerate(self.creatures, start=1):
            for other_index in range(i, len(self.creatures)):
                other_creature: Creature = self.creatures[other_index]
                if (
                    creature.specie == other_creature.specie
                    and int(other_creature.x) == int(creature.x)
                    and int(other_creature.y) == int(creature.y)
                    and self.can_reproduce(creature)
                    and self.can_reproduce(other_creature)
                ):
                    new_creature: Creature = Creature(
                        creature.specie,
                        x=creature.x,
                        y=creature.y,
                        direction=float(random.randint(0, 360)),
                        starvation=0.5,
                    )
                    new_creatures.append(new_creature)
                    creature.starvation += COST_OF_REPRODUCTION
                    other_creature.starvation += COST_OF_REPRODUCTION
        self.creatures += new_creatures
        if new_creatures:
            print(f"new creatures: {len(new_creatures)}")

        if random.randint(0, 99) > 0:
            self.spawn_food()
        print(f"update elapsed: {datetime.datetime.now() - start}")

    def draw(self):
        start = datetime.datetime.now()
        pyxel.cls(pyxel.COLOR_GREEN)

        # Draw creatures.
        for creature in self.creatures:
            pyxel.rect(creature.x, creature.y, 1, 1, creature.specie.colour)

        # Draw number of creatures.
        pyxel.text(0, 0, f"{len(self.creatures)}", pyxel.COLOR_WHITE)

        # Draw food.
        for food in self.foods:
            pyxel.rect(food[0], food[1], 1, 1, pyxel.COLOR_WHITE)

        print(f"draw elapsed: {datetime.datetime.now() - start}")


App()
