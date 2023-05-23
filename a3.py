import tkinter as tk
from typing import Any, Callable, Union, Optional
from typing_extensions import Literal
from a3_support import *
from model import *
from constants import *

# Implement your classes here


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
        **kwargs
    ) -> None:
        """REWRITE
        Sets up the FarmView to be an AbstractGrid with the appropriate
        dimensions and size, and creates an instance attribute of an empty
        dictionary to be used as an image cache.
        """

        super().__init__(master, dimensions, size, **kwargs)
        self._image_cache = {}


class ItemView(tk.Frame):
    """REWRITE
    ItemView should inherit from tk.Frame. The ItemView is a frame displaying relevant information and buttons for a single item. There are 6 items available in the game (see the ITEMS constant in constants.py).
    """

    def __init__(
        self,
        master: tk.Frame,
        item_name: str,
        amoutn: int,
        select_command: Optional[Callable[[str], None]] = None,
        sell_command: Optional[Callable[[str], None]] = None,
        buy_command: Optional[Callable[[str], None]] = None,
    ) -> None:
        """REWRITE
        Sets up ItemView to operate as a tk.Frame, and creates all internal
        widgets. Sets the com- mands for the buy and sell buttons to the buy
        command and sell command each called with the appropriate item name
        respectively. Binds the select command to be called with the appropriate
        item name when either the ItemView frame or label is left clicked. Note:
        The three callbacks are type-hinted as Optional to allow you to pass in
        None if you have not yet implemented these callbacks (i.e. when
        developing, just pass None to begin with, and hookup the functionality
        once you’ve completed the rest of the tasks; see Section 5)."""
        super().__init__(master)
        self._item_name = item_name
        self._amount = amoutn
        self._select_command = select_command
        self._buy_command = buy_command
        self._sell_command = sell_command
        self._create_widgets()
        self._create_bindings()

    def _create_widgets(self) -> None:
        pass

    def _create_bindings(self) -> None:
        pass


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
        self._title_banner_img = get_image("images/header.png", (880, 205))
        self._title_banner_label = tk.Label(
            self._master, image=self._title_banner_img
        )
        self._model = FarmModel(map_file)
        self.redraw()
        # self._farm_view = FarmView(
        #     self._master, self._model.get_dimensions(), (80, 80)
        # )
        # self._item_view = ItemView(self._master, "item", 0)
        # self._store_view = StoreView(self._master, self._model.get_store())
        # self._day_button = tk.Button(
        #     self._master, text="Next day", command=self._next_day
        # )

    def redraw(self) -> None:
        """REWRITE
        Redraws the entire game based on the current model state
        """

        # Pack title banner
        self._title_banner_label.pack(side="top")


def play_game(root: tk.Tk, map_file: str) -> None:
    """REWRITE
        The play game function should be fairly short. You should:
    1. Construct the controller instance using given map file and the root tk.Tk parameter.
    2. Ensure the root window stays opening listening for events (using mainloop).
    """

    game = FarmGame(root, map_file)
    root.mainloop()


def main() -> None:
    """REWRITE
    The main function should:
    Construct the root tk.Tk instance.
    Call the play game function passing in the newly created root tk.Tk instance, and the path
    to any map file you like (e.g. ‘maps/map1.txt’)."""

    root = tk.Tk()
    play_game(root, "maps/map1.txt")


if __name__ == "__main__":
    main()
