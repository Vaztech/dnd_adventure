from typing import List, Dict, Optional
from .quests import DND_35E_QUESTS
from .character import Character

import json
from pathlib import Path

SAVE_PATH = Path("dnd35e/save/quests_save.json")

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
            print(f"⚠️ Objective '{objective}' already completed or invalid.")
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
        status = "✅ Complete" if self.is_complete else "🕒 In Progress"
        details = (
            f"\n📜 {self.name} [{status}]\n"
            f"Hook: {self.hook}\n"
            f"Source: {self.source}\n"
            f"Objectives:\n" +
            "\n".join(
                f"  [{'x' if obj in self.completed_objectives else ' '}] {obj}"
                for obj in self.objectives
            )
        )
        return details


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
                print(f"⚠️ Quest '{quest_data['name']}' already accepted or completed.")
                return
            quest = Quest(quest_data)
            self.active_quests.append(quest)
            print(f"🆕 New quest added: {quest.name}")
        except KeyError:
            print(f"❌ Quest not found: {category} > {subcategory} > {quest_id}")

    def complete_objective(self, quest_name: str, objective: str):
        for quest in self.active_quests:
            if quest.name == quest_name:
                quest.check_objective(objective)
                if quest.is_complete:
                    self.reward_player(quest)
                    self.active_quests.remove(quest)
                    self.completed_quests.append(quest)
                return
        print(f"❌ No active quest found with name: '{quest_name}'")

    def reward_player(self, quest: Quest):
        print(f"\n🎁 Granting rewards for quest: {quest.name}")
        gp = quest.rewards.get("gp", 0)
        xp = quest.rewards.get("xp", 0)
        items = quest.rewards.get("items", [])

        self.character.gain_xp(xp)
        print(f"✨ Rewards: {gp} gp, {xp} XP")
        if items:
            print("📦 Items Found:")
            for item in items:
                print(f"- {item}")
        # TODO: Add GP or items to player inventory system

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
            print(f"📍 {quest.name}:")
            for obj in quest.objectives:
                status = "✓" if obj in quest.completed_objectives else " "
                print(f"  [{status}] {obj}")
        print()
        print("📜 Type 'quest list' to see all quest details.")

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
            print(f"⚠️ Failed to load quest save: {e}")
            return

        self.active_quests.clear()
        self.completed_quests.clear()

        for quest_data in data.get("active", []):
            quest = Quest({
                "name": quest_data["name"],
                "hook": quest_data["hook"],
                "objectives": quest_data["objectives"],
                "rewards": quest_data["rewards"],
                "source": quest_data.get("source", "Unknown"),
                "completed_objectives": quest_data.get("completed_objectives", [])
            })
            self.active_quests.append(quest)

        for name in data.get("completed", []):
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
