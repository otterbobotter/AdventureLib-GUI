# AdventureLib GUI - Quick Start Guide

## 🎮 Create Your First Text Adventure in 5 Minutes!

### What You'll Need

* Python 3.x installed
* The AdventureLib library: `pip install adventurelib`
* This GUI tool (the Python file you have)

---

## 📘 Tutorial: Your First Adventure

Let's create a simple treasure hunt game with 3 rooms, an item, and a locked door!

### Step 1: Launch the Application

```bash
python adventurelib\\\_gui.py
```

---

### Step 2: Create Rooms

**Click the "Rooms" tab (it should be selected by default)**

#### Room 1: Entrance

1. **Room Name:** `Entrance`
2. **Description:** `You are standing at the entrance of an ancient temple. Dust fills the air.`
3. **Way:** `entrance` (how other rooms refer to this room)
4. Click **"Add Room"**

#### Room 2: Hallway

1. **Room Name:** `Hallway`
2. **Description:** `A dark hallway stretches before you. Torch sconces line the walls.`
3. **Way:** `hallway`
4. Click **"Add Room"**

#### Room 3: Treasury

1. **Room Name:** `Treasury`
2. **Description:** `The treasury! Gold coins are scattered across the floor.`
3. **Way:** `chamber`
4. Click **"Add Room"**

💡 **What's "Way"?** When you connect rooms, the description automatically says "To the north is a \[way]". So "hallway" becomes "To the north is a hallway."

---

### Step 3: Connect the Rooms

**Select "Entrance" from the room list**

1. In the **Exits** section:

   * Direction: `north`
   * Target: `Hallway`
   * Click **"Add Exit"**

**Select "Hallway" from the room list**

1. Add first exit:

   * Direction: `south`
   * Target: `Entrance`
   * Click **"Add Exit"**

2. Add second exit:

   * Direction: `east`
   * Target: `Treasury`
   * Click **"Add Exit"**

**Select "Treasury" from the room list**

1. Add exit:

   * Direction: `west`
   * Target: `Hallway`
   * Click **"Add Exit"**

✅ **Check the Visual Graph** - You should see three connected boxes at the top of the screen! You can click and drag to pan, scroll to zoom.

---

### Step 4: Add Items

**Click the "Items" tab**

#### Item 1: Ancient Key

1. **Item Name:** `key`
2. **Description:** `An ancient bronze key, covered in mysterious symbols.`
3. **Located in Room:** `Entrance`
4. **Check the box:** ✅ This is a Key
5. Click **"Add Item"**

You should see: `key \\\[KEY]` in the items list

#### Item 2: Gold Coin

1. **Item Name:** `coin`
2. **Description:** `A heavy gold coin stamped with a dragon.`
3. **Located in Room:** `Treasury`
4. **Leave unchecked:** ☐ This is a Key
5. Click **"Add Item"**

---

### Step 5: Lock the Treasury Door

**Return to the "Rooms" tab**

**Select "Hallway" from the room list**

Scroll down to **"Locked Directions"**

1. ✅ Check **"East locked:"**
2. In the dropdown next to it, select: `key`

This means: To go east from the Hallway, the player needs the key!

---

### Step 6: Add a First-Time Action

**Click the "First Time Entry" tab**

1. **Room:** `Treasury`
2. **Code (runs only on first entry):**

```python
   say("You found the treasure! Congratulations!")
   ```

3. Click **"Add First Time Action"**

💡 This message will only appear the FIRST time the player enters the Treasury!

---

### Step 7: Export Your Game!

**Click the "Export" tab**

1. Click **"Refresh Preview"** to see the generated code
2. Click **"Export to File"**
3. Save as: `treasure\\\_hunt.py`

---

### Step 8: Play Your Game! 🎮

```bash
python treasure\\\_hunt.py
```

**Try these commands:**

```
> look
You are standing at the entrance of an ancient temple. Dust fills the air. Items: key. To the north is a hallway.

> take key
You take the key.

> north
You go north.
A dark hallway stretches before you. Torch sconces line the walls. To the south is an entrance. To the east is a chamber.

> east
You go east.
The treasury! Gold coins are scattered across the floor. Items: coin. To the west is a hallway.
You found the treasure! Congratulations!

> take coin
You take the coin.

> inventory
Inventory: coin, key

> examine coin
A heavy gold coin stamped with a dragon.
```

🎉 **Congratulations!** You've created your first text adventure!

---

## 🎓 Advanced Features

### Custom Commands
## this is not needed, adventerlib starts with help as like a thing already
**Click the "Commands" tab**

Example - Add a "help" command:

1. **Trigger:** `help`
2. **Code:**

```python
   say("Commands: look, take \\\[item], inventory, examine \\\[item], north, south, east, west")
   ```

3. Click **"Add Command"**

### Room Entry Actions

**Click the "Room Entry Actions" tab**

Example - Make hallway scary:

1. **Room:** `Hallway`
2. **Code (runs on entry):**

```python
   say("The torches flicker ominously...")
   ```

3. Click **"Add Entry Action"**

This runs EVERY time you enter the Hallway (unlike First Time Entry which runs only once).

---

## 💡 Tips \& Tricks

### Visual Graph

* **Click nodes** to select that room in the editor
* **Click and drag** empty space to pan
* **Scroll wheel** to zoom in/out
* **Green arrows** show connections

### Reserved Room Names

If you name a room "start", "look", or "inventory", the tool automatically prefixes it with "room\_" to avoid conflicts.

### Items in Descriptions

When you add items to a room, they automatically appear in the room description: "Items: key, coin."

### Locked Doors

* Only works ONE WAY (from the room where you set it)
* Example: East locked on Hallway = can't go east FROM Hallway
* But you CAN go west from Treasury back to Hallway
* This is intentional! (One-way exits)

### Multiple Exits

You can have exits in all four directions (north, south, east, west) from any room.

---

## 🎯 Common Patterns

### A Linear Story (Room1 → Room2 → Room3)

```
Room1: north → Room2
Room2: south → Room1, north → Room3
Room3: south → Room2
```

### A Central Hub (Hallway with rooms around it)

```
Hallway: north → Room1, south → Room2, east → Room3, west → Room4
Room1: south → Hallway
Room2: north → Hallway
Room3: west → Hallway
Room4: east → Hallway
```

### A Key Hunt

1. Place key in Room A
2. Lock a direction in Room B
3. Player must visit Room A first to get the key
4. Then return to Room B to proceed

---

## 🐛 Troubleshooting

### "AttributeError: 'Room' object has no attribute 'north'"

**Fix:** Make sure you connected the rooms! Add exits in the Rooms tab.

### "That way is locked"

**Fix:** You need the required key. Type `inventory` to see what you have. Type `take \\\[key name]` to pick it up.

### Item won't take

**Fix:** Make sure you're in the right room. Type `look` to see items in current room.

### Commands not working

**Fix:** Make sure you typed exactly what's in the trigger. Commands are case-sensitive!

### Game won't start

**Fix:** Make sure you have adventurelib installed: `pip install adventurelib`

---

## 📚 Available Commands in Your Exported Game

### Movement

* `north` or `n` - Go north
* `south` or `s` - Go south
* `east` or `e` - Go east
* `west` or `w` - Go west

### Interaction

* `look` or `l` - Look around current room
* `take \\\[item]` - Pick up an item
* `inventory` or `inv` - Check what you're carrying
* `examine \\\[item]` - Look at an item closely

### Custom

* Any commands you add in the "Commands" tab!

---

## 🎨 Example Game Ideas

### Mystery Game

* Multiple rooms to investigate
* Items as clues
* First-time entry actions reveal story
* Locked rooms requiring correct key

### Escape Room

* Start in locked room
* Find items to unlock exits
* Puzzle commands (e.g., "use lever")
* Multiple keys for different doors

### Treasure Hunt

* Map of connected rooms
* Items scattered throughout
* Treasury at the end (locked)
* First-time entry celebration

### Horror Story

* Dark atmosphere in descriptions
* Entry actions for scares
* Limited items (flashlight, weapon)
* Escape is the goal

---

## 🚀 Next Steps

1. **Experiment!** Try adding more rooms, items, and commands
2. **Test thoroughly** - Play through your game before sharing
3. **Share your creation** - Export and send the .py file to friends
4. **Learn AdventureLib** - Visit https://adventurelib.readthedocs.io/ for more advanced features

---

## 📖 Quick Reference Card

|**Tab**|**Purpose**|**When to Use**|
|-|-|-|
|Rooms|Create locations|Start here - build your world|
|Commands|Custom actions|Add special interactions (help, jump, etc.)|
|Room Entry Actions|Repeated effects|Make rooms reactive (every visit)|
|First Time Entry|One-time events|Story moments, discoveries|
|Items|Objects to find|Create collectibles, keys, clues|
|Export|Generate game|Final step - create playable file|

---

## 🎮 Have Fun Creating Adventures!

The best way to learn is to experiment. Start simple, test often, and gradually add complexity.

**Remember:** Every great adventure starts with a single room!

---

**Need Help?** Check the validation checklist and bug report documents for technical details.

**Happy Adventuring!** 🗺️✨

