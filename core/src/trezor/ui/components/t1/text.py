from trezor import ui
from trezor.ui import display, style

from ..common.text import (  # noqa: F401
    BR,
    BR_HALF,
    TEXT_LINE_HEIGHT,
    TEXT_MAX_LINES,
    TextBase,
    render_text,
)


def header(title: str, fg: int = style.FG, bg: int = style.BG) -> None:
    display.text(0, 7, title, ui.BOLD, fg, bg)
    for x in range(0, ui.WIDTH, 2):
        display.bar(x, 9, 1, 1, ui.FG)


class Text(TextBase):
    NO_HEADER_TEXT_Y = TEXT_LINE_HEIGHT - 2

    def on_render(self) -> None:
        if self.repaint:
            if self.header_text:
                header(self.header_text, ui.TITLE_GREY, ui.BG)
                render_text(self.content, self.new_lines, self.max_lines)
            else:
                render_text(
                    self.content,
                    self.new_lines,
                    self.max_lines,
                    offset_y=self.NO_HEADER_TEXT_Y,
                )
            self.repaint = False
