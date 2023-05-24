import tkinter as tk
from typing import Any, Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

SEED_MAP = {
    "Potato Seed": PotatoPlant,
    "Kale Seed": KalePlant,
    "Berry Seed": BerryPlant,
}


class InfoBar(AbstractGrid):
    """REWRITE
    It is a grid with 2 rows and 3 columns, which displays information to the
    user about the number of days elapsed in the game, as well as the player’s
    energy and health. The InfoBar should span the entire width of the farm and
    inventory combined.
    """

    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """REWRITE
        Sets up the InfoBar to be an AbstractGrid with the appropriate number of
        rows and columns, and the appropriate width and height (see constants)
        """

        super().__init__(
            master,
            (2, 3),
            (FARM_WIDTH + INVENTORY_WIDTH, INFO_BAR_HEIGHT),
        )
        self.redraw(0, 0, 0)

    def _create_label(
        self, grid_position: tuple[int, int], text: str, amount: str
    ) -> None:
        """REWRITE
        Creates an info label with the given text and amount.

        'text' is placed in the given grid position and 'amount' is placed in
        the subsequent row.
        """
        mid_x, mid_y = self.get_midpoint(grid_position)

        self.create_text(mid_x, mid_y, text=text, font=HEADING_FONT)

        mid_x, mid_y = self.get_midpoint(
            (grid_position[0] + 1, grid_position[1])
        )

        self.create_text(mid_x, mid_y, text=amount)

    def redraw(self, day: int, money: int, energy: int) -> None:
        """REWRITE
        Clears the InfoBar and redraws it to display the provided day, money,
        and energy. E.g. in Figure 3, this method was called with day = 1,
        money = 0, and energy = 100.
        """

        self.clear()
        self._create_label((0, 0), "Day:", str(day))
        self._create_label((0, 1), "Money:", f"${money}")
        self._create_label((0, 2), "Energy:", str(energy))


class FarmView(AbstractGrid):
    """REWRITE
    FarmView should inherit from AbstractGrid (see a3 support.py). The FarmView
    is a grid dis- playing the farm map, player, and plants. An example of a
    completed FarmView is shown in Figure 4. The methods you must implement in
    this class are:
    - init (self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int],
        size: tuple[int, int], **kwargs) -> None: Sets up the FarmView to be an
        AbstractGrid with the appropriate dimensions and size, and creates an
        instance attribute of an empty dictionary to be used as an image cache.
    - redraw(self, ground: list[str], plants: dict[tuple[int, int], ‘Plant’],
        player position: tuple[int, int], player direction: str) -> None: Clears
        the farm view, then creates (on the FarmView instance) the images for
        the ground, then the plants, then the player. That is, the player and
        plants should render in front of the ground, and the player should
        render in front of the plants. You must use the get image function
        from a3 support.py to create your images.
    """

    def __init__(
        self,
        master: tk.Tk | tk.Frame,
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs,
    ) -> None:
        """REWRITE
        Sets up the FarmView to be an AbstractGrid with the appropriate
        dimensions and size, and creates an instance attribute of an empty
        dictionary to be used as an image cache.
        """

        super().__init__(master, dimensions, size, **kwargs)
        self._image_cache = {}

    def redraw(
        self,
        ground: list[str],
        plants: dict[tuple[int, int], "Plant"],
        player_position: tuple[int, int],
        player_direction: str,
    ) -> None:
        """REWRITE
        Clears the farm view, then creates (on the FarmView instance) the images
        for the ground, then the plants, then the player. That is, the player
        and plants should render in front of the ground, and the player should
        render in front of the plants. You must use the get image function from
        a3 support.py to create your images.
        """
        self.clear()

        # Draw ground
        ground_type_map = {"G": "grass", "S": "soil", "U": "untilled_soil"}
        for row, ground_row in enumerate(ground):
            for col, ground_type in enumerate(ground_row):
                ground_type = ground_type_map[ground_type]
                if ground_type not in self._image_cache:
                    self._image_cache[ground_type] = get_image(
                        f"images/{ground_type}.png", self.get_cell_size()
                    )
                image = self._image_cache[ground_type]
                self.create_image(self.get_midpoint((row, col)), image=image)

        # Draw plants
        for position, plant in plants.items():
            path = get_plant_image_name(plant)
            if path not in self._image_cache:
                self._image_cache[path] = get_image(
                    f"images/{get_plant_image_name(plant)}",
                    self.get_cell_size(),
                )
            image = self._image_cache[path]
            self.create_image(self.get_midpoint(position), image=image)

        # Draw player
        direction_map = {"UP": "w", "DOWN": "s", "LEFT": "a", "RIGHT": "d"}
        # player_direction = direction_map[player_direction]
        if player_direction not in self._image_cache:
            self._image_cache[player_direction] = get_image(
                f"images/player_{player_direction}.png", self.get_cell_size()
            )
        image = self._image_cache[player_direction]
        self.create_image(self.get_midpoint(player_position), image=image)


class ItemView(tk.Frame):
    """REWRITE
    ItemView should inherit from tk.Frame. The ItemView is a frame displaying
    relevant information and buttons for a single item. There are 6 items
    available in the game (see the ITEMS constant in constants.py).
    """

    def __init__(
        self,
        master: tk.Frame,
        item_name: str,
        amount: int,
        select_command: Optional[Callable[[str], None]] = None,
        sell_command: Optional[Callable[[str], None]] = None,
        buy_command: Optional[Callable[[str], None]] = None,
    ) -> None:
        """REWRITE
        Sets up ItemView to operate as a tk.Frame, and creates all internal
        widgets. Sets the commands for the buy and sell buttons to the buy
        command and sell command each called with the appropriate item name
        respectively. Binds the select command to be called with the appropriate
        item name when either the ItemView frame or label is left clicked. Note:
        The three callbacks are type-hinted as Optional to allow you to pass in
        None if you have not yet implemented these callbacks (i.e. when
        developing, just pass None to begin with, and hookup the functionality
        once you’ve completed the rest of the tasks; see Section 5)."""
        super().__init__(
            master,
            width=INVENTORY_WIDTH,
            height=FARM_WIDTH // len(ITEMS),
            relief="raised",
            borderwidth=2,
            # highlightbackground=INVENTORY_OUTLINE_COLOUR,
            # highlightthickness=2,
        )
        self.pack_propagate(False)
        self._item_name = item_name
        self._amount = amount
        self._select_command = select_command
        self._buy_command = buy_command
        self._sell_command = sell_command

        if self._select_command is not None:
            self.bind("<Button-1>", self._selected)

        self._label_stack = tk.Frame(self)
        self._label_stack.pack(side="left")

        self._item_label = tk.Label(self._label_stack, fg="black")
        self._sell_label = tk.Label(
            self._label_stack,
            text=f"Sell price: ${SELL_PRICES[self._item_name]}",
            fg="black",
        )
        buy_price = (
            BUY_PRICES[self._item_name]
            if self._item_name in BUY_PRICES
            else "N/A"
        )
        self._buy_label = tk.Label(
            self._label_stack, text=f"Buy price: ${buy_price}", fg="black"
        )

        for label in [self._item_label, self._sell_label, self._buy_label]:
            label.pack(fill="x")
            label.bind("<Button-1>", self._selected)

        if self._item_name in BUY_PRICES:
            self._buy_button = tk.Button(self, text="Buy", command=self._buy)
            self._buy_button.pack(side="left")

        self._sell_button = tk.Button(self, text="Sell", command=self._sell)
        self._sell_button.pack(side="left")

        # Convenience list of all sub-widgets, for use when updating colours
        self._sub_widgets: list[tk.Label | tk.Button] = [
            self._item_label,
            self._sell_label,
            self._buy_label,
            self._sell_button,
        ]

        if self._item_name in BUY_PRICES:
            self._sub_widgets.append(self._buy_button)

        self.update(self._amount)

    def update(self, amount: int, selected: bool = False) -> None:
        """REWRITE
        Updates the ItemView to display the new amount of the item, and if
        selected is True, the ItemView should be highlighted (i.e. the
        background colour should be changed to yellow)."""
        self._amount = amount
        self._item_label.config(text=f"{self._item_name}: {self._amount}")

        if self._amount <= 0:
            new_colour = INVENTORY_EMPTY_COLOUR
        elif not selected:
            new_colour = INVENTORY_COLOUR
        else:
            new_colour = INVENTORY_SELECTED_COLOUR

        self.config(bg=new_colour)
        for widget in self._sub_widgets:
            widget.config(bg=new_colour, highlightbackground=new_colour)

    def _selected(self, _: tk.Event) -> None:
        """REWRITE
        Called when the ItemView is selected (i.e. when the ItemView is left
        clicked). Calls the select command with the item name."""
        if self._select_command is not None:
            self._select_command(self._item_name)

    def _buy(self) -> None:
        """REWRITE
        Called when the buy button is pressed. Calls the buy command with the
        item name."""
        if self._buy_command is not None:
            self._buy_command(self._item_name)

    def _sell(self) -> None:
        """REWRITE
        Called when the sell button is pressed. Calls the sell command with the
        item name."""
        if self._sell_command is not None:
            self._sell_command(self._item_name)

    def get_item_name(self):
        return self._item_name


class FarmGame:
    """REWRITE
    FarmGame is the controller class for the overall game. The controller is
    responsible for creating and maintaining instances of the model and view
    classes, event handling, and facilitating communi- cation between the model
    and view classes.
    """

    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """REWRITE
        Sets up the FarmGame. This includes the following steps:
        – Set the title of the window.
        – Create the title banner (you must use get image).
        – Create the FarmModel instance.
        – Create the instances of your view classes, and ensure they display in
            the format shown in Figure 1.
        – Create a button to enable users to increment the day, which should
            have the text ‘Next day’ and be displayed below the other view
            classes. When this button is pressed, the model should advance to
            the next day, and then the view classes should be redrawn to reflect
            the changes in the model.
        – Bind the handle keypress method to the ‘<KeyPress>’ event.
        – Call the redraw method to ensure the view draws according to the
            current model state.
        """

        self._master = master
        self._master.title("Farm Game")

        self._model = FarmModel(map_file)

        self._selected_item: str | None = None

        self._title_banner_img = get_image(
            "images/header.png", (FARM_WIDTH + INVENTORY_WIDTH, BANNER_HEIGHT)
        )
        self._title_banner_label = tk.Label(
            self._master, image=self._title_banner_img
        )
        self._title_banner_label.pack(side="top")

        # A structural frame to help align the farm view and item views
        self._game_stack = tk.Frame(self._master)
        self._game_stack.pack(side="top", fill="x", expand=True)

        self._farm_view = FarmView(
            self._game_stack,
            self._model.get_dimensions(),
            (FARM_WIDTH, FARM_WIDTH),
        )
        self._farm_view.pack(side="left")

        self._item_view_stack = tk.Frame(self._game_stack)
        self._item_view_stack.pack(side="right", anchor="n")

        self._item_views: list[ItemView] = []
        player_inventory = self._model.get_player().get_inventory()
        for item in ITEMS:
            self._item_views.append(
                ItemView(
                    self._item_view_stack,
                    item,
                    player_inventory[item] if item in player_inventory else 0,
                    self.select_item,
                    self.sell_item,
                    self.buy_item,
                )
            )
            if ITEMS.index(item) == 0:
                self._model.get_player().select_item(item)
            self._item_views[-1].pack(side="top")

        self._day_button = tk.Button(
            self._master, text="Next day", command=self._next_day
        )
        self._day_button.pack(side="bottom")

        self._info_bar = InfoBar(self._master)
        self._info_bar.pack(side="bottom")

        self.redraw()

        # bind keypress
        self._master.bind("<KeyPress>", self.handle_keypress)

    def handle_keypress(self, event: tk.Event) -> None:
        player = self._model.get_player()
        inventory = player.get_inventory()
        player_pos = self._model.get_player_position()

        if event.char == "w":
            self._model.move_player("w")
        elif event.char == "a":
            self._model.move_player("a")
        elif event.char == "s":
            self._model.move_player("s")
        elif event.char == "d":
            self._model.move_player("d")

        elif event.char == "p":
            selected = self._model.get_player().get_selected_item()
            if (
                selected is not None
                and selected in SEED_MAP
                and selected in inventory
                and inventory[selected] > 0
                and not player_pos in self._model.get_plants()
                and self._model.get_map()[player_pos[0]][player_pos[1]] == SOIL
            ):
                self._model.add_plant(
                    self._model.get_player_position(), SEED_MAP[selected]()
                )
                player.remove_item((selected, 1))
        elif event.char == "h":
            harvest_result = self._model.harvest_plant(
                self._model.get_player_position()
            )
            if harvest_result is not None:
                player.add_item(harvest_result)
        elif event.char == "r":
            self._model.remove_plant(self._model.get_player_position())
        elif event.char == "t":
            self._model.till_soil(self._model.get_player_position())
        elif event.char == "u":
            self._model.untill_soil(self._model.get_player_position())
        else:
            # We don't need to redraw if nothing happened
            return

        self.redraw()

    def _next_day(self) -> None:
        """REWRITE
        Advances the model to the next day, and redraws the views.
        """
        self._model.new_day()
        self.redraw()

    def redraw(self) -> None:
        """REWRITE
        Redraws the entire game based on the current model state
        """

        player = self._model.get_player()
        self._info_bar.redraw(
            self._model.get_days_elapsed(),
            player.get_money(),
            player.get_energy(),
        )

        self._farm_view.redraw(
            self._model.get_map(),
            self._model.get_plants(),
            self._model.get_player_position(),
            self._model.get_player_direction(),
        )

        for item_view in self._item_views:
            item_name = item_view.get_item_name()
            item_view.update(
                player.get_inventory()[item_name]
                if item_name in player.get_inventory()
                else 0,
                player.get_selected_item() == item_name,
            )

    def select_item(self, item_name: str):
        self._model.get_player().select_item(item_name)
        self.redraw()

    def buy_item(self, item_name: str):
        player = self._model.get_player()
        player.buy(item_name, BUY_PRICES[item_name])
        self.redraw()

    def sell_item(self, item_name: str):
        player = self._model.get_player()
        player.sell(item_name, SELL_PRICES[item_name])
        self.redraw()


def play_game(root: tk.Tk, map_file: str) -> None:
    """REWRITE
        The play game function should be fairly short. You should:
    1. Construct the controller instance using given map file and the root tk.Tk
        parameter.
    2. Ensure the root window stays opening listening for events (using
        mainloop).
    """

    game = FarmGame(root, map_file)
    root.mainloop()


def main() -> None:
    """REWRITE
    The main function should:
    Construct the root tk.Tk instance.
    Call the play game function passing in the newly created root tk.Tk
    instance, and the path
    to any map file you like (e.g. ‘maps/map1.txt’)."""

    root = tk.Tk()

    WINDOW_WIDTH = FARM_WIDTH + INVENTORY_WIDTH
    WINDOW_HEIGHT = BANNER_HEIGHT + FARM_WIDTH + INFO_BAR_HEIGHT + 30

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

    play_game(root, "maps/map1.txt")


if __name__ == "__main__":
    main()
