from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging
import random
from colorama import Fore, Style
from dnd_adventure.races import Race
from dnd_adventure.classes import DnDClass

logger = logging.getLogger(__name__)

def format_description_block(title: str, description: str, indent: int = 0) -> str:
    indentation = " " * indent
    lines = description.splitlines()
    formatted = f"{indentation}{title}:\n"
    for line in lines:
        formatted += f"{indentation}  {line}\n"
    return formatted.rstrip()

@dataclass
class ClassFeature:
    name: str
    level: int
    description: str

    @staticmethod
    def from_dict(data: Dict) -> 'ClassFeature':
        return ClassFeature(
            name=data.get("name", "Unknown Feature"),
            level=data.get("level", 1),
            description=data.get("description", "")
        )

@dataclass
class DnDClass:
    name: str
    hit_die: int
    base_attack_bonus: str
    saving_throws: Dict[str, str]
    skill_points: int
    class_skills: List[str]
    spellcasting: Optional[Dict] = None
    features: Optional[List[ClassFeature]] = None
    subclasses: Optional[Dict[str, Dict]] = None

    def bab_at_level(self, level: int) -> int:
        if self.base_attack_bonus == 'good':
            return level
        elif self.base_attack_bonus == 'average':
            return level * 3 // 4
        return level // 2

    def save_at_level(self, save_type: str, level: int) -> int:
        return 2 + level // 2 if self.saving_throws.get(save_type, 'poor') == 'good' else level // 3

    def handle_level_up(self, level: int, skills: Dict[str, int]) -> 'DnDClass':
        if level == 3 and self.subclasses:
            print(f"\n--- Level {level} reached: Choose your subclass for {self.name} ---")
            subclass_choice = self.choose_subclass(skills)
            if subclass_choice:
                print(f"Subclass chosen: {subclass_choice}")
                return DnDClass.from_dict(self.__dict__, subclass_name=subclass_choice)
        return self

    def choose_subclass(self, skills: Dict[str, int]) -> Optional[str]:
        if not self.subclasses:
            return None
        recommendation = self.recommend_subclass(skills)
        print(f"Available subclasses for {self.name}:")
        for i, sub in enumerate(self.subclasses.keys(), 1):
            subclass_data = self.subclasses[sub]
            description = subclass_data.get("description", "No description provided.")
            features = subclass_data.get("features", [])
            feature_desc = "\n".join(f"{f['name']}: {f['description']}" for f in features) if features else "No features."
            print(f"\n{Fore.YELLOW}[{i}] {sub}{Style.RESET_ALL}" + (" (Recommended)" if sub == recommendation else ""))
            print(format_description_block("Description", description, indent=4))
            if features:
                print(format_description_block("Features", feature_desc, indent=4))
        while True:
            try:
                choice = input(f"\nEnter subclass number [default: {recommendation}]: ").strip()
                if not choice:
                    return recommendation
                choice_idx = int(choice) - 1
                subclass_list = list(self.subclasses.keys())
                if 0 <= choice_idx < len(subclass_list):
                    return subclass_list[choice_idx]
                print(f"Please enter a number between 1 and {len(subclass_list)}.")
            except ValueError:
                print("Invalid input. Please enter a number or press Enter for the default.")

    def recommend_subclass(self, skills: Dict[str, int]) -> Optional[str]:
        if not self.subclasses or not skills:
            return None
        def score(sub):
            sub_skills = set(self.subclasses[sub].get("class_skills", []))
            return sum(skills.get(skill, 0) for skill in sub_skills)
        return max(self.subclasses.keys(), key=score, default=None)

    @staticmethod
    def from_dict(data: Dict, subclass_name: Optional[str] = None) -> 'DnDClass':
        features = [ClassFeature.from_dict(f) for f in data.get("features", [])]
        subclasses = data.get("subclasses")
        if subclass_name and subclasses and subclass_name in subclasses:
            subclass_data = subclasses[subclass_name]
            subclass_features = [ClassFeature.from_dict(f) for f in subclass_data.get("features", [])]
            combined_features = features + subclass_features
            return DnDClass(
                name=f"{data.get('name')} ({subclass_name})",
                hit_die=subclass_data.get("hit_die", data.get("hit_die", 8)),
                base_attack_bonus=subclass_data.get("base_attack_bonus", data.get("base_attack_bonus", "average")),
                saving_throws=subclass_data.get("saving_throws", data.get("saving_throws", {})),
                skill_points=subclass_data.get("skill_points", data.get("skill_points", 2)),
                class_skills=subclass_data.get("class_skills", data.get("class_skills", [])),
                spellcasting=subclass_data.get("spellcasting", data.get("spellcasting")),
                features=combined_features,
                subclasses=subclasses
            )
        return DnDClass(
            name=data.get("name", "Unknown"),
            hit_die=data.get("hit_die", 8),
            base_attack_bonus=data.get("base_attack_bonus", "average"),
            saving_throws=data.get("saving_throws", {}),
            skill_points=data.get("skill_points", 2),
            class_skills=data.get("class_skills", []),
            spellcasting=data.get("spellcasting"),
            features=features,
            subclasses=subclasses
        )

@dataclass
class Character:
    name: str
    race_name: str
    class_name: str
    level: int = 1
    xp: int = 0
    stats: List[int] = field(default_factory=list)
    skills: Dict[str, int] = field(default_factory=dict)
    feats: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=lambda: ["Leather Armor"])
    hit_points: int = 0
    skill_points: int = 0
    race: Optional[Race] = None
    dnd_class: Optional[DnDClass] = None
    armor_class: int = 10
    known_spells: Dict[int, List[str]] = field(default_factory=lambda: {0: [], 1: []})
    mp: int = 0
    max_mp: int = 0

    def __post_init__(self):
        self.dnd_class = self.dnd_class or get_class_by_name(self.class_name) or get_default_class()
        if self.stats and len(self.stats) == 6:
            stat_names = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
            logger.debug(f"Loading stats for {self.name}: {dict(zip(stat_names, self.stats))}")
            self.apply_racial_traits()
            self.calculate_mp()
            self.calculate_skill_points()
            self.calculate_hit_points()

    def get_stat_modifier(self, stat_index: int) -> int:
        stat_value = self.stats[stat_index] if stat_index < len(self.stats) else 10
        modifier = (stat_value - 10) // 2
        logger.debug(f"Calculated modifier for stat index {stat_index} (value: {stat_value}): {modifier}")
        return modifier

    def apply_racial_traits(self):
        if not self.race or not self.race_name:
            logger.warning(f"No race defined for {self.name}, skipping racial trait application")
            return
        dex_mod = self.get_stat_modifier(1)
        self.armor_class = 10 + dex_mod
        if self.race_name.startswith("Dwarf (Mountain Dwarf)"):
            self.armor_class = max(self.armor_class, 14 + min(dex_mod, 2))
            logger.debug(f"Applied Mountain Dwarf Armor Training for {self.name}: AC={self.armor_class}")

    def calculate_mp(self):
        if not self.dnd_class.spellcasting or self.dnd_class.spellcasting.get('type') not in ['arcane', 'divine']:
            logger.debug(f"No spellcasting for {self.name} ({self.class_name})")
            self.mp = 0
            self.max_mp = 0
            return
        primary_stat = {
            "Wizard": 3,  # INT
            "Sorcerer": 5,  # CHA
            "Cleric": 4,  # WIS
            "Druid": 4,  # WIS
            "Bard": 5  # CHA
        }
        stat_idx = primary_stat.get(self.class_name, 3)  # Default to INT
        stat_mod = self.get_stat_modifier(stat_idx)
        self.max_mp = max(0, (stat_mod * 2) + self.level + 4)
        self.mp = self.max_mp
        logger.debug(f"Calculated MP for {self.name}: stat_mod={stat_mod}, level={self.level}, max_mp={self.max_mp}, mp={self.mp}, known_spells={self.known_spells}")

    def cast_spell(self, spell_name: str, target: Optional['Character'] = None, enemy: Optional[object] = None) -> str:
        spell_level = None
        for level, spells in self.known_spells.items():
            if spell_name in spells:
                spell_level = level
                break
        if spell_level is None:
            logger.debug(f"Spell {spell_name} not known by {self.name}")
            return f"Cannot cast {spell_name}: not known."

        mp_cost = 1 if spell_level == 0 else 2
        if self.mp < mp_cost:
            logger.debug(f"Insufficient MP for {self.name} to cast {spell_name}: mp={self.mp}, cost={mp_cost}")
            return f"Not enough MP to cast {spell_name} (need {mp_cost}, have {self.mp})."

        self.mp -= mp_cost
        logger.info(f"{self.name} cast {spell_name}, MP reduced to {self.mp}/{self.max_mp}")

        if self.class_name == "Cleric":
            if spell_name == "Cure Light Wounds":
                if not target:
                    target = self
                healing = random.randint(1, 8) + self.level
                target.hit_points += healing
                logger.info(f"{self.name} cast Cure Light Wounds on {target.name}, healed {healing} HP (Total HP: {target.hit_points})")
                return f"Healed {target.name} for {healing} HP!"
            elif spell_name == "Bless":
                logger.info(f"{self.name} cast Bless, gaining +1 to attack rolls")
                return "Blessed, gaining +1 to attack rolls!"
            elif spell_name == "Light":
                logger.info(f"{self.name} cast Light, illuminating the area")
                return "Area illuminated!"
            elif spell_name == "Guidance":
                logger.info(f"{self.name} cast Guidance, gaining +1 to next attack")
                return "Gained +1 to next attack!"
            elif spell_name == "Cure Minor Wounds":
                if not target:
                    target = self
                target.hit_points += 1
                logger.info(f"{self.name} cast Cure Minor Wounds on {target.name}, healed 1 HP (Total HP: {target.hit_points})")
                return f"Healed {target.name} for 1 HP!"
            else:
                return f"Spell {spell_name} not implemented."
        elif self.class_name in ["Wizard", "Sorcerer"]:
            if spell_name == "Magic Missile" and enemy:
                damage = random.randint(1, 4) + 1
                enemy.hit_points -= damage
                logger.info(f"{self.name} cast Magic Missile, dealt {damage} damage to {enemy.name} (HP: {enemy.hit_points})")
                return f"Dealt {damage} damage to {enemy.name}!"
            elif spell_name == "Shield":
                self.armor_class += 4
                logger.info(f"{self.name} cast Shield, AC increased to {self.armor_class}")
                return f"AC increased by 4!"
            elif spell_name == "Daze" and enemy:
                stat_idx = 3 if self.class_name == "Wizard" else 5  # INT or CHA
                if random.randint(1, 20) + self.get_stat_modifier(stat_idx) >= 10:
                    logger.info(f"{self.name} cast Daze, {enemy.name} is stunned")
                    return f"{enemy.name} is stunned!"
                logger.info(f"{self.name} cast Daze, but {enemy.name} resists")
                return f"{enemy.name} resists Daze!"
            elif spell_name == "Mage Hand":
                logger.info(f"{self.name} cast Mage Hand, moved a small object")
                return "Moved a small object!"
            else:
                return f"Spell {spell_name} not implemented."
        else:
            return f"{self.class_name} cannot cast spells."

    def rest(self):
        self.mp = self.max_mp
        logger.info(f"{self.name} rested, MP restored to {self.mp}/{self.max_mp}")
        return f"{self.name} rests, restoring MP to {self.mp}/{self.max_mp}."

    def calculate_skill_points(self):
        int_modifier = self.get_stat_modifier(3)
        is_human = "Human" in self.race_name
        if self.level == 1:
            base_points = max(1, self.dnd_class.skill_points + int_modifier) * 4
            bonus = 4 if is_human else 0
            self.skill_points = base_points + bonus
            logger.debug(f"Level 1 skill points for {self.name}: class={self.dnd_class.skill_points}, Int mod={int_modifier}, base={base_points}, Human bonus={bonus}, Total={self.skill_points}")
        else:
            base_points = max(1, self.dnd_class.skill_points + int_modifier)
            bonus = 1 if is_human else 0
            self.skill_points += base_points + bonus
            logger.debug(f"Level {self.level} skill_points for {self.name}: class={self.dnd_class.skill_points}, Int mod={int_modifier}, base={base_points}, Human bonus={bonus}, Total={self.skill_points}")
        logger.info(f"{self.name} skill points updated: {self.skill_points}")

    def calculate_hit_points(self):
        con_modifier = self.get_stat_modifier(2)
        hit_die = 6 if self.class_name == "Wizard" else self.dnd_class.hit_die
        if self.level == 1:
            hp_gain = hit_die + con_modifier
            self.hit_points = max(1, hp_gain)
            logger.debug(f"Level 1 HP for {self.name}: max hit die (d{hit_die}) = {hit_die}, Con modifier = {con_modifier}, Total = {self.hit_points}")
        else:
            roll = random.randint(1, hit_die)
            hp_gain = max(1, roll + con_modifier)
            self.hit_points += hp_gain
            logger.debug(f"Level {self.level} HP for {self.name}: rolled d{hit_die} = {roll}, Con modifier = {con_modifier}, HP gain = {hp_gain}, Total = {self.hit_points}")
        logger.info(f"{self.name} HP updated: {self.hit_points}")
        print(f"{self.name} now has {self.hit_points} HP")

    def calculate_damage_output(self, weapon_die: int = 8) -> int:
        str_modifier = self.get_stat_modifier(0)
        weapon_roll = random.randint(1, weapon_die)
        damage = max(0, weapon_roll + str_modifier)
        logger.debug(f"Damage calculation for {self.name}: weapon roll (1d{weapon_die}) = {weapon_roll}, Str modifier = {str_modifier}, Total = {damage}")
        logger.info(f"{self.name} dealt {damage} damage")
        return damage

    def gain_xp(self, amount: int):
        logger.debug(f"{self.name} gaining {amount} XP (current: {self.xp})")
        self.xp += amount
        xp_threshold = self.level * 1000
        if self.xp >= xp_threshold:
            self.level_up()

    def level_up(self):
        self.level += 1
        logger.info(f"{self.name} has reached level {self.level}")
        print(f"{self.name} has reached level {self.level}!")
        self.dnd_class = self.dnd_class.handle_level_up(self.level, self.skills)
        self.class_name = self.dnd_class.name
        self.calculate_mp()
        self.calculate_skill_points()
        self.calculate_hit_points()

CORE_CLASSES: Dict[str, DnDClass] = {}

def get_default_class() -> DnDClass:
    return CORE_CLASSES.get("Fighter", DnDClass(
        name="Fighter",
        hit_die=10,
        base_attack_bonus="good",
        saving_throws={"Fort": "good", "Ref": "poor", "Will": "poor"},
        skill_points=2,
        class_skills=["Climb", "Handle Animal", "Intimidate", "Jump", "Ride"]
    ))

def get_class_by_name(name: str) -> Optional[DnDClass]:
    return CORE_CLASSES.get(name)

def get_all_classes() -> List[DnDClass]:
    return list(CORE_CLASSES.values())