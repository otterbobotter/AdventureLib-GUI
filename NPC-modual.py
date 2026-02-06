from adventurelib import *

class NPC(Item):
    name = ""
    words = ""
    detail = ""
    question = ""  # Question attribute can be empty or non-empty
    ans = ""
    wrongans = ""
    gift = []


    def ask_question(self):
        """Ask a question and give a gift if the answer is correct."""
        if self.question != "":  # Check if the NPC has a question to ask
            say(f"{self.name} asks: {self.question}")
            say("What is your answer?")
        else:
            say(f"{self.name} says: {self.words}")

    def check_answer(self, answer):
        """Check if the answer is correct."""
        if answer.lower() == self.ans.lower():
            say(f"Correct! {self.name} gives you the {self.gift}.")
            player_stuff.add(self.gift)  # Add gift to player's inventory
        else:
            say(f"Wrong answer! {self.name} shakes their head sadly.")
            
class GirlNPC(NPC):
    subject_pronoun = "she"
    object_pronoun = "her"
class BoyNPC(NPC):
    subject_pronoun = "he"
    object_pronoun = "him"
