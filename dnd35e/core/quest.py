# quests.py

DND_35E_QUESTS = {
    "Adventure_Types": {
        "Dungeon_Crawl": {
            "The_Sunken_Citadel": {
                "name": "The Sunken Citadel",
                "level_range": "1-3",
                "hook": "Villagers report missing travelers near ancient ruins",
                "objectives": [
                    "Investigate the disappearances",
                    "Explore the ruined citadel",
                    "Stop the goblin cult's necromantic rituals"
                ],
                "key_locations": [
                    "Surface ruins (goblin ambush)",
                    "Flooded lower levels (undead)",
                    "Ritual chamber (boss fight)"
                ],
                "rewards": {
                    "gp": 500,
                    "items": ["+1 weapon", "Potion of Healing x3"],
                    "xp": 900
                },
                "source": "Dungeon #XXX"
            }
        },
        "Urban_Adventure": {
            "Shadows_of_the_City": {
                "name": "Shadows of the City",
                "level_range": "4-6",
                "hook": "Nobles are being blackmailed by a thieves' guild",
                "objectives": [
                    "Identify the blackmailers",
                    "Infiltrate the guild headquarters",
                    "Recover incriminating documents"
                ],
                "key_locations": [
                    "Noble district",
                    "Undercity tunnels",
                    "Guild safehouse"
                ],
                "rewards": {
                    "gp": 1200,
                    "items": ["Cloak of Resistance +1", "Thieves' Tools Masterwork"],
                    "xp": 1800
                },
                "source": "Cityscape"
            }
        }
    },
    "Quest_Archetypes": {
        "Rescue_Mission": {
            "template": {
                "name": "Rescue Mission Template",
                "variations": [
                    {
                        "hook": "Merchant's daughter kidnapped by bandits",
                        "complications": [
                            "Hostages have been moved to secondary location",
                            "Bandits have political connections"
                        ]
                    },
                    {
                        "hook": "Dwarven miners trapped in collapsed tunnel",
                        "complications": [
                            "Tunnel is now monster-infested",
                            "Limited time before air runs out"
                        ]
                    }
                ],
                "reward_scale": {
                    "low": "200 gp + minor magic item",
                    "medium": "500 gp + potions",
                    "high": "1000 gp + permanent magic item"
                },
                "source": "DMG p.XXX"
            }
        },
        "Artifact_Recovery": {
            "template": {
                "name": "Artifact Recovery Template",
                "variations": [
                    {
                        "hook": "Stolen holy relic must be reclaimed before holy day",
                        "complications": [
                            "Thieves don't know it's cursed",
                            "Temple rivals want it destroyed"
                        ]
                    },
                    {
                        "hook": "Lost wizard's staff holds key to stopping plague",
                        "complications": [
                            "Guarded by constructs",
                            "Multiple factions seek it"
                        ]
                    }
                ],
                "reward_scale": {
                    "low": "Access to restricted knowledge",
                    "medium": "Faction favor + gold",
                    "high": "Keep a secondary recovered item"
                },
                "source": "Complete Scoundrel"
            }
        }
    },
    "Campaign_Structures": {
        "The_Red_Hand": {
            "name": "The Red Hand of Doom",
            "level_range": "5-10",
            "phases": [
                {
                    "name": "Scouts and Skirmishes",
                    "quests": [
                        "Investigate hobgoblin patrols",
                        "Secure the bridge at Rhest"
                    ]
                },
                {
                    "name": "The March Begins",
                    "quests": [
                        "Defend Drellin's Ferry",
                        "Sabotage enemy siege weapons"
                    ]
                },
                {
                    "name": "Final Confrontation",
                    "quests": [
                        "Assault on the Fane of Tiamat",
                        "Battle of Brindol"
                    ]
                }
            ],
            "rewards": {
                "gp": 15000,
                "items": ["+2 armor/weapons", "Wondrous items"],
                "xp": 30000
            },
            "source": "Red Hand of Doom"
        }
    },
    "Random_Quest_Generator": {
        "Hooks": [
            "Local ruler needs deniable agents for...",
            "Scholar seeks protection while investigating...",
            "Unusual monster sightings at..."
        ],
        "Locations": [
            "Abandoned wizard's tower",
            "Underdark outpost",
            "Haunted graveyard"
        ],
        "Twists": [
            "Target is actually innocent",
            "Secondary faction intervenes",
            "Ancient defense mechanisms activate"
        ],
        "Reward_Tiers": {
            "1-3": "100-500 gp",
            "4-7": "800-1500 gp + minor magic",
            "8+": "2000+ gp + major magic"
        }
    }
}
