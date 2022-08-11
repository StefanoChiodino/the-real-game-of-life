import dataclasses
import datetime
import math
import random

from typing import List, Tuple

import pyxel

DEBUG_TIMINGS = False
DEBUG_LIFE_AND_DEATH = False

REPRODUCTION_MIN_AGE = 100

SCREEN_SIZE_X = 80
SCREEN_SIZE_Y = 80

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
                    x=float(random.randint(0, SCREEN_SIZE_X - 1)),
                    y=float(random.randint(0, SCREEN_SIZE_Y - 1)),
                    direction=float(random.randint(0, 360 - 1)),
                )
                self.creatures.append(creature)
        self.foods: List[Tuple[int, int]] = []
        for _ in range(200):
            self.spawn_food()

        pyxel.init(SCREEN_SIZE_X, SCREEN_SIZE_Y, title="The Real Game of Life", quit_key=pyxel.KEY_Q)
        pyxel.run(self.update, self.draw)

    def spawn_food(self):
        new_food: Tuple[int, int] = random.randint(0, SCREEN_SIZE_X - 1), random.randint(0, SCREEN_SIZE_Y - 1)
        while new_food in self.foods:
            new_food: Tuple[int, int] = random.randint(0, SCREEN_SIZE_X - 1), random.randint(0, SCREEN_SIZE_Y - 1)
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
        creature.x = min(creature.x, SCREEN_SIZE_X - 1)
        creature.y = min(creature.y, SCREEN_SIZE_Y - 1)

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
        return creature.starvation + COST_OF_REPRODUCTION < 1 and creature.age > REPRODUCTION_MIN_AGE

    def update(self):
        start = datetime.datetime.now()
        dead_creatures: List[Creature] = []
        for creature in self.creatures:
            self.update_creature(creature)
            if creature.starvation == 1 or creature.age >= MAX_AGE:
                dead_creatures.append(creature)
                if DEBUG_LIFE_AND_DEATH:
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
                        starvation=COST_OF_REPRODUCTION * 2,
                    )
                    new_creatures.append(new_creature)
                    creature.starvation += COST_OF_REPRODUCTION
                    other_creature.starvation += COST_OF_REPRODUCTION
        self.creatures += new_creatures

        if DEBUG_LIFE_AND_DEATH and new_creatures:
            print(f"new creatures: {len(new_creatures)}")

        if random.randint(0, 99) > 0:
            self.spawn_food()
        if DEBUG_TIMINGS:
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
        if DEBUG_TIMINGS:
            print(f"draw elapsed: {datetime.datetime.now() - start}")


App()
