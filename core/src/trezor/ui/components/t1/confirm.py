from trezor import ui

from ..common.confirm import ConfirmBase
from .button import Button, ButtonBlack, ButtonWhite

if False:
    from typing import Optional
    from .button import ButtonContent, ButtonStyleType


class Confirm(ConfirmBase):
    DEFAULT_CONFIRM = "CONFIRM"
    DEFAULT_CONFIRM_STYLE = ButtonWhite
    DEFAULT_CANCEL = "CANCEL"
    DEFAULT_CANCEL_STYLE = ButtonBlack

    def __init__(
        self,
        content: ui.Component,
        confirm: Optional[ButtonContent] = DEFAULT_CONFIRM,
        confirm_style: ButtonStyleType = DEFAULT_CONFIRM_STYLE,
        cancel: Optional[ButtonContent] = DEFAULT_CANCEL,
        cancel_style: ButtonStyleType = DEFAULT_CANCEL_STYLE,
    ) -> None:
        button_confirm = None  # type: Optional[Button]
        button_cancel = None  # type: Optional[Button]

        if confirm is not None:
            button_confirm = Button(True, confirm, confirm_style)
            button_confirm.on_click = self.on_confirm  # type: ignore

        if cancel is not None:
            button_cancel = Button(False, cancel, cancel_style)
            button_cancel.on_click = self.on_cancel  # type: ignore

        super().__init__(content, button_confirm, button_cancel)


# class HoldToConfirm(ui.Layout):
#    DEFAULT_CONFIRM = "Hold to confirm"
#    DEFAULT_CONFIRM_STYLE = ButtonConfirm
#    DEFAULT_LOADER_STYLE = LoaderDefault
#
#    def __init__(
#        self,
#        content: ui.Component,
#        confirm: str = DEFAULT_CONFIRM,
#        confirm_style: ButtonStyleType = DEFAULT_CONFIRM_STYLE,
#        loader_style: LoaderStyleType = DEFAULT_LOADER_STYLE,
#        cancel: bool = True,
#    ):
#        super().__init__()
#        self.content = content
#
#        self.loader = Loader(loader_style)
#        self.loader.on_start = self._on_loader_start  # type: ignore
#
#        if cancel:
#            self.confirm = Button(ui.grid(17, n_x=4, cells_x=3), confirm, confirm_style)
#        else:
#            self.confirm = Button(ui.grid(4, n_x=1), confirm, confirm_style)
#        self.confirm.on_press_start = self._on_press_start  # type: ignore
#        self.confirm.on_press_end = self._on_press_end  # type: ignore
#        self.confirm.on_click = self._on_click  # type: ignore
#
#        self.cancel = None
#        if cancel:
#            self.cancel = Button(
#                ui.grid(16, n_x=4), res.load(ui.ICON_CANCEL), ButtonAbort
#            )
#            self.cancel.on_click = self.on_cancel  # type: ignore
#
#    def _on_press_start(self) -> None:
#        self.loader.start()
#
#    def _on_press_end(self) -> None:
#        self.loader.stop()
#
#    def _on_loader_start(self) -> None:
#        # Loader has either started growing, or returned to the 0-position.
#        # In the first case we need to clear the content leftovers, in the latter
#        # we need to render the content again.
#        ui.display.bar(0, 0, ui.WIDTH, ui.HEIGHT - 58, ui.BG)
#        self.content.dispatch(ui.REPAINT, 0, 0)
#
#    def _on_click(self) -> None:
#        if self.loader.elapsed_ms() >= self.loader.target_ms:
#            self.on_confirm()
#
#    def dispatch(self, event: int, x: int, y: int) -> None:
#        if self.loader.start_ms is not None:
#            if utils.DISABLE_ANIMATION:
#                self.on_confirm()
#            self.loader.dispatch(event, x, y)
#        else:
#            self.content.dispatch(event, x, y)
#        self.confirm.dispatch(event, x, y)
#        if self.cancel:
#            self.cancel.dispatch(event, x, y)
#
#    def on_confirm(self) -> None:
#        raise ui.Result(CONFIRMED)
#
#    def on_cancel(self) -> None:
#        raise ui.Result(CANCELLED)
#
#    if __debug__:
#
#        def read_content(self) -> list[str]:
#            return self.content.read_content()
#
#        def create_tasks(self) -> tuple[loop.Task, ...]:
#            from apps.debug import confirm_signal
#
#            return super().create_tasks() + (confirm_signal(),)
