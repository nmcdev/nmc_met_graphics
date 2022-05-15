## Brian Blaylock
# April 10, 2021

"""
==================
Sesame Street Gang
==================

Primarily helping me learn how to build and use python classes.

Style Guide 2001
https://muppet.fandom.com/wiki/Sesame_Street_style_guide_(2001)
"""

import matplotlib.pyplot as plt


class character:
    def __init__(self, name, catch_phrase=""):
        self.name = name
        self.catch_phrase = catch_phrase
        self.colors = {}
        self.friends = {}

    def __repr__(self):
        """Representation in Notebook"""
        return self.greeting()

    def __str__(self):
        """When class object is printed"""
        msg = [
            f"{self.name=}",
            f"{self.catch_phrase=}",
            f"{self.colors=}",
            f"{self.friends=}",
        ]
        return "\n".join(msg)

    def greeting(self):
        return f"My name is {self.name}. {self.catch_phrase}"

    def add_color(self, part, color):
        self.colors[part] = color

    def add_friend(self, name, description):
        self.friends[name] = description

    def show_colors(self):
        plt.figure(figsize=[2, len(self.colors)])

        for i, (name, color) in enumerate(self.colors.items()):
            if color.upper() == "#FFFFFF":
                txt_color = ".5"
            else:
                txt_color = "w"
            plt.text(
                0,
                i,
                f"{name:^18}",
                va="center",
                fontsize=15,
                fontfamily="monospace",
                color=txt_color,
                fontweight="bold",
                bbox=dict(color=color, boxstyle="round"),
            )
            plt.scatter(0, i, color=color, s=1000, clip_on=False, ec="k")

        plt.title(f"{self.name}'s Colors")
        plt.gca().axis("off")
        plt.tight_layout()


################
# Pantone Colors

P021C = "#FE5000"  # Orange 2
P032C = "#EF3340"  # Red
P109C = "#FFD100"  # Yellow
P116C = "#FFCD00"  # Yellow 2
P122C = "#FED141"  # Yellow
P130C = "#F2A900"  # Orange
P143C = "#F1B434"  # Yellow
P144C = "#ED8B00"  # Orange
P145C = "#CF7F00"  # Light Brown
P150C = "#FFB25B"  # Light Orange
P151C = "#FF8200"  # Light Orange
P165C = "#FF6720"  # Orange
P167C = "#BE531C"  # Brown
P172C = "#FA4616"  # Orange 3
P185C = "#E4002B"  # Red
P210C = "#F99FC9"  # Pink 2
P211C = "#F57EB6"  # Pink
P212C = "#F04E98"  # Pink
P219C = "#DA1984"  # Pink
P239C = "#DB3EB1"  # Dark Pink
P251C = "#DD9CDF"  # Pink
P252C = "#C964CF"  # Pink
P265C = "#9063CD"  # Purple
P279C = "#418FDE"  # Blue 3
P285C = "#0072CE"  # Blue
P291C = "#9BCBEB"  # Light Blue
P293C = "#003DA5"  # Blue 2
P305C = "#59CBE8"  # Blue
P333C = "#3CDBC0"  # Sea Green
P348C = "#00843D"  # Green
P361C = "#43B02A"  # Green
P375C = "#97D700"  # Light Green
P376C = "#84BD00"  # Green
P430C = "#7C878E"  # Gray
P432C = "#333F48"  # Dark Gray
P529C = "#CAA2DD"  # Purple
P2925C = "#009CDE"  # Blue
P2995C = "#00A9E0"  # Blue
PBLUE = "#0085CA"  # Blue
PWarmRedC = "#F9423A"  # Red
PReflexBlue = "#001489"  # Blue
PYELLOW = "#FEDD00"  # Yellow
BLACK = "#000000"  # Black
WHITE = "#FFFFFF"  # White
WarmGray2 = "#CBC4BC"  # Light Gray
WarmGray3 = "#BFB8AF"
CoolGray5 = "#B1B3B3"  # Gray
CoolGray3 = "#C8C9C7"  # Gray

###########################
# Seasame Street Characters

bigBird = character("Big Bird", "I'm happy to be me!")
bigBird.add_friend("Radar", "Teddy Bear")
bigBird.add_color("body", P109C)
bigBird.add_color("mouth", P185C)
bigBird.add_color("tongue", P212C)
bigBird.add_color("leg stripe", P212C)
bigBird.add_color("eyelid", P212C)
bigBird.add_color("eyelash", PBLUE)
bigBird.add_color("legs", P165C)

radar = character("Radar", "")
radar.add_color("body", P167C)
radar.add_color("face", P145C)
radar.add_color("bandanna", P185C)

ernie = character("Ernie", "")
ernie.add_friend("Rubber Duckie", "Duck")
ernie.add_color("body", P151C)
ernie.add_color("tongue", P212C)
ernie.add_color("hair", BLACK)
ernie.add_color("nose", P185C)
ernie.add_color("mouth", P185C)
ernie.add_color("shirt1", P293C)
ernie.add_color("shirt2", WHITE)
ernie.add_color("shirt3", P185C)
ernie.add_color("shirt4", P109C)
ernie.add_color("collar, cuffs", P116C)
ernie.add_color("pants", P279C)
ernie.add_color("shoes1", WHITE)
ernie.add_color("shoes2", P185C)

rubberDucky = character("Rubber Duckie", "*squeak!*")
rubberDucky.add_color("body", P109C)
rubberDucky.add_color("beak", P021C)
rubberDucky.add_color("mouth", P185C)
rubberDucky.add_color("tongue", P210C)

bert = character("Bert", "What to see my paper clip collection?")
bert.add_friend("Bernice", "pigeon")
bert.add_color("body", P109C)
bert.add_color("hair", BLACK)
bert.add_color("nose", P151C)
bert.add_color("mouth", P185C)
bert.add_color("tongue", P212C)
bert.add_color("shirt1", P172C)
bert.add_color("shirt3", P293C)
bert.add_color("shirt3", P375C)
bert.add_color("pants", P361C)
bert.add_color("shoes1", WHITE)
bert.add_color("shoes2", P167C)

bernice = character("Bernice")
bernice.add_color("body", P2925C)
bernice.add_color("wing, neck, collar", P291C)
bernice.add_color("beak, feet", P151C)

cookieMonster = character(
    "Cookie Monter", "C is for Cookie, that's good enough for me."
)
cookieMonster.add_color("body", PBLUE)
cookieMonster.add_color("mouth", BLACK)
cookieMonster.add_color("cookie", P145C)

count = character("Count Von Count", "Three! Three buttons on my coat. Ah, Ah, Ahaa!")
count.add_color("body", P529C)
count.add_color("tongue", P212C)
count.add_color("mouth", BLACK)
count.add_color("cape exterior", P348C)
count.add_color("cape interior", P239C)
count.add_color("chest ribbon1", P185C)
count.add_color("chest ribbon2", P116C)
count.add_color("shirt", WHITE)
count.add_color("tuxedo", P432C)
count.add_color("spats", WarmGray2)
count.add_color("lapel, cumberbund", P430C)

elmo = character("Elmo", "Elmo is so happy to see you!")
elmo.add_friend("Dorthy", "Goldfish")
elmo.add_friend("David", "Monster Toy")
elmo.add_friend("Mr.Noodle", "Human")
elmo.add_color("body", P032C)
elmo.add_color("mouth", BLACK)
elmo.add_color("nose", P151C)

dorthy = character("Dorthy", "...")
dorthy.add_color("body", P151C)
dorthy.add_color("fins", PYELLOW)
dorthy.add_color("outline", P032C)
dorthy.add_color("water", P2995C)

david = character("David")
david.add_color("body", P150C)
david.add_color("mouth", P185C)
david.add_color("shirt1", P185C)
david.add_color("shirt2", P122C)
david.add_color("shirt3", P252C)
david.add_color("nose", P252C)

grover = character("Grover", "Hello Everybodeeeeeeeee!")
grover.alter_ego = "Super Grover"
grover.add_color("body", P285C)
grover.add_color("nose", P212C)
grover.add_color("lip", P185C)
grover.add_color("mouth", BLACK)
grover.add_color("super suite1", CoolGray5)
grover.add_color("super suite2", CoolGray3)
grover.add_color("super suite3", P291C)
grover.add_color("super suite4", P143C)
grover.add_color("super suite5", PBLUE)

oscar = character("Oscar the Grouch", "Scram!!")
oscar.add_friend("Slimey", "worm")
oscar.add_color("body", P376C)
oscar.add_color("tongue", PWarmRedC)
oscar.add_color("eyebrows", P167C)
oscar.add_color("mouth", BLACK)
oscar.add_color("garbage can", WarmGray3)

slimey = character("Slimey", "...")
slimey.add_color("body", P151C)
slimey.add_color("stripes", P109C)

rosita = character("Rosita", "Hola!")
rosita.add_color("body", P333C)
rosita.add_color("eyelids", P251C)
rosita.add_color("eyelashes", P144C)
rosita.add_color("mouth", BLACK)
rosita.add_color("nose", P151C)
rosita.add_color("bow", P109C)

zoe = character("Zoe")
zoe.add_friend("Mimi", "doll")
zoe.add_color("body", P143C)
zoe.add_color("eyelids", P333C)
zoe.add_color("eyelashes", P145C)
zoe.add_color("nose", P211C)
zoe.add_color("mouth", P185C)
zoe.add_color("tongue", P211C)

mimi = character("Mimi")
mimi.add_color("body", P305C)
mimi.add_color("hair", P130C)
mimi.add_color("eyelids", P144C)
mimi.add_color("mouth", P032C)
mimi.add_color("dress", P265C)
mimi.add_color("pants", P219C)
mimi.add_color("shoes", PReflexBlue)


class gang:
    characters = [
        bigBird,
        ernie,
        bert,
        cookieMonster,
        count,
        elmo,
        grover,
        oscar,
        rosita,
        zoe,
    ][::-1]

    def __init__(self, characters=characters):
        self.characters = characters

    def get_colors(self, part="body"):
        cdict = {}
        for i in self.characters:
            cdict[i.name] = i.colors.get(part, None)
        return cdict

    def show_colors(self, part="body"):
        plt.figure(figsize=[2, 6])

        for i, (name, color) in enumerate(self.get_colors(part=part).items()):

            if color is not None:
                plt.scatter(0, i, color=color, s=1000, clip_on=False)
                plt.text(
                    0,
                    i,
                    f"{name:^18}",
                    va="center",
                    fontsize=15,
                    fontfamily="monospace",
                    color="w",
                    fontweight="bold",
                    bbox=dict(color=color, boxstyle="round"),
                )
            else:
                plt.text(
                    0,
                    i,
                    f"{name:^18}",
                    va="center",
                    fontsize=15,
                    fontfamily="monospace",
                    color=".8",
                    fontweight="bold",
                )

        plt.title(f"{part.capitalize()} Color")
        plt.gca().axis("off")
        plt.tight_layout()
