from trezor import ui
from trezor.ui import display


def loader(
    progress: int,  # 0-1000
    # indeterminate: bool,
    yoffset: int = 12,
    height: int = 9,
    width: int = 80,
) -> None:
    loader_x0 = (ui.WIDTH - width) // 2
    loader_y0 = ui.HEIGHT - yoffset - height

    # border
    display.bar(loader_x0, loader_y0, width, height, ui.FG)

    # background
    display.bar(
        loader_x0 + 1,
        loader_y0 + 1,
        width - 2,
        height - 2,
        ui.BG,
    )

    # round corners
    pixels = (
        (loader_x0, loader_y0, ui.BG),
        (loader_x0, loader_y0 + height - 1, ui.BG),
        (loader_x0 + width - 1, loader_y0, ui.BG),
        (loader_x0 + width - 1, loader_y0 + height - 1, ui.BG),
        (loader_x0 + 1, loader_y0 + 1, ui.FG),
        (loader_x0 + 1, loader_y0 + height - 2, ui.FG),
        (loader_x0 + width - 2, loader_y0 + 1, ui.FG),
        (loader_x0 + width - 2, loader_y0 + height - 2, ui.FG),
    )
    for x, y, c in pixels:
        display.bar(x, y, 1, 1, c)

    # bar
    progress_width = progress * (width - 4) // 1000
    display.bar(
        (ui.WIDTH - width) // 2 + 2,
        ui.HEIGHT - yoffset - height + 2,
        progress_width,
        height - 4,
        ui.FG,
    )
