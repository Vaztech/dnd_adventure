from dataclasses import dataclass
from typing import List, Dict, Optional, Union
import json
from pathlib import Path

@dataclass
class MonsterAttack:
    name: str
    attack_bonus: int
    damage: str
    damage_type: str
    special: Optional[str] = None
    range: Optional[str] = None

@dataclass
class MonsterAbility:
    name: str
    description: str
    dc: Optional[int] = None
    uses: Optional[str] = None

@dataclass
class Monster:
    name: str
    challenge_rating: float
    size: str
    type: str
    subtype: Optional[str] = None
    hit_dice: str
    initiative: int
    speed: str
    armor_class: int
    touch_ac: int
    flat_footed_ac: int
    base_attack: int
    grapple: int
    attacks: List[MonsterAttack]
    full_attack: str
    space: str
    reach: str
    special_qualities: List[str]
    saves: Dict[str, int]
    abilities: Dict[str, int]
    skills: Dict[str, int]
    feats: List[str]
    abilities_list: List[MonsterAbility]
    environment: str
    organization: str
    treasure: str
    alignment: str
    advancement: str
    level_adjustment: Optional[int] = None
    spell_like_abilities: Optional[Dict[str, str]] = None
    spells: Optional[List[str]] = None
    spell_dc: Optional[int] = None
    regeneration: Optional[int] = None
    damage_reduction: Optional[str] = None
    resistances: Optional[Dict[str, int]] = None
    immunities: Optional[List[str]] = None

def load_monsters_from_json():
    """Load all SRD monsters from JSON file with enhanced error handling"""
    monsters_path = Path(__file__).parent.parent / 'data' / 'srd_monsters.json'
    try:
        with open(monsters_path, 'r', encoding='utf-8') as f:
            monsters_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Monster data file not found at {monsters_path}")
    except json.JSONDecodeError:
        raise ValueError("Monster data file contains invalid JSON")

    monsters = {}
    for category, category_monsters in monsters_data.items():
        for name, data in category_monsters.items():
            try:
                attacks = [
                    MonsterAttack(
                        name=atk['name'],
                        attack_bonus=atk['attack_bonus'],
                        damage=atk['damage'],
                        damage_type=atk['damage_type'],
                        special=atk.get('special'),
                        range=atk.get('range')
                    ) for atk in data.get('attacks', [])
                ]
                
                abilities = [
                    MonsterAbility(
                        name=ab['name'],
                        description=ab['description'],
                        dc=ab.get('dc'),
                        uses=ab.get('uses')
                    ) for ab in data.get('abilities_list', [])
                ]
                
                monsters[name] = Monster(
                    name=name,
                    challenge_rating=data['challenge_rating'],
                    size=data['size'],
                    type=data['type'],
                    subtype=data.get('subtype'),
                    hit_dice=data['hit_dice'],
                    initiative=data['initiative'],
                    speed=data['speed'],
                    armor_class=data['armor_class'],
                    touch_ac=data.get('touch_ac', data['armor_class']),
                    flat_footed_ac=data.get('flat_footed_ac', data['armor_class']),
                    base_attack=data['base_attack'],
                    grapple=data.get('grapple', 
                                   data['base_attack'] + 
                                   (data['abilities']['STR'] - 10) // 2),
                    attacks=attacks,
                    full_attack=data.get('full_attack', ''),
                    space=data['space'],
                    reach=data['reach'],
                    special_qualities=data.get('special_qualities', []),
                    saves=data['saves'],
                    abilities=data['abilities'],
                    skills=data.get('skills', {}),
                    feats=data.get('feats', []),
                    abilities_list=abilities,
                    environment=data['environment'],
                    organization=data.get('organization', ''),
                    treasure=data.get('treasure', ''),
                    alignment=data['alignment'],
                    advancement=data.get('advancement', ''),
                    level_adjustment=data.get('level_adjustment'),
                    spell_like_abilities=data.get('spell_like_abilities'),
                    spells=data.get('spells'),
                    spell_dc=data.get('spell_dc'),
                    regeneration=data.get('regeneration'),
                    damage_reduction=data.get('damage_reduction'),
                    resistances=data.get('resistances'),
                    immunities=data.get('immunities')
                )
            except KeyError as e:
                raise ValueError(f"Missing required field {e} in monster {name}")

    return monsters

SRD_MONSTERS = load_monsters_from_json()

def get_monster(name: str) -> Optional[Monster]:
    """Case-insensitive monster lookup"""
    lower_name = name.lower()
    for monster_name, monster in SRD_MONSTERS.items():
        if monster_name.lower() == lower_name:
            return monster
    return None

def get_monsters_by_cr(max_cr: float) -> Dict[str, Monster]:
    """Filter monsters by challenge rating"""
    return {name: m for name, m in SRD_MONSTERS.items() 
            if m.challenge_rating <= max_cr}

def get_monsters_by_type(type_name: str) -> Dict[str, Monster]:
    """Filter monsters by type (e.g., 'Dragon', 'Undead')"""
    return {name: m for name, m in SRD_MONSTERS.items() 
            if m.type.lower() == type_name.lower()}