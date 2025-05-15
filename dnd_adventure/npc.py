class NPC:
    def __init__(self, name: str, quest_offer: tuple = None, dialog: str = None):
        """
        :param name: Name of the NPC
        :param quest_offer: A tuple in the form (category, subcategory, quest_id)
        :param dialog: Optional general dialog string
        """
        self.name = name
        self.quest_offer = quest_offer
        self.dialog = dialog or f"{self.name} nods politely."

    def talk(self) -> str:
        """
        Returns the NPC's dialogue and quest offer instructions if available.
        """
        speech = f"{self.name} says: {self.dialog}"
        if self.quest_offer:
            category, sub, quest_id = self.quest_offer
            speech += (
                f"\nThey also mention a task: '{quest_id}'.\n"
                f"📝 Use command: quest start {category} {sub} {quest_id}"
            )
        return speech

    def __repr__(self):
        return f"NPC(name={self.name}, quest_offer={self.quest_offer})"
