import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class AdventureLibGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AdventureLib Assistant")
        self.root.geometry("900x700")
        
        self.rooms = {}
        self.room_ways = {}  # room_name -> "way" (e.g. "passage", "building", "moon")
        self.room_exits = {}  # room_name -> {direction: target_room}
        self.room_locked_directions = {}  # room_name -> set of locked directions (e.g. {'north', 'south'})
        self.room_direction_keys = {}  # (room_name, direction) -> key_item_name
        self.commands = {}
        self.room_entry_commands = {}
        self.room_first_time_commands = {}  # room_name -> code that runs only on first visit
        
        # Items system
        self.items = {}  # item_name -> description
        self.item_locations = {}  # item_name -> room_name (where item is placed)
        self.item_keys = {}  # item_name -> is_key (bool)
        # NPC system
        self.npcs = {}  # npc_name -> dict of attributes
        self.npc_locations = {}  # npc_name -> room_name
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Room Management Tab
        room_frame = ttk.Frame(notebook)
        notebook.add(room_frame, text="Rooms")
        self.setup_room_tab(room_frame)
        
        # Commands Tab
        cmd_frame = ttk.Frame(notebook)
        notebook.add(cmd_frame, text="Commands")
        self.setup_commands_tab(cmd_frame)
        
        # Room Entry Commands Tab
        entry_frame = ttk.Frame(notebook)
        notebook.add(entry_frame, text="Room Entry Actions")
        self.setup_entry_commands_tab(entry_frame)
        
        # First Time Entry Commands Tab
        first_frame = ttk.Frame(notebook)
        notebook.add(first_frame, text="First Time Entry")
        self.setup_first_time_tab(first_frame)
        
        # Items Tab
        items_frame = ttk.Frame(notebook)
        notebook.add(items_frame, text="Items")
        self.setup_items_tab(items_frame)
        
        # NPCs Tab
        npcs_frame = ttk.Frame(notebook)
        notebook.add(npcs_frame, text="NPCs")
        self.setup_npcs_tab(npcs_frame)

        # Export Tab
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="Export")
        self.setup_export_tab(export_frame)
    
    def setup_room_tab(self, parent):
        # TOP SECTION: Canvas + Buttons (fixed height)
        top_sect = ttk.Frame(parent)
        top_sect.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)
        
        ttk.Label(top_sect, text="Rooms (visual - click and drag to pan, click node to select):").pack(anchor=tk.W)
        self.canvas = tk.Canvas(top_sect, height=250, bg="#222222")
        self.canvas.pack(fill=tk.X)
        self.canvas.bind('<Button-1>', self.on_canvas_button_down)
        self.canvas.bind('<B1-Motion>', self.on_pan_motion)
        self.canvas.bind('<ButtonRelease-1>', self.on_pan_end)
        self.canvas.bind('<MouseWheel>', self.on_canvas_scroll)  # Windows
        self.canvas.bind('<Button-4>', self.on_canvas_scroll)    # Linux scroll up
        self.canvas.bind('<Button-5>', self.on_canvas_scroll)    # Linux scroll down
        
        # Canvas pan/zoom state
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.canvas_zoom = 1.0
        self.pan_start = None
        
        # Buttons (right below canvas)
        btn_frame = ttk.Frame(top_sect)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add Room", command=self.add_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update Room", command=self.update_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Room", command=self.delete_room).pack(side=tk.LEFT, padx=2)
        
        # BOTTOM SECTION: Scrollable editing area
        scroll_frame = ttk.Frame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for scrolling
        scroll_canvas = tk.Canvas(scroll_frame, bg="white")
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Inner frame to hold all content
        bottom_sect = ttk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=bottom_sect, anchor="nw")
        
        # Room list
        ttk.Label(bottom_sect, text="Rooms:").pack(anchor=tk.W)
        list_frame = ttk.Frame(bottom_sect)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_scrollbar = ttk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.room_listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set, height=6)
        self.room_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.room_listbox.bind('<<ListboxSelect>>', self.on_room_select)
        list_scrollbar.config(command=self.room_listbox.yview)
        
        # Room name input
        name_frame = ttk.Frame(bottom_sect)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Room Name:").pack(side=tk.LEFT)
        self.room_name_entry = ttk.Entry(name_frame)
        self.room_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Room description (smaller height)
        ttk.Label(bottom_sect, text="Description:").pack(anchor=tk.W)
        self.room_desc_text = tk.Text(bottom_sect, height=3)
        self.room_desc_text.pack(fill=tk.X, pady=5)
        
        # Room way (how adjacent rooms refer to this one)
        way_frame = ttk.Frame(bottom_sect)
        way_frame.pack(fill=tk.X, pady=5)
        ttk.Label(way_frame, text="Way (how to refer to this room, e.g. 'passage', 'building', 'moon'):").pack(side=tk.LEFT)
        self.room_way_entry = ttk.Entry(way_frame)
        self.room_way_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Exits editor
        exits_frame = ttk.Frame(bottom_sect)
        exits_frame.pack(fill=tk.X, pady=5)
        ttk.Label(exits_frame, text="Exits:").pack(side=tk.LEFT)
        self.exit_dir_var = tk.StringVar(value="north")
        self.exit_dir_combo = ttk.Combobox(exits_frame, textvariable=self.exit_dir_var, values=["north","south","east","west"], width=8)
        self.exit_dir_combo.pack(side=tk.LEFT, padx=5)
        self.exit_target_var = tk.StringVar()
        self.exit_target_combo = ttk.Combobox(exits_frame, textvariable=self.exit_target_var)
        self.exit_target_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(exits_frame, text="Add Exit", command=self.add_exit).pack(side=tk.LEFT, padx=5)
        ttk.Button(exits_frame, text="Delete Exit", command=self.delete_exit).pack(side=tk.LEFT, padx=5)
        
        # Exits list for current room
        ttk.Label(bottom_sect, text="Current Room Exits:").pack(anchor=tk.W)
        self.exits_listbox = tk.Listbox(bottom_sect, height=2)
        self.exits_listbox.pack(fill=tk.X, pady=2)
        
        # Locked directions
        ttk.Label(bottom_sect, text="Locked Directions (one-way exits) - Select key if locked:").pack(anchor=tk.W, pady=(10, 5))
        locked_frame = ttk.Frame(bottom_sect)
        locked_frame.pack(fill=tk.X, pady=2)
        
        # North
        locked_n_frame = ttk.Frame(locked_frame)
        locked_n_frame.pack(fill=tk.X, pady=2)
        self.locked_north = tk.BooleanVar()
        ttk.Checkbutton(locked_n_frame, text="North locked:", variable=self.locked_north).pack(side=tk.LEFT, padx=5)
        self.locked_north_key_var = tk.StringVar()
        self.locked_north_key_combo = ttk.Combobox(locked_n_frame, textvariable=self.locked_north_key_var, width=20)
        self.locked_north_key_combo.pack(side=tk.LEFT, padx=5)
        
        # South
        locked_s_frame = ttk.Frame(locked_frame)
        locked_s_frame.pack(fill=tk.X, pady=2)
        self.locked_south = tk.BooleanVar()
        ttk.Checkbutton(locked_s_frame, text="South locked:", variable=self.locked_south).pack(side=tk.LEFT, padx=5)
        self.locked_south_key_var = tk.StringVar()
        self.locked_south_key_combo = ttk.Combobox(locked_s_frame, textvariable=self.locked_south_key_var, width=20)
        self.locked_south_key_combo.pack(side=tk.LEFT, padx=5)
        
        # East
        locked_e_frame = ttk.Frame(locked_frame)
        locked_e_frame.pack(fill=tk.X, pady=2)
        self.locked_east = tk.BooleanVar()
        ttk.Checkbutton(locked_e_frame, text="East locked:", variable=self.locked_east).pack(side=tk.LEFT, padx=5)
        self.locked_east_key_var = tk.StringVar()
        self.locked_east_key_combo = ttk.Combobox(locked_e_frame, textvariable=self.locked_east_key_var, width=20)
        self.locked_east_key_combo.pack(side=tk.LEFT, padx=5)
        
        # West
        locked_w_frame = ttk.Frame(locked_frame)
        locked_w_frame.pack(fill=tk.X, pady=2)
        self.locked_west = tk.BooleanVar()
        ttk.Checkbutton(locked_w_frame, text="West locked:", variable=self.locked_west).pack(side=tk.LEFT, padx=5)
        self.locked_west_key_var = tk.StringVar()
        self.locked_west_key_combo = ttk.Combobox(locked_w_frame, textvariable=self.locked_west_key_var, width=20)
        self.locked_west_key_combo.pack(side=tk.LEFT, padx=5)
        
        # Update scroll region when inner frame resizes
        def on_frame_configure(event=None):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        bottom_sect.bind("<Configure>", on_frame_configure)
        
        # Bind mousewheel to scroll (only on the scroll canvas, not globally)
        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scroll_canvas.bind("<MouseWheel>", _on_mousewheel)
        scroll_canvas.bind("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))
        scroll_canvas.bind("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))
    
    def setup_commands_tab(self, parent):
        ttk.Label(parent, text="Commands:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Command list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cmd_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.cmd_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cmd_listbox.bind('<<ListboxSelect>>', self.on_command_select)
        scrollbar.config(command=self.cmd_listbox.yview)
        
        # Command trigger
        trigger_frame = ttk.Frame(parent)
        trigger_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(trigger_frame, text="Trigger:").pack(side=tk.LEFT)
        self.cmd_trigger_entry = ttk.Entry(trigger_frame)
        self.cmd_trigger_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Command code
        ttk.Label(parent, text="Code:").pack(anchor=tk.W, padx=5)
        self.cmd_code_text = tk.Text(parent, height=8, width=40)
        self.cmd_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add Command", command=self.add_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update Command", command=self.update_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Command", command=self.delete_command).pack(side=tk.LEFT, padx=2)
    
    def setup_entry_commands_tab(self, parent):
        ttk.Label(parent, text="Room Entry Actions:").pack(anchor=tk.W, padx=5, pady=5)
        
        # List
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.entry_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.entry_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry_listbox.bind('<<ListboxSelect>>', self.on_entry_select)
        scrollbar.config(command=self.entry_listbox.yview)
        
        # Room selection
        room_frame = ttk.Frame(parent)
        room_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(room_frame, text="Room:").pack(side=tk.LEFT)
        self.entry_room_var = tk.StringVar()
        self.entry_room_combo = ttk.Combobox(room_frame, textvariable=self.entry_room_var)
        self.entry_room_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Code
        ttk.Label(parent, text="Code (runs on entry):").pack(anchor=tk.W, padx=5)
        self.entry_code_text = tk.Text(parent, height=8, width=40)
        self.entry_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add Entry Action", command=self.add_entry_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_entry_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_entry_command).pack(side=tk.LEFT, padx=2)
    
    def setup_first_time_tab(self, parent):
        ttk.Label(parent, text="First Time Entry Actions (runs only on first visit):").pack(anchor=tk.W, padx=5, pady=5)
        
        # List
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.first_time_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.first_time_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.first_time_listbox.bind('<<ListboxSelect>>', self.on_first_time_select)
        scrollbar.config(command=self.first_time_listbox.yview)
        
        # Room selection
        room_frame = ttk.Frame(parent)
        room_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(room_frame, text="Room:").pack(side=tk.LEFT)
        self.first_time_room_var = tk.StringVar()
        self.first_time_room_combo = ttk.Combobox(room_frame, textvariable=self.first_time_room_var)
        self.first_time_room_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Code
        ttk.Label(parent, text="Code (runs only on first entry):").pack(anchor=tk.W, padx=5)
        self.first_time_code_text = tk.Text(parent, height=8, width=40)
        self.first_time_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add First Time Action", command=self.add_first_time_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_first_time_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_first_time_command).pack(side=tk.LEFT, padx=2)
    
    def setup_items_tab(self, parent):
        ttk.Label(parent, text="Items Management").pack(anchor=tk.W, padx=5, pady=5)
        
        # Items list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.items_listbox.bind('<<ListboxSelect>>', self.on_item_select)
        scrollbar.config(command=self.items_listbox.yview)
        
        # Item name
        name_frame = ttk.Frame(parent)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(name_frame, text="Item Name:").pack(side=tk.LEFT)
        self.item_name_entry = ttk.Entry(name_frame)
        self.item_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Item description
        ttk.Label(parent, text="Description:").pack(anchor=tk.W, padx=5)
        self.item_desc_text = tk.Text(parent, height=3)
        self.item_desc_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Item location (room)
        loc_frame = ttk.Frame(parent)
        loc_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(loc_frame, text="Located in Room:").pack(side=tk.LEFT)
        self.item_room_var = tk.StringVar()
        self.item_room_combo = ttk.Combobox(loc_frame, textvariable=self.item_room_var)
        self.item_room_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Is key checkbox
        self.item_is_key_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="This is a Key", variable=self.item_is_key_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update Item", command=self.update_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Item", command=self.delete_item).pack(side=tk.LEFT, padx=2)
    
    def setup_npcs_tab(self, parent):
        ttk.Label(parent, text="NPC Management").pack(anchor=tk.W, padx=5, pady=5)

        # NPC list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.npc_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.npc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.npc_listbox.bind('<<ListboxSelect>>', self.on_npc_select)
        scrollbar.config(command=self.npc_listbox.yview)

        # NPC fields
        name_frame = ttk.Frame(parent)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        self.npc_name_entry = ttk.Entry(name_frame)
        self.npc_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(parent, text="Words:").pack(anchor=tk.W, padx=5)
        self.npc_words_text = tk.Text(parent, height=2)
        self.npc_words_text.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(parent, text="Detail:").pack(anchor=tk.W, padx=5)
        self.npc_detail_text = tk.Text(parent, height=2)
        self.npc_detail_text.pack(fill=tk.X, padx=5, pady=2)

        # Question / answer / wrong answer
        qframe = ttk.Frame(parent)
        qframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(qframe, text="Question:").pack(side=tk.LEFT)
        self.npc_question_entry = ttk.Entry(qframe)
        self.npc_question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        aframe = ttk.Frame(parent)
        aframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(aframe, text="Answer:").pack(side=tk.LEFT)
        self.npc_answer_entry = ttk.Entry(aframe)
        self.npc_answer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        wa_frame = ttk.Frame(parent)
        wa_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(wa_frame, text="Wrong Answer Text:").pack(side=tk.LEFT)
        self.npc_wrong_entry = ttk.Entry(wa_frame)
        self.npc_wrong_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Gift selection (comma-separated items)
        gframe = ttk.Frame(parent)
        gframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gframe, text="Gifts (comma-separated item names):").pack(side=tk.LEFT)
        self.npc_gift_entry = ttk.Entry(gframe)
        self.npc_gift_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Located in room
        loc_frame = ttk.Frame(parent)
        loc_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(loc_frame, text="Located in Room:").pack(side=tk.LEFT)
        self.npc_room_var = tk.StringVar()
        self.npc_room_combo = ttk.Combobox(loc_frame, textvariable=self.npc_room_var)
        self.npc_room_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add NPC", command=self.add_npc).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update NPC", command=self.update_npc).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete NPC", command=self.delete_npc).pack(side=tk.LEFT, padx=2)
    
    def setup_export_tab(self, parent):
        ttk.Label(parent, text="Export your adventure as Python code").pack(padx=5, pady=10)
        
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(preview_frame, text="Preview:").pack(anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(preview_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_text = tk.Text(preview_frame, yscrollcommand=scrollbar.set)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preview_text.yview)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Refresh Preview", command=self.refresh_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export to File", command=self.export_to_file).pack(side=tk.LEFT, padx=2)
    
    def add_room(self):
        name = self.room_name_entry.get()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a room name")
            return
        self.rooms[name] = self.room_desc_text.get("1.0", tk.END).strip()
        way = self.room_way_entry.get().strip() or "passage"
        self.room_ways[name] = way
        self.room_exits.setdefault(name, {})
        # Store locked directions and their keys
        locked = set()
        if self.locked_north.get():
            locked.add('north')
            key = self.locked_north_key_var.get()
            if key:
                self.room_direction_keys[(name, 'north')] = key
        if self.locked_south.get():
            locked.add('south')
            key = self.locked_south_key_var.get()
            if key:
                self.room_direction_keys[(name, 'south')] = key
        if self.locked_east.get():
            locked.add('east')
            key = self.locked_east_key_var.get()
            if key:
                self.room_direction_keys[(name, 'east')] = key
        if self.locked_west.get():
            locked.add('west')
            key = self.locked_west_key_var.get()
            if key:
                self.room_direction_keys[(name, 'west')] = key
        if locked:
            self.room_locked_directions[name] = locked
        self.refresh_room_list()
        self.refresh_exits_list()
        self.room_name_entry.delete(0, tk.END)
        self.room_desc_text.delete("1.0", tk.END)
        self.room_way_entry.delete(0, tk.END)
        self.locked_north.set(False)
        self.locked_south.set(False)
        self.locked_east.set(False)
        self.locked_west.set(False)
        self.locked_north_key_var.set("")
        self.locked_south_key_var.set("")
        self.locked_east_key_var.set("")
        self.locked_west_key_var.set("")
        self.update_room_combo()
    
    def update_room(self):
        selection = self.room_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a room")
            return
        old_name = self.room_listbox.get(selection[0])
        new_name = self.room_name_entry.get() or old_name
        
        if old_name != new_name and new_name in self.rooms:
            messagebox.showerror("Error", "Room name already exists")
            return
        
        if old_name != new_name:
            self.rooms[new_name] = self.rooms.pop(old_name)
            self.room_ways[new_name] = self.room_ways.pop(old_name, "passage")
            # rename exits key
            self.room_exits[new_name] = self.room_exits.pop(old_name, {})
            # rename locked directions entry
            if old_name in self.room_locked_directions:
                self.room_locked_directions[new_name] = self.room_locked_directions.pop(old_name)
            # rename locked direction keys
            keys_to_rename = [(old_name, d) for (room, d) in self.room_direction_keys.keys() if room == old_name]
            for (room, direction) in keys_to_rename:
                key_value = self.room_direction_keys.pop((room, direction))
                self.room_direction_keys[(new_name, direction)] = key_value
            # update any exits that pointed to old_name
            for r, exits in self.room_exits.items():
                for d, t in list(exits.items()):
                    if t == old_name:
                        exits[d] = new_name
        
        self.rooms[new_name] = self.room_desc_text.get("1.0", tk.END).strip()
        way = self.room_way_entry.get().strip() or "passage"
        self.room_ways[new_name] = way
        # Update locked directions and their keys
        locked = set()
        # Clean up old keys first
        for direction in ['north', 'south', 'east', 'west']:
            if (new_name, direction) in self.room_direction_keys:
                del self.room_direction_keys[(new_name, direction)]
        
        if self.locked_north.get():
            locked.add('north')
            key = self.locked_north_key_var.get()
            if key:
                self.room_direction_keys[(new_name, 'north')] = key
        if self.locked_south.get():
            locked.add('south')
            key = self.locked_south_key_var.get()
            if key:
                self.room_direction_keys[(new_name, 'south')] = key
        if self.locked_east.get():
            locked.add('east')
            key = self.locked_east_key_var.get()
            if key:
                self.room_direction_keys[(new_name, 'east')] = key
        if self.locked_west.get():
            locked.add('west')
            key = self.locked_west_key_var.get()
            if key:
                self.room_direction_keys[(new_name, 'west')] = key
        if locked:
            self.room_locked_directions[new_name] = locked
        elif new_name in self.room_locked_directions:
            del self.room_locked_directions[new_name]
        self.refresh_room_list()
        self.update_room_combo()
    
    def delete_room(self):
        selection = self.room_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a room")
            return
        name = self.room_listbox.get(selection[0])
        del self.rooms[name]
        if name in self.room_ways:
            del self.room_ways[name]
        if name in self.room_locked_directions:
            del self.room_locked_directions[name]
        # Remove locked direction keys for this room
        keys_to_delete = [(room, d) for (room, d) in self.room_direction_keys.keys() if room == name]
        for (room, direction) in keys_to_delete:
            del self.room_direction_keys[(room, direction)]
        if name in self.room_entry_commands:
            del self.room_entry_commands[name]
        if name in self.room_first_time_commands:
            del self.room_first_time_commands[name]
        # remove exits for this room and references to it
        if name in self.room_exits:
            del self.room_exits[name]
        for r, exits in list(self.room_exits.items()):
            for d, t in list(exits.items()):
                if t == name:
                    del exits[d]
        self.refresh_room_list()
        self.refresh_entry_list()
        self.refresh_first_time_list()
        self.update_room_combo()
    
    def on_room_select(self, event):
        selection = self.room_listbox.curselection()
        if selection:
            name = self.room_listbox.get(selection[0])
            self.room_name_entry.delete(0, tk.END)
            self.room_name_entry.insert(0, name)
            self.room_desc_text.delete("1.0", tk.END)
            self.room_desc_text.insert("1.0", self.rooms[name])
            self.room_way_entry.delete(0, tk.END)
            self.room_way_entry.insert(0, self.room_ways.get(name, "passage"))
            # Load locked directions for this room
            locked = self.room_locked_directions.get(name, set())
            self.locked_north.set('north' in locked)
            self.locked_south.set('south' in locked)
            self.locked_east.set('east' in locked)
            self.locked_west.set('west' in locked)
            # Load locked direction keys
            self.locked_north_key_var.set(self.room_direction_keys.get((name, 'north'), ""))
            self.locked_south_key_var.set(self.room_direction_keys.get((name, 'south'), ""))
            self.locked_east_key_var.set(self.room_direction_keys.get((name, 'east'), ""))
            self.locked_west_key_var.set(self.room_direction_keys.get((name, 'west'), ""))
            # refresh exits for this room
            self.refresh_exits_list()
    
    def refresh_room_list(self):
        self.room_listbox.delete(0, tk.END)
        for name in self.rooms:
            self.room_listbox.insert(tk.END, name)
        self.update_room_combo()
        self.refresh_exit_targets()
        self.refresh_key_combos()  # Ensure keys are available for room locks
        # Update NPC room combo as well
        try:
            self.npc_room_combo['values'] = list(self.rooms.keys())
        except Exception:
            pass
        # Reset pan/zoom when refreshing
        if not self.rooms:
            self.canvas_offset_x = 0
            self.canvas_offset_y = 0
            self.canvas_zoom = 1.0
        self.draw_graph()

    def refresh_exit_targets(self):
        vals = list(self.rooms.keys())
        self.exit_target_combo['values'] = vals
        self.entry_room_combo['values'] = vals
    
    def add_command(self):
        trigger = self.cmd_trigger_entry.get()
        if not trigger:
            messagebox.showwarning("Input Error", "Please enter a trigger")
            return
        self.commands[trigger] = self.cmd_code_text.get("1.0", tk.END).strip()
        self.refresh_command_list()
        self.cmd_trigger_entry.delete(0, tk.END)
        self.cmd_code_text.delete("1.0", tk.END)
    
    def update_command(self):
        selection = self.cmd_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a command")
            return
        old_trigger = self.cmd_listbox.get(selection[0])
        new_trigger = self.cmd_trigger_entry.get() or old_trigger
        
        if old_trigger != new_trigger:
            self.commands[new_trigger] = self.commands.pop(old_trigger)
        
        self.commands[new_trigger] = self.cmd_code_text.get("1.0", tk.END).strip()
        self.refresh_command_list()
    
    def delete_command(self):
        selection = self.cmd_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a command")
            return
        trigger = self.cmd_listbox.get(selection[0])
        del self.commands[trigger]
        self.refresh_command_list()
    
    def on_command_select(self, event):
        selection = self.cmd_listbox.curselection()
        if selection:
            trigger = self.cmd_listbox.get(selection[0])
            self.cmd_trigger_entry.delete(0, tk.END)
            self.cmd_trigger_entry.insert(0, trigger)
            self.cmd_code_text.delete("1.0", tk.END)
            self.cmd_code_text.insert("1.0", self.commands[trigger])
    
    def refresh_command_list(self):
        self.cmd_listbox.delete(0, tk.END)
        for trigger in self.commands:
            self.cmd_listbox.insert(tk.END, trigger)

    
    def add_entry_command(self):
        room = self.entry_room_var.get()
        if not room:
            messagebox.showwarning("Input Error", "Please select a room")
            return
        self.room_entry_commands[room] = self.entry_code_text.get("1.0", tk.END).strip()
        self.refresh_entry_list()
        self.entry_code_text.delete("1.0", tk.END)
    
    def update_entry_command(self):
        selection = self.entry_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an entry command")
            return
        old_room = self.entry_listbox.get(selection[0])
        new_room = self.entry_room_var.get() or old_room
        
        if old_room != new_room:
            self.room_entry_commands[new_room] = self.room_entry_commands.pop(old_room)
        
        self.room_entry_commands[new_room] = self.entry_code_text.get("1.0", tk.END).strip()
        self.refresh_entry_list()
    
    def delete_entry_command(self):
        selection = self.entry_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an entry command")
            return
        room = self.entry_listbox.get(selection[0])
        del self.room_entry_commands[room]
        self.refresh_entry_list()
    
    def on_entry_select(self, event):
        selection = self.entry_listbox.curselection()
        if selection:
            room = self.entry_listbox.get(selection[0])
            self.entry_room_var.set(room)
            self.entry_code_text.delete("1.0", tk.END)
            self.entry_code_text.insert("1.0", self.room_entry_commands[room])
    
    def refresh_entry_list(self):
        self.entry_listbox.delete(0, tk.END)
        for room in self.room_entry_commands:
            self.entry_listbox.insert(tk.END, room)
    
    def add_first_time_command(self):
        room = self.first_time_room_var.get()
        if not room:
            messagebox.showwarning("Input Error", "Please select a room")
            return
        self.room_first_time_commands[room] = self.first_time_code_text.get("1.0", tk.END).strip()
        self.refresh_first_time_list()
        self.first_time_code_text.delete("1.0", tk.END)
    
    def update_first_time_command(self):
        selection = self.first_time_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a first time command")
            return
        old_room = self.first_time_listbox.get(selection[0])
        new_room = self.first_time_room_var.get() or old_room
        
        if old_room != new_room:
            self.room_first_time_commands[new_room] = self.room_first_time_commands.pop(old_room)
        
        self.room_first_time_commands[new_room] = self.first_time_code_text.get("1.0", tk.END).strip()
        self.refresh_first_time_list()
    
    def delete_first_time_command(self):
        selection = self.first_time_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a first time command")
            return
        room = self.first_time_listbox.get(selection[0])
        del self.room_first_time_commands[room]
        self.refresh_first_time_list()
    
    def on_first_time_select(self, event):
        selection = self.first_time_listbox.curselection()
        if selection:
            room = self.first_time_listbox.get(selection[0])
            self.first_time_room_var.set(room)
            self.first_time_code_text.delete("1.0", tk.END)
            self.first_time_code_text.insert("1.0", self.room_first_time_commands[room])
    
    def refresh_first_time_list(self):
        self.first_time_listbox.delete(0, tk.END)
        for room in self.room_first_time_commands:
            self.first_time_listbox.insert(tk.END, room)
    
    # Items management
    def add_item(self):
        name = self.item_name_entry.get()
        if not name:
            messagebox.showwarning("Input Error", "Please enter an item name")
            return
        if name in self.items:
            messagebox.showerror("Error", "Item already exists")
            return
        
        self.items[name] = self.item_desc_text.get("1.0", tk.END).strip()
        self.item_locations[name] = self.item_room_var.get()
        self.item_keys[name] = self.item_is_key_var.get()
        
        self.refresh_items_list()
        self.refresh_key_combos()
        self.item_name_entry.delete(0, tk.END)
        self.item_desc_text.delete("1.0", tk.END)
        self.item_room_var.set("")
        self.item_is_key_var.set(False)

    # NPC CRUD
    def add_npc(self):
        name = self.npc_name_entry.get()
        if not name:
            messagebox.showwarning("Input Error", "Please enter an NPC name")
            return
        if name in self.npcs:
            messagebox.showerror("Error", "NPC already exists")
            return
        self.npcs[name] = {
            'words': self.npc_words_text.get("1.0", tk.END).strip(),
            'detail': self.npc_detail_text.get("1.0", tk.END).strip(),
            'question': self.npc_question_entry.get().strip(),
            'ans': self.npc_answer_entry.get().strip(),
            'wrongans': self.npc_wrong_entry.get().strip(),
            'gift': [g.strip() for g in self.npc_gift_entry.get().split(',') if g.strip()]
        }
        self.npc_locations[name] = self.npc_room_var.get()
        self.refresh_npc_list()
        self.npc_name_entry.delete(0, tk.END)
        self.npc_words_text.delete("1.0", tk.END)
        self.npc_detail_text.delete("1.0", tk.END)
        self.npc_question_entry.delete(0, tk.END)
        self.npc_answer_entry.delete(0, tk.END)
        self.npc_wrong_entry.delete(0, tk.END)
        self.npc_gift_entry.delete(0, tk.END)
        self.npc_room_var.set("")

    def update_npc(self):
        selection = self.npc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an NPC")
            return
        old_name = self.npc_listbox.get(selection[0])
        new_name = self.npc_name_entry.get() or old_name
        if old_name != new_name and new_name in self.npcs:
            messagebox.showerror("Error", "NPC name already exists")
            return
        if old_name != new_name:
            self.npcs[new_name] = self.npcs.pop(old_name)
            self.npc_locations[new_name] = self.npc_locations.pop(old_name, "")
        self.npcs[new_name] = {
            'words': self.npc_words_text.get("1.0", tk.END).strip(),
            'detail': self.npc_detail_text.get("1.0", tk.END).strip(),
            'question': self.npc_question_entry.get().strip(),
            'ans': self.npc_answer_entry.get().strip(),
            'wrongans': self.npc_wrong_entry.get().strip(),
            'gift': [g.strip() for g in self.npc_gift_entry.get().split(',') if g.strip()]
        }
        self.npc_locations[new_name] = self.npc_room_var.get()
        self.refresh_npc_list()

    def delete_npc(self):
        selection = self.npc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an NPC")
            return
        name = self.npc_listbox.get(selection[0])
        if name in self.npcs:
            del self.npcs[name]
        if name in self.npc_locations:
            del self.npc_locations[name]
        self.refresh_npc_list()

    def on_npc_select(self, event):
        selection = self.npc_listbox.curselection()
        if selection:
            name = self.npc_listbox.get(selection[0])
            data = self.npcs.get(name, {})
            self.npc_name_entry.delete(0, tk.END)
            self.npc_name_entry.insert(0, name)
            self.npc_words_text.delete("1.0", tk.END)
            self.npc_words_text.insert("1.0", data.get('words', ""))
            self.npc_detail_text.delete("1.0", tk.END)
            self.npc_detail_text.insert("1.0", data.get('detail', ""))
            self.npc_question_entry.delete(0, tk.END)
            self.npc_question_entry.insert(0, data.get('question', ""))
            self.npc_answer_entry.delete(0, tk.END)
            self.npc_answer_entry.insert(0, data.get('ans', ""))
            self.npc_wrong_entry.delete(0, tk.END)
            self.npc_wrong_entry.insert(0, data.get('wrongans', ""))
            self.npc_gift_entry.delete(0, tk.END)
            self.npc_gift_entry.insert(0, ', '.join(data.get('gift', [])))
            self.npc_room_var.set(self.npc_locations.get(name, ""))

    def refresh_npc_list(self):
        self.npc_listbox.delete(0, tk.END)
        for n in self.npcs:
            self.npc_listbox.insert(tk.END, n)
    
    def update_item(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an item")
            return
        
        old_name = self.items_listbox.get(selection[0]).replace(" [KEY]", "")
        new_name = self.item_name_entry.get() or old_name
        
        if old_name != new_name and new_name in self.items:
            messagebox.showerror("Error", "Item name already exists")
            return
        
        # Rename if needed
        if old_name != new_name:
            self.items[new_name] = self.items.pop(old_name)
            self.item_locations[new_name] = self.item_locations.pop(old_name, "")
            self.item_keys[new_name] = self.item_keys.pop(old_name, False)
        
        self.items[new_name] = self.item_desc_text.get("1.0", tk.END).strip()
        self.item_locations[new_name] = self.item_room_var.get()
        self.item_keys[new_name] = self.item_is_key_var.get()
        
        self.refresh_items_list()
        self.refresh_key_combos()
    
    def delete_item(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an item")
            return
        
        name = self.items_listbox.get(selection[0]).replace(" [KEY]", "")
        del self.items[name]
        if name in self.item_locations:
            del self.item_locations[name]
        if name in self.item_keys:
            del self.item_keys[name]
        
        self.refresh_items_list()
        self.refresh_key_combos()
    
    def on_item_select(self, event):
        selection = self.items_listbox.curselection()
        if selection:
            name = self.items_listbox.get(selection[0]).replace(" [KEY]", "")
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.insert(0, name)
            self.item_desc_text.delete("1.0", tk.END)
            self.item_desc_text.insert("1.0", self.items.get(name, ""))
            self.item_room_var.set(self.item_locations.get(name, ""))
            self.item_is_key_var.set(self.item_keys.get(name, False))
    
    def refresh_items_list(self):
        self.items_listbox.delete(0, tk.END)
        for item in self.items:
            is_key = " [KEY]" if self.item_keys.get(item, False) else ""
            self.items_listbox.insert(tk.END, f"{item}{is_key}")
    
    def refresh_key_combos(self):
        # Get list of keys (items marked as keys)
        keys_list = [item for item in self.items if self.item_keys.get(item, False)]
        try:
            self.locked_north_key_combo['values'] = keys_list
            self.locked_south_key_combo['values'] = keys_list
            self.locked_east_key_combo['values'] = keys_list
            self.locked_west_key_combo['values'] = keys_list
        except Exception:
            pass
        # Also include keys as possible NPC gift items (no UI control needed here)
    
    def update_room_combo(self):
        self.entry_room_combo['values'] = list(self.rooms.keys())
        self.first_time_room_combo['values'] = list(self.rooms.keys())
        self.item_room_combo['values'] = list(self.rooms.keys())
        # also keep exit targets updated
        try:
            self.exit_target_combo['values'] = list(self.rooms.keys())
        except Exception:
            pass

    # Exits management
    def add_exit(self):
        sel = self.room_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection Error", "Select a room to add an exit to")
            return
        room = self.room_listbox.get(sel[0])
        direction = self.exit_dir_var.get()
        target = self.exit_target_var.get()
        if not target or target not in self.rooms:
            messagebox.showwarning("Input Error", "Select a valid target room")
            return
        self.room_exits.setdefault(room, {})[direction] = target
        self.refresh_exits_list()
        self.draw_graph()

    def delete_exit(self):
        sel = self.room_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection Error", "Select a room first")
            return
        room = self.room_listbox.get(sel[0])
        sel2 = self.exits_listbox.curselection()
        if not sel2:
            messagebox.showwarning("Selection Error", "Select an exit to delete")
            return
        entry = self.exits_listbox.get(sel2[0])
        # entry format: "north -> target"
        direction = entry.split()[0]
        if room in self.room_exits and direction in self.room_exits[room]:
            del self.room_exits[room][direction]
        self.refresh_exits_list()
        self.draw_graph()

    def refresh_exits_list(self):
        self.exits_listbox.delete(0, tk.END)
        sel = self.room_listbox.curselection()
        if not sel:
            return
        room = self.room_listbox.get(sel[0])
        exits = self.room_exits.get(room, {})
        for d, t in exits.items():
            self.exits_listbox.insert(tk.END, f"{d} -> {t}")

    # Canvas graph drawing
    def draw_graph(self):
        self.canvas.delete('all')
        if not self.rooms:
            return

        # compute grid positions using BFS starting from 'start' or first room
        dirs = {'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}
        positions = {}
        from collections import deque
        try:
            start = 'start' if 'start' in self.rooms else next(iter(self.rooms))
        except StopIteration:
            return
        positions[start] = (0,0)
        q = deque([start])
        while q:
            r = q.popleft()
            x,y = positions[r]
            for d, tgt in self.room_exits.get(r, {}).items():
                if tgt not in positions:
                    dx,dy = dirs.get(d,(0,0))
                    positions[tgt] = (x+dx, y+dy)
                    q.append(tgt)

        # place any unpositioned rooms nearby
        cur_x = 0
        for r in self.rooms:
            if r not in positions:
                cur_x += 1
                positions[r] = (cur_x, 0)

        # draw nodes (with pan/zoom applied)
        w = int(self.canvas.winfo_width() or 800)
        h = int(self.canvas.winfo_height() or 250)
        cell = 140
        cx = w//2 + self.canvas_offset_x
        cy = h//2 + self.canvas_offset_y
        node_coords = {}
        for r, (gx,gy) in positions.items():
            px = cx + int(gx*cell*self.canvas_zoom)
            py = cy + int(gy*cell*self.canvas_zoom)
            node_size = int(50 * self.canvas_zoom)
            nw = px - node_size
            nh = py - int(25 * self.canvas_zoom)
            se = px + node_size
            se_y = py + int(25 * self.canvas_zoom)
            rect = self.canvas.create_rectangle(nw, nh, se, se_y, fill="#444444", outline="#ffffff", width=2, tags=(f"node:{r}",))
            text = self.canvas.create_text(px, py, text=r, fill="#ffffff", tags=(f"node:{r}",))
            node_coords[r] = (px, py)

        # draw edges
        for r, exits in self.room_exits.items():
            src = node_coords.get(r)
            if not src:
                continue
            sx, sy = src
            for d, tgt in exits.items():
                dst = node_coords.get(tgt)
                if not dst:
                    continue
                dx, dy = dst
                self.canvas.create_line(sx, sy, dx, dy, arrow=tk.LAST, fill="#88ff88", width=max(1, int(2*self.canvas_zoom)))

    def on_canvas_button_down(self, event):
        # Check if we clicked on a node
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for it in items:
            tags = self.canvas.gettags(it)
            for t in tags:
                if t.startswith('node:'):
                    name = t.split(':',1)[1]
                    # select in listbox
                    try:
                        idx = list(self.rooms.keys()).index(name)
                    except ValueError:
                        idx = None
                    if idx is not None:
                        self.room_listbox.selection_clear(0, tk.END)
                        self.room_listbox.selection_set(idx)
                        self.room_listbox.see(idx)
                        self.on_room_select(None)
                    self.pan_start = None  # Don't pan if clicked a node
                    return
        # Not on a node, start panning
        self.pan_start = (event.x, event.y)

    def on_pan_motion(self, event):
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas_offset_x += dx
            self.canvas_offset_y += dy
            self.pan_start = (event.x, event.y)
            self.draw_graph()

    def on_pan_end(self, event):
        self.pan_start = None

    def on_canvas_scroll(self, event):
        # Zoom on scroll
        if event.num == 4 or event.delta > 0:  # scroll up
            self.canvas_zoom *= 1.1
        elif event.num == 5 or event.delta < 0:  # scroll down
            self.canvas_zoom /= 1.1
        self.canvas_zoom = max(0.3, min(3.0, self.canvas_zoom))  # clamp
        self.draw_graph()
    
    def refresh_preview(self):
        code = self.generate_python_code()
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", code)
    
    def generate_python_code(self):
        code = "from adventurelib import *\n\n"
        code += "# Rooms\n"

        # sanitize room identifiers
        def safe_id(name):
            import re
            s = re.sub(r"[^0-9a-zA-Z_]", "_", name.strip())
            if not s:
                s = "room"
            if s[0].isdigit():
                s = "r_" + s
            s = s.lower()
            # Avoid generating an identifier that would shadow AdventureLib API
            reserved = {"start", "current_room", "when", "room", "say", "look", "inventory", "items"}
            if s in reserved:
                s = "room_" + s
            return s

        id_map = {room: safe_id(room) for room in self.rooms}
        for room_name, desc in self.rooms.items():
            # Enhance description with available exits and their "ways"
            enhanced_desc = desc
            
            # Add items in this room to description
            items_here = [item for item, loc in self.item_locations.items() if loc == room_name]
            if items_here:
                enhanced_desc += f" Items: {', '.join(items_here)}."
            
            exits = self.room_exits.get(room_name, {})
            if exits:
                exit_parts = []
                for direction in ["north", "south", "east", "west"]:
                    if direction in exits:
                        target = exits[direction]
                        way = self.room_ways.get(target, "passage")
                        exit_parts.append(f"To the {direction} is a {way}")
                if exit_parts:
                    enhanced_desc = enhanced_desc + " " + ". ".join(exit_parts) + "."
            code += f"{id_map[room_name]} = Room(\"{enhanced_desc}\")\n"

        code += "\n# Room connections\n"
        for room, exits in self.room_exits.items():
            for d, tgt in exits.items():
                if room in id_map and tgt in id_map:
                    code += f"{id_map[room]}.{d} = {id_map[tgt]}\n"

        # Initialize current_room to start or first room
        start_room = None
        if 'start' in id_map:
            start_room = id_map['start']
        else:
            # pick the first defined room
            start_room = next(iter(id_map.values())) if id_map else None
        if start_room:
            code += f"\n# Starting room and visited tracking\n"
            code += f"current_room = {start_room}\n"
            code += f"visited_rooms = set()  # Tracks rooms visited for first-time actions\n"
        # Always ensure item_locations exist (used by NPCs/gifts)
        code += "\n# Player inventory and item locations\n"
        code += "item_locations = {}\n"
        # Items and inventory system
        if self.items:
            code += f"\n# Items\n"
            code += f"inventory = set()  # Items player has collected\n"
            code += f"item_descriptions = {{\n"
            for item_name, desc in self.items.items():
                code += f"    \"{item_name}\": \"{desc}\",\n"
            code += f"}}\n"
        # NPC class definitions (user-provided structure)
        if self.npcs:
            code += "\n# NPC classes\n"
            code += "class NPC(Item):\n"
            code += "    name = \"\"\n"
            code += "    words = \"\"\n"
            code += "    detail = \"\"\n"
            code += "    question = \"\"\n"
            code += "    ans = \"\"\n"
            code += "    wrongans = \"\"\n"
            code += "    gift = []\n\n"
            code += "    def ask_question(self):\n"
            code += "        if self.question != \"\":\n"
            code += "            say(f\"{self.name} asks: {self.question}\")\n"
            code += "        else:\n"
            code += "            say(f\"{self.name} says: {self.words}\")\n\n"
            code += "    def check_answer(self, answer):\n"
            code += "        if answer.lower() == self.ans.lower():\n"
            code += "            gifts = self.gift if isinstance(self.gift, list) else ([self.gift] if self.gift else [])\n"
            code += "            if gifts:\n"
            code += "                say(f\"Correct! {self.name} gives you: {', '.join(gifts)}\")\n"
            code += "                for g in gifts:\n"
            code += "                    try:\n"
            code += "                        inventory.add(g)\n"
            code += "                        # remove from room if present\n"
            code += "                        if g in item_locations.get(current_room, []):\n"
            code += "                            item_locations[current_room].remove(g)\n"
            code += "                    except Exception:\n"
            code += "                        pass\n"
            code += "        else:\n"
            code += "            if self.wrongans:\n"
            code += "                say(self.wrongans)\n"
            code += "            else:\n"
            code += "                say(f\"Wrong answer! {self.name} shakes their head sadly.\")\n\n"
            code += "class GirlNPC(NPC):\n"
            code += "    subject_pronoun = \"she\"\n"
            code += "    object_pronoun = \"her\"\n\n"
            code += "class BoyNPC(NPC):\n"
            code += "    subject_pronoun = \"he\"\n"
            code += "    object_pronoun = \"him\"\n\n"

        # Item placements
        if self.items:
            code += f"\n# Item locations (room_id: list of items)\n"
            code += f"item_locations = {{\n"
            items_by_room = {}
            for item_name, room_name in self.item_locations.items():
                if room_name and room_name in id_map:
                    if id_map[room_name] not in items_by_room:
                        items_by_room[id_map[room_name]] = []
                    items_by_room[id_map[room_name]].append(item_name)
            for room_id, items_in_room in items_by_room.items():
                code += f"    {room_id}: {items_in_room},\n"
            code += f"}}\n"

        # Ensure direction_keys exists even when no locks are defined
        code += "\n# Locked direction keys (room: {direction: key_name})\n"
        code += "direction_keys = {}\n"
        if self.room_direction_keys:
            code += f"\n"
            direction_keys_by_room = {}
            for (room_name, direction), key_name in self.room_direction_keys.items():
                if room_name in id_map:
                    if id_map[room_name] not in direction_keys_by_room:
                        direction_keys_by_room[id_map[room_name]] = {}
                    direction_keys_by_room[id_map[room_name]][direction] = key_name
            # overwrite the empty mapping with the real data
            code += f"direction_keys = {{\n"
            for room_id, directions in direction_keys_by_room.items():
                code += f"    {room_id}: {directions},\n"
            code += f"}}\n"
        
        # Add helper function to run first-time entry actions
        if self.room_first_time_commands:
            code += "\ndef handle_first_time_entry():\n"
            code += "    global current_room, visited_rooms\n"
            code += "    room_name = str(current_room)\n"
            code += "    if room_name not in visited_rooms:\n"
            code += "        visited_rooms.add(room_name)\n"
            for room_name, action_code in self.room_first_time_commands.items():
                if room_name in id_map:
                    code += f"        if current_room == {id_map[room_name]}:\n"
                    lines = action_code.split('\n')
                    for line in lines:
                        code += f"            {line}\n"
            code += "\n"

        # NPC instances and interaction commands
        if self.npcs:
            code += "\n# NPC instances\n"
            npc_var_map = {}
            for npc_name, data in self.npcs.items():
                var = safe_id(npc_name)
                # ensure unique var name
                orig = var
                i = 1
                while var in npc_var_map.values():
                    var = f"{orig}_{i}"
                    i += 1
                npc_var_map[npc_name] = var
                code += f"{var} = NPC()\n"
                code += f"{var}.name = \"{npc_name}\"\n"
                code += f"{var}.words = \"{data.get('words','')}\"\n"
                code += f"{var}.detail = \"{data.get('detail','')}\"\n"
                code += f"{var}.question = \"{data.get('question','')}\"\n"
                code += f"{var}.ans = \"{data.get('ans','')}\"\n"
                code += f"{var}.wrongans = \"{data.get('wrongans','')}\"\n"
                gifts = data.get('gift', [])
                code += f"{var}.gift = {gifts}\n\n"

            # Build npc_locations mapping (room_id -> [npc_vars])
            code += "npc_locations = {\n"
            npc_by_room = {}
            for npc_name, room_name in self.npc_locations.items():
                if room_name and room_name in id_map and npc_name in npc_var_map:
                    if id_map[room_name] not in npc_by_room:
                        npc_by_room[id_map[room_name]] = []
                    npc_by_room[id_map[room_name]].append(npc_var_map[npc_name])
            for room_id, npcs_here in npc_by_room.items():
                code += f"    {room_id}: [{', '.join(npcs_here)}],\n"
            code += "}\n\n"

            # last questioned tracking
            code += "last_questioned = None\n\n"
            # ask handlers per-NPC
            for npc_name, var in npc_var_map.items():
                code += f"@when('ask {npc_name}')\n"
                code += f"def ask_{var}():\n"
                code += f"    global last_questioned, current_room\n"
                code += f"    npcs_here = npc_locations.get(current_room, [])\n"
                code += f"    if {var} in npcs_here:\n"
                code += f"        last_questioned = {var}\n"
                code += f"        {var}.ask_question()\n"
                code += f"    else:\n"
                code += f"        say(\"I don't see that here.\")\n\n"

            # generic answer handler
            code += "@when('answer ANSWER')\n"
            code += "def answer_cmd(answer):\n"
            code += "    global last_questioned\n"
            code += "    if last_questioned:\n"
            code += "        last_questioned.check_answer(answer)\n"
            code += "    else:\n"
            code += "        say(\"No one has asked a question.\")\n\n"

            # unified talkto command (all-in-one NPC interaction)
            code += "@when('talkto NAME')\n"
            code += "def talkto_cmd(name):\n"
            code += "    global current_room, inventory\n"
            code += "    npcs_here = npc_locations.get(current_room, [])\n"
            code += "    npc_found = None\n"
            code += "    for npc in npcs_here:\n"
            code += "        if npc.name.lower() == name.lower():\n"
            code += "            npc_found = npc\n"
            code += "            break\n"
            code += "    if npc_found:\n"
            code += "        say(f\"You talk to {npc_found.name}. {npc_found.words}\")\n"
            code += "        if npc_found.question:\n"
            code += "            say(npc_found.question)\n"
            code += "            try:\n"
            code += "                ans = input(\"> \")\n"
            code += "                npc_found.check_answer(ans)\n"
            code += "            except EOFError:\n"
            code += "                say(\"(Conversation ended)\")\n"
            code += "    else:\n"
            code += "        say(f\"I don't see {name} here.\")\n\n"

        # Movement handlers (single unified handler)
        code += "\n# Movement handlers\n"
        
        # Build locked_doors mapping
        code += "# Locked directions (one-way exits)\n"
        code += "locked_doors = {\n"
        for room_name, directions in self.room_locked_directions.items():
            if room_name in id_map:
                code += f"    {id_map[room_name]}: {sorted(list(directions))},\n"
        code += "}\n\n"
        
        # Generate handle_room_entry() function to run entry actions when entering rooms
        if self.room_entry_commands:
            code += "# Room entry actions handler\n"
            code += "def handle_room_entry():\n"
            code += "    global current_room\n"
            for room_name in self.room_entry_commands:
                if room_name in id_map:
                    fn = room_name.lower().replace(' ', '_')
                    code += f"    if current_room == {id_map[room_name]}:\n"
                    code += f"        on_enter_{fn}()\n"
            code += "\n"
        
        # Insert the user's unified go(direction) handler using correct AdventureLib syntax
        code += "# Define movement commands with proper AdventureLib syntax\n"
        if self.items:
            code += "def _go_helper(direction):\n"
            code += "    global current_room, inventory\n"
            code += "    # Check if locked and key from direction_keys mapping\n"
            code += "    if direction in direction_keys.get(current_room, {}):\n"
            code += "        required_key = direction_keys[current_room][direction]\n"
            code += "        if required_key not in inventory:\n"
            code += "            say(f\"That way is locked. You need: {required_key}\")\n"
            code += "            return\n"
            code += "    # Also check generic locked_doors for simple one-way exits\n"
            code += "    elif direction in locked_doors.get(current_room, []):\n"
            code += "        say(\"That way is locked\")\n"
            code += "        return\n"
            code += "    room = current_room.exit(direction)\n"
            code += "    if room:\n"
            code += "        current_room = room\n"
            code += "        say('You go %s.' % direction)\n"
            code += "        say(current_room)\n"
            code += "        room_items = item_locations.get(current_room, [])\n"
            code += "        if room_items:\n"
            code += "            say(f\"You can see: {', '.join(room_items)}\")\n"
            if self.room_entry_commands:
                code += "        try:\n"
                code += "            handle_room_entry()\n"
                code += "        except Exception:\n"
                code += "            pass\n"
            if self.room_first_time_commands:
                code += "        try:\n"
                code += "            handle_first_time_entry()\n"
                code += "        except Exception:\n"
                code += "            pass\n"
            code += "    else:\n"
            code += "        say(\"You can't go that way.\")\n"
            code += "\n"
        else:
            code += "def _go_helper(direction):\n"
            code += "    global current_room\n"
            code += "    if direction in locked_doors.get(current_room, []):\n"
            code += "        say(\"That way is locked\")\n"
            code += "        return\n"
            code += "    room = current_room.exit(direction)\n"
            code += "    if room:\n"
            code += "        current_room = room\n"
            code += "        say('You go %s.' % direction)\n"
            code += "        say(current_room)\n"
            if self.room_entry_commands:
                code += "        try:\n"
                code += "            handle_room_entry()\n"
                code += "        except Exception:\n"
                code += "            pass\n"
            if self.room_first_time_commands:
                code += "        try:\n"
                code += "            handle_first_time_entry()\n"
                code += "        except Exception:\n"
                code += "            pass\n"
            code += "    else:\n"
            code += "        say(\"You can't go that way.\")\n"
            code += "\n"
        
        code += "@when('north')\n"
        code += "def go_north():\n"
        code += "    _go_helper('north')\n"
        code += "\n"
        code += "@when('south')\n"
        code += "def go_south():\n"
        code += "    _go_helper('south')\n"
        code += "\n"
        code += "@when('east')\n"
        code += "def go_east():\n"
        code += "    _go_helper('east')\n"
        code += "\n"
        code += "@when('west')\n"
        code += "def go_west():\n"
        code += "    _go_helper('west')\n"
        code += "\n"
        code += "@when('n')\n"
        code += "def go_n():\n"
        code += "    _go_helper('north')\n"
        code += "\n"
        code += "@when('s')\n"
        code += "def go_s():\n"
        code += "    _go_helper('south')\n"
        code += "\n"
        code += "@when('e')\n"
        code += "def go_e():\n"
        code += "    _go_helper('east')\n"
        code += "\n"
        code += "@when('w')\n"
        code += "def go_w():\n"
        code += "    _go_helper('west')\n"
        code += "\n"
        
        # Add look command
        code += "@when('look')\n"
        code += "@when('l')\n"
        code += "def look_around():\n"
        code += "    global current_room\n"
        code += "    say(current_room)\n"
        if self.items:
            code += "    room_items = item_locations.get(current_room, [])\n"
            code += "    if room_items:\n"
            code += "        say(f\"You can see: {', '.join(room_items)}\")\n"
        code += "\n"

        code += "\n# Commands\n"
        # Movement commands are engine-owned, skip them
        movement_triggers = {
            'north', 'south', 'east', 'west',
            'n', 's', 'e', 'w',
            'go north', 'go south', 'go east', 'go west'
        }
        for trigger in self.commands:
            if trigger in movement_triggers:
                continue  # Skip movement commands; they're engine-owned
            func_name = trigger.replace(' ', '_')
            code += f"@when(\"{trigger}\")\n"
            code += f"def _{func_name}():\n"
            lines = self.commands[trigger].split('\n')
            for line in lines:
                code += f"    {line}\n"
            code += "\n"

        # Items commands (if items exist)
        if self.items:
            code += "# Item commands\n"
            code += "@when('take ITEM')\n"
            code += "def take_item(item):\n"
            code += "    global current_room, inventory\n"
            code += "    room_items = item_locations.get(current_room, [])\n"
            code += "    if item in room_items:\n"
            code += "        inventory.add(item)\n"
            code += "        say(f\"You take the {item}.\")\n"
            code += "        item_locations[current_room].remove(item)\n"
            code += "    else:\n"
            code += "        say(f\"I don't see that here.\")\n"
            code += "\n"
            
            code += "@when('inventory')\n"
            code += "@when('inv')\n"
            code += "def show_inventory():\n"
            code += "    if inventory:\n"
            code += "        say(f\"Inventory: {', '.join(sorted(inventory))}\")\n"
            code += "    else:\n"
            code += "        say(\"You are not carrying anything.\")\n"
            code += "\n"
            
            code += "@when('examine ITEM')\n"
            code += "@when('look at ITEM')\n"
            code += "def examine_item(item):\n"
            code += "    if item in item_descriptions:\n"
            code += "        say(item_descriptions[item])\n"
            code += "    else:\n"
            code += "        say(\"You don't see that.\")\n"
            code += "\n"

        code += "# Room entry action handlers (called by handle_room_entry())\n"
        for room in self.room_entry_commands:
            fn = room.lower().replace(' ', '_')
            code += f"def on_enter_{fn}():\n"
            lines = self.room_entry_commands[room].split('\n')
            for line in lines:
                code += f"    {line}\n"
            code += "\n"

        code += "# Start the game\n"
        if self.room_first_time_commands:
            code += "handle_first_time_entry()  # Run first-time action for starting room\n"
        code += "start()\n"

        return code
    
    def export_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            code = self.generate_python_code()
            with open(file_path, 'w') as f:
                f.write(code)
            messagebox.showinfo("Success", f"Exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdventureLibGUI(root)
    root.mainloop()
