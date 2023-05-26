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
    """A class representing the information bar in the game.

    An instance of InfoBar displays the current day, money, and energy."""

    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """
        Initialise the InfoBar.

        Initialises the InfoBar as a 2x3 AbstractGrid and draws the initial values.

        Args:
            master (tk.Tk | tk.Frame): The parent widget for the InfoBar.
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
        """
        Create a label with text and amount at the specified grid position.

        The text is placed at the specified grid position and the amount is
        placed on the row below.

        Args:
            grid_position (tuple[int, int]): The grid position of the label.
            text (str): The text to display.
            amount (str): The amount to display.
        """
        mid_x, mid_y = self.get_midpoint(grid_position)

        self.create_text(mid_x, mid_y, text=text, font=HEADING_FONT)

        mid_x, mid_y = self.get_midpoint(
            (grid_position[0] + 1, grid_position[1])
        )

        self.create_text(mid_x, mid_y, text=amount)

    def redraw(self, day: int, money: int, energy: int) -> None:
        """
        Redraw the information bar with the specified values.

        Args:
            day (int): The current day.
            money (int): The amount of money.
            energy (int): The amount of energy.
        """
        self.clear()
        self._create_label((0, 0), "Day:", str(day))
        self._create_label((0, 1), "Money:", f"${money}")
        self._create_label((0, 2), "Energy:", str(energy))


class FarmView(AbstractGrid):
    """A class representing the farm view in the game.

    The FarmView handles displaying the ground, plants, and player."""

    def __init__(
        self,
        master: tk.Tk | tk.Frame,
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs,
    ) -> None:
        """
        Initialise the FarmView.

        Args:
            master (tk.Tk | tk.Frame): The parent widget for the FarmView.
            dimensions (tuple[int, int]): The dimensions of the farm.
            size (tuple[int, int]): The size of the farm view.
            **kwargs: Additional keyword arguments for the AbstractGrid.
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
        """
        Redraw the farm view with the specified values.

        Args:
            ground (list[str]): The ground layout.
            plants (dict[tuple[int, int], "Plant"]): The dictionary of plant positions and objects.
            player_position (tuple[int, int]): The player's position.
            player_direction (str): The player's direction.
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
        if player_direction not in self._image_cache:
            self._image_cache[player_direction] = get_image(
                f"images/player_{player_direction}.png", self.get_cell_size()
            )
        image = self._image_cache[player_direction]
        self.create_image(self.get_midpoint(player_position), image=image)


class ItemView(tk.Frame):
    """A class representing a single item view in the inventory.

    Each ItemView displays an item name and amount, sell and buy price (if
    applicable), can be selected and has a button to buy or sell the item (if
    applicable).
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
        """
        Initialize the ItemView.

        Args:
            master (tk.Frame): The master tkinter frame.
            item_name (str): The name of the item.
            amount (int): The amount of the item.
            select_command (Optional[Callable[[str], None]], optional): The
                select command callback. Defaults to None.
            sell_command (Optional[Callable[[str], None]], optional): The sell
                command callback. Defaults to None.
            buy_command (Optional[Callable[[str], None]], optional): The buy
                command callback. Defaults to None.
        """
        super().__init__(
            master,
            width=INVENTORY_WIDTH,
            height=FARM_WIDTH // len(ITEMS),
            relief="raised",
            borderwidth=2,
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
        self._sub_widgets: list[tk.Label | tk.Frame] = [
            self._label_stack,
            self._item_label,
            self._sell_label,
            self._buy_label,
        ]

        self.update(self._amount)

    def update(self, amount: int, selected: bool = False) -> None:
        """
        Update the item view with the specified amount.

        Args:
            amount (int): The new amount of the item.
            selected (bool, optional): Whether the item is currently selected.
                Defaults to False.
        """
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
        """Handle the item being selected."""
        if self._select_command is not None:
            self._select_command(self._item_name)

    def _buy(self) -> None:
        """Handle the item being bought."""
        if self._buy_command is not None:
            self._buy_command(self._item_name)

    def _sell(self) -> None:
        """Handle the item being sold."""
        if self._sell_command is not None:
            self._sell_command(self._item_name)

    def get_item_name(self):
        """
        Get the name of the item.

        Returns:
            str: The name of the item.
        """
        return self._item_name


class FarmGame:
    """The controller class for the overall game.

    The FarmGame class is responsible for creating the model and view classes
    and handling the main game loop."""

    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """
        Initialize the FarmGame.

        Args:
            master (tk.Tk): The master Tk widget for the FarmGame to instansiate
                views into.
            map_file (str): The file path to the map.
        """
        self._master = master
        self._master.title("Farm Game")

        self._model = FarmModel(map_file)

        # Retrieve and display the header banner
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

        # Instansiate and pack the farm view
        self._farm_view = FarmView(
            self._game_stack,
            self._model.get_dimensions(),
            (FARM_WIDTH, FARM_WIDTH),
        )
        self._farm_view.pack(side="left")

        # A structural frame to help align the item views
        self._item_view_stack = tk.Frame(self._game_stack)
        self._item_view_stack.pack(side="right", anchor="n")

        # Instansiate and pack the item views
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
            self._item_views[-1].pack(side="top")

        # Create and pack the day button
        self._day_button = tk.Button(
            self._master, text="Next day", command=self._next_day
        )
        self._day_button.pack(side="bottom")

        # Instansiate and pack the info bar
        self._info_bar = InfoBar(self._master)
        self._info_bar.pack(side="bottom")

        # Redraw t o encsure everything is drawn with the correct information
        # from frame 1
        self.redraw()

        # Bind keypress
        self._master.bind("<KeyPress>", self.handle_keypress)

    def handle_keypress(self, event: tk.Event) -> None:
        """
        Handle keypress events.

        Args:
            event (tk.Event): The keypress event.
        """
        player = self._model.get_player()
        inventory = player.get_inventory()
        player_pos = self._model.get_player_position()

        # Handle movement
        if event.char == "w":
            self._model.move_player("w")
        elif event.char == "a":
            self._model.move_player("a")
        elif event.char == "s":
            self._model.move_player("s")
        elif event.char == "d":
            self._model.move_player("d")

        # Handle farming actions
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
        """Advance model to the next day and redraw views."""
        self._model.new_day()
        self.redraw()

    def redraw(self) -> None:
        """Redraw all views with latest information from the model."""
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
        """
        Selection callback for ItemViews.

        Handles selecting the relevant item in the player's inventory.

        Args:
            item_name (str): The name of the item to select.
        """
        self._model.get_player().select_item(item_name)
        self.redraw()

    def buy_item(self, item_name: str):
        """
        Buying callback for ItemViews.

        Handles purchasing the relevant item and adding it to the player's
        inventory.

        Args:
            item_name (str): The name of the item to buy.
        """
        player = self._model.get_player()
        player.buy(item_name, BUY_PRICES[item_name])
        self.redraw()

    def sell_item(self, item_name: str):
        """
        Selling callback for ItemViews.

        Handles selling the relevant item from the player's inventory.

        Args:
            item_name (str): The name of the item to sell.
        """
        player = self._model.get_player()
        player.sell(item_name, SELL_PRICES[item_name])
        self.redraw()


def play_game(root: tk.Tk, map_file: str) -> None:
    """
    Play the farm game.

    Args:
        root (tk.Tk): The root tkinter window.
        map_file (str): The file path to the map.
    """
    game = FarmGame(root, map_file)
    root.mainloop()


def main() -> None:
    """
    Entry point of the farm game program.

    Creates a Tkinter root window, sets the window dimensions, and launches the game.
    The game is played using the map file "maps/map1.txt".
    """
    root = tk.Tk()

    WINDOW_WIDTH = FARM_WIDTH + INVENTORY_WIDTH
    WINDOW_HEIGHT = BANNER_HEIGHT + FARM_WIDTH + INFO_BAR_HEIGHT + 30

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

    play_game(root, "maps/map1.txt")


if __name__ == "__main__":
    main()
