"""
Project 11 : Virtual Pet Simulator
Concepts   : OOP, Dictionaries, Loops, Conditional Logic, File I/O

How it works
------------
* The user adopts a pet (name + type).
* The pet has 4 stats (0-100): Hunger, Happiness, Energy, Health.
      Hunger  : 100 = full stomach, 0 = starving
* Every action the user performs = 1 turn. After each turn all stats
  decrease automatically (Pet.pass_turn).
* Neglect has consequences: starving / exhausted / miserable pets lose Health.
  If Health reaches 0 the pet dies.
* Pet state is saved to a JSON file so progress continues next session.
"""

import json
import os

# ----------------------------------------------------------------------
# 1. CONSTANTS AND DICTIONARIES
# ----------------------------------------------------------------------
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet_save.json")

# Each pet type has its own rate of stat loss per turn (dictionary of dictionaries)
PET_TYPES = {
    "dog":    {"hunger": 8, "happiness": 7, "energy": 5},   # needs lots of play
    "cat":    {"hunger": 6, "happiness": 4, "energy": 4},   # independent
    "rabbit": {"hunger": 9, "happiness": 5, "energy": 6},   # hungry & sleepy
}

# Effect of every action on the stats (positive = increase, negative = decrease)
ACTIONS = {
    "feed":  {"hunger": +30, "happiness": +3,  "energy": 0,   "health": +2},
    "play":  {"hunger": -10, "happiness": +25, "energy": -20, "health": 0},
    "sleep": {"hunger": -8,  "happiness": 0,   "energy": +40, "health": +3},
    "vet":   {"hunger": 0,   "happiness": -10, "energy": 0,   "health": +35},
}

STAT_NAMES = ["hunger", "happiness", "energy", "health"]


# ----------------------------------------------------------------------
# 2. THE PET CLASS (Object-Oriented Programming)
# ----------------------------------------------------------------------
class Pet:
    """Represents one virtual pet and everything it can do."""

    def __init__(self, name, pet_type):
        self.name = name
        self.pet_type = pet_type
        self.age = 0                      # number of turns survived
        # Stats are kept in a dictionary -> easy to loop over and save
        self.stats = {"hunger": 80, "happiness": 80, "energy": 80, "health": 100}

    # ---------- helper ----------
    def change_stat(self, stat, amount):
        """Add 'amount' to a stat and keep it inside the range 0-100."""
        self.stats[stat] = max(0, min(100, self.stats[stat] + amount))

    def apply_action(self, action):
        """Apply the effects listed in the ACTIONS dictionary."""
        for stat, amount in ACTIONS[action].items():
            self.change_stat(stat, amount)

    # ---------- the four user actions ----------
    def feed(self):
        if self.stats["hunger"] >= 95:
            print(f"{self.name} is not hungry and refuses the food.")
            return
        self.apply_action("feed")
        print(f"You fed {self.name}. Yum!")

    def play(self):
        if self.stats["energy"] < 15:
            print(f"{self.name} is too tired to play. Let it sleep first!")
            self.change_stat("happiness", -5)   # pet is annoyed
            return
        self.apply_action("play")
        print(f"You played with {self.name}. What fun!")

    def sleep(self):
        self.apply_action("sleep")
        print(f"{self.name} took a nice nap. Zzz...")

    def visit_vet(self):
        self.apply_action("vet")
        print(f"The vet checked {self.name}. Health improved (but vets are scary!).")

    # ---------- automatic changes every turn ----------
    def pass_turn(self):
        """Stats decrease automatically. Neglect damages health."""
        self.age += 1
        rates = PET_TYPES[self.pet_type]
        for stat, loss in rates.items():
            self.change_stat(stat, -loss)

        # Realistic consequences of neglect
        if self.stats["hunger"] == 0:
            self.change_stat("health", -15)
            print(f"!! {self.name} is starving and losing health!")
        if self.stats["energy"] == 0:
            self.change_stat("health", -10)
            print(f"!! {self.name} is exhausted and losing health!")
        if self.stats["happiness"] == 0:
            self.change_stat("health", -5)
            print(f"!! {self.name} is depressed and losing health!")

    # ---------- mood and status ----------
    def get_mood(self):
        """Decide the mood from stat values (order of checks matters)."""
        s = self.stats
        if s["health"] < 30:
            return "sick"
        if s["hunger"] < 20 or s["energy"] < 20:
            return "angry"
        if s["happiness"] < 40:
            return "sad"
        return "happy"

    def is_alive(self):
        return self.stats["health"] > 0

    def show_status(self):
        print("\n" + "=" * 40)
        print(f" {self.name} the {self.pet_type}   (Age: {self.age} turns)")
        print("=" * 40)
        for stat in STAT_NAMES:
            value = self.stats[stat]
            bar = "#" * (value // 10) + "." * (10 - value // 10)
            print(f" {stat.capitalize():<10} [{bar}] {value:>3}")
        print(f" Mood       : {self.get_mood().upper()}")
        print("=" * 40)

    # ---------- converting to / from a dictionary for saving ----------
    def to_dict(self):
        return {"name": self.name, "pet_type": self.pet_type,
                "age": self.age, "stats": self.stats}

    @classmethod
    def from_dict(cls, data):
        pet = cls(data["name"], data["pet_type"])
        pet.age = data["age"]
        pet.stats = data["stats"]
        return pet


# ----------------------------------------------------------------------
# 3. FILE HANDLING (File I/O)
# ----------------------------------------------------------------------
def save_pet(pet):
    """Write the pet's data to a JSON file."""
    with open(SAVE_FILE, "w") as f:
        json.dump(pet.to_dict(), f, indent=4)


def load_pet():
    """Read the pet from the JSON file. Returns None if not possible."""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            return Pet.from_dict(json.load(f))
    except (json.JSONDecodeError, KeyError):
        print("Save file is damaged. Starting a new game.")
        return None


def delete_save():
    """Remove the save file (used when the pet dies)."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


# ----------------------------------------------------------------------
# 4. GAME SET-UP AND MENU
# ----------------------------------------------------------------------
def create_pet():
    """Ask the user to name and choose a pet type."""
    print("\n--- Adopt a new pet ---")
    name = ""
    while name.strip() == "":                       # loop until a name is given
        name = input("Give your pet a name: ")
    print("Choose a pet type:", ", ".join(PET_TYPES))
    pet_type = ""
    while pet_type not in PET_TYPES:                # loop until valid type
        pet_type = input("Pet type: ").strip().lower()
    print(f"\nCongratulations! You adopted {name.strip()} the {pet_type}!")
    return Pet(name.strip(), pet_type)


def show_menu():
    print("\nWhat do you want to do?")
    print(" 1. Feed")
    print(" 2. Play")
    print(" 3. Sleep")
    print(" 4. Visit Vet")
    print(" 5. Save and Quit")


def game_loop(pet):
    """Main loop: show status -> take action -> pass turn -> save."""
    while pet.is_alive():
        pet.show_status()
        show_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            pet.feed()
        elif choice == "2":
            pet.play()
        elif choice == "3":
            pet.sleep()
        elif choice == "4":
            pet.visit_vet()
        elif choice == "5":
            save_pet(pet)
            print("Game saved. See you soon!")
            return
        else:
            print("Invalid choice, try again.")
            continue                                 # invalid input = no turn used

        pet.pass_turn()                              # stats decrease automatically
        save_pet(pet)                                # autosave every turn

    # Loop ended because health reached 0
    pet.show_status()
    print(f"\n{pet.name} has passed away after {pet.age} turns. "
          "Neglect has consequences...")
    delete_save()


def main():
    print("*** VIRTUAL PET SIMULATOR ***")
    pet = load_pet()
    if pet is not None:
        answer = input(f"Saved pet found: {pet.name} the {pet.pet_type}. "
                       "Continue? (y/n): ").strip().lower()
        if answer != "y":
            pet = create_pet()
    else:
        pet = create_pet()
    game_loop(pet)


if __name__ == "__main__":
    main()
