from typing import List, Dict, Optional
from .quests import DND_35E_QUESTS
from dnd_adventure.character import Character  # Use absolute import for Character

import json
from pathlib import Path

SAVE_PATH = Path("dnd_adventure/dnd35e/save/quests_save.json")

class Quest:
    def __init__(self, data: Dict):
        self.name = data["name"]
        self.hook = data["hook"]
        self.objectives = data["objectives"]
        self.key_locations = data.get("key_locations", [])
        self.rewards = data["rewards"]
        self.source = data.get("source", "Unknown")
        self.completed_objectives: List[str] = data.get("completed_objectives", [])
        self.is_complete = False
        self.check_completion()

    def check_objective(self, objective: str):
        if objective in self.objectives and objective not in self.completed_objectives:
            self.completed_objectives.append(objective)
            print(f"✅ Objective completed: {objective}")
        else:
            print(f"⚠ Objective '{objective}' already completed or invalid.")
        self.check_completion()

    def check_completion(self):
        if set(self.objectives) == set(self.completed_objectives):
            self.is_complete = True
            print(f"🎉 Quest '{self.name}' completed!")

    def to_dict(self):
        return {
            "name": self.name,
            "hook": self.hook,
            "objectives": self.objectives,
            "completed_objectives": self.completed_objectives,
            "rewards": self.rewards,
            "source": self.source
        }

    def __str__(self):
        status = "✅ Complete" if self.is_complete else "⏳ In Progress"
        return (
            f"\n📜 {self.name} [{status}]\n"
            f"Hook: {self.hook}\n"
            f"Source: {self.source}\n"
            f"Objectives:\n" +
            "\n".join(
                f"  [{'x' if obj in self.completed_objectives else ' '}] {obj}"
                for obj in self.objectives
            )
        )

class QuestManager:
    def __init__(self, character: Character):
        self.character = character
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []

    def assign_quest(self, category: str, subcategory: str, quest_id: str):
        try:
            existing_names = [q.name for q in self.active_quests + self.completed_quests]
            quest_data = DND_35E_QUESTS[category][subcategory][quest_id]
            if quest_data["name"] in existing_names:
                print(f"⚠ Quest '{quest_data['name']}' already accepted or completed.")
                return
            quest = Quest(quest_data)
            self.active_quests.append(quest)
            print(f"🆕 New quest added: {quest.name}")
        except KeyError:
            print(f"❌ Quest not found: {category}/{subcategory}/{quest_id}")

    def complete_quest(self, quest_name: str):
        quest = next((q for q in self.active_quests if q.name == quest_name), None)
        if not quest:
            print(f"⚠ Quest '{quest_name}' not found in active quests.")
            return

        self.active_quests.remove(quest)
        self.completed_quests.append(quest)
        quest.is_complete = True
        print(f"🎉 Quest '{quest.name}' completed!")

        # Grant rewards
        print(f"✨ Granting rewards for quest: {quest.name}")
        gp = quest.rewards.get("gp", 0)
        xp = quest.rewards.get("xp", 0)
        items = quest.rewards.get("items", [])

        self.character.gain_xp(xp)
        print(f"✨ Rewards: {gp} gp, {xp} XP")
        if items:
            print("📦 Items Found:")
            for item in items:
                print(f"- {item}")
        # TODO: Add GP/items to actual inventory system

    def list_quests(self):
        if not self.active_quests and not self.completed_quests:
            print("📭 No quests assigned yet.")
            return

        print("\n🗂️ Active Quests:")
        for quest in self.active_quests:
            print(quest)
        print("\n🏆 Completed Quests:")
        for quest in self.completed_quests:
            print(quest)

    def display_hud(self):
        """Quick HUD-style display of current quest progress."""
        if not self.active_quests:
            print("\n📘 Quest Log: No active quests.")
            return

        print("\n📘 Quest Log Summary:")
        for quest in self.active_quests:
            print(f"📜 {quest.name}:")
            for obj in quest.objectives:
                status = "✓" if obj in quest.completed_objectives else " "
                print(f"  [{status}] {obj}")
        print("\n📜 Type 'quest list' to see full quest details.")

    def save(self):
        """Save quests to file."""
        data = {
            "active": [q.to_dict() for q in self.active_quests],
            "completed": [q.name for q in self.completed_quests]
        }
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Load quests from save file if it exists."""
        if not SAVE_PATH.exists():
            return

        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠ Failed to load quest save: {e}")
            return

        self.active_quests.clear()
        self.completed_quests.clear()

        for quest_data in data.get("active", []):
            quest = Quest(quest_data)
            self.active_quests.append(quest)

        for name in data.get("completed", []):
            # Try to find matching completed quest info from definitions
            found = None
            for cat in DND_35E_QUESTS.values():
                for sub in cat.values():
                    for q_id, q_data in sub.items():
                        if isinstance(q_data, dict) and q_data.get("name") == name:
                            found = Quest(q_data)
                            break
            if found:
                found.is_complete = True
                self.completed_quests.append(found)
            else:
                # Fallback stub if not found in definitions
                quest = Quest({
                    "name": name,
                    "hook": "",
                    "objectives": [],
                    "rewards": {},
                    "source": "Unknown",
                    "completed_objectives": []
                })
                quest.is_complete = True
                self.completed_quests.append(quest)
                print(f"⚠ Quest '{name}' not found in definitions, loaded as incomplete.")