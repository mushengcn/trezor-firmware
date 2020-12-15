from micropython import const

from trezor import ui, wire
from trezor.enums import ButtonRequestType
from trezor.ui.qr import Qr
from trezor.utils import chunks

from ..components.common import break_path_to_lines
from ..components.common.confirm import is_confirmed, raise_if_cancelled
from ..components.t1.confirm import Confirm
from ..components.t1.text import Text
from ..constants.t1 import (
    MONO_CHARS_PER_LINE,
    MONO_HEX_PER_LINE,
    QR_SIZE_THRESHOLD,
    QR_X,
    QR_Y,
    TEXT_MAX_LINES,
)
from .common import interact

if False:
    from typing import Any, Iterator, Sequence, Union

    from trezor import wire
    from trezor.messages.ButtonRequest import EnumTypeButtonRequestType

    from .common import LayoutType

    ExceptionType = Union[BaseException, Type[BaseException]]


async def confirm_action(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    action: str | None = None,
    description: str | None = None,
    description_param: str | None = None,
    description_param_font: int = ui.BOLD,
    verb: str | bytes | None = Confirm.DEFAULT_CONFIRM,
    verb_cancel: str | bytes | None = Confirm.DEFAULT_CANCEL,
    hold: bool = False,
    hold_danger: bool = False,
    icon: str | None = None,  # TODO cleanup @ redesign
    icon_color: int | None = None,  # TODO cleanup @ redesign
    reverse: bool = False,  # TODO cleanup @ redesign
    larger_vspace: bool = False,  # TODO cleanup @ redesign
    exc: ExceptionType = wire.ActionCancelled,
    br_code: ButtonRequestType = ButtonRequestType.Other,
) -> None:
    text = Text(title.upper(), new_lines=False)

    if reverse and description is not None:
        text.format_parametrized(
            description,
            description_param if description_param is not None else "",
            param_font=description_param_font,
        )
    elif action is not None:
        text.bold(action)

    if action is not None and description is not None:
        text.br()
        if larger_vspace:
            text.br_half()

    if reverse and action is not None:
        text.bold(action)
    elif description is not None:
        text.format_parametrized(
            description,
            description_param if description_param is not None else "",
            param_font=description_param_font,
        )

    cls = Confirm
    if hold:
        # cls = HoldToConfirm
        if verb == Confirm.DEFAULT_CONFIRM and verb_cancel == Confirm.DEFAULT_CANCEL:
            verb = "HOLD TO CONFIRM"
            verb_cancel = "X"
    kwargs = {}
    if hold_danger:
        # kwargs = {"loader_style": LoaderDanger, "confirm_style": ButtonCancel}
        pass
    await raise_if_cancelled(
        interact(
            ctx,
            cls(text, confirm=verb, cancel=verb_cancel, **kwargs),
            br_type,
            br_code,
        ),
        exc,
    )


async def confirm_reset_device(ctx: wire.GenericContext, prompt: str) -> None:
    text = Text(None, new_lines=False)
    if prompt:
        text.bold(prompt.replace("\n", " "))  # FIXME
        text.br()
    text.br_half()
    text.normal("By continuing you agree")
    text.br()
    text.normal("to ")
    text.bold("trezor.io/tos")
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text, confirm="CREATE"),
            "setup_device",
            ButtonRequestType.ResetDevice,
        )
    )


async def confirm_backup(ctx: wire.GenericContext) -> bool:
    text1 = Text(None)
    text1.bold("New wallet created", "successfully!")
    text1.br_half()
    text1.normal("You should back up your", "new wallet right now.")

    text2 = Text("Skip the backup?")  # new_lines=False?
    text2.normal("You can back up ", "your Trezor once, ", "at any time.")

    if is_confirmed(
        await interact(
            ctx,
            Confirm(text1, cancel="NO", confirm="BACKUP"),
            "backup_device",
            ButtonRequestType.ResetDevice,
        )
    ):
        return True

    confirmed = is_confirmed(
        await interact(
            ctx,
            Confirm(text2, cancel="NO", confirm="BACKUP"),
            "backup_device",
            ButtonRequestType.ResetDevice,
        )
    )
    return confirmed


async def confirm_path_warning(ctx: wire.GenericContext, path: str) -> None:
    text = Text("WRONG ADDRESS PATH")
    text.mono(*break_path_to_lines(path, MONO_CHARS_PER_LINE))
    text.br_half()
    text.normal("Are you sure?")
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text),
            "path_warning",
            ButtonRequestType.UnknownDerivationPath,
        )
    )


def _show_qr(
    address: str,
) -> Confirm:
    QR_COEF = 2 if len(address) < QR_SIZE_THRESHOLD else 1
    qr = Qr(address, QR_X, QR_Y, QR_COEF)

    return Confirm(qr, confirm="CONTINUE", cancel="")


def _split_address(address: str) -> Iterator[str]:
    return chunks(address, MONO_CHARS_PER_LINE)


def _truncate_hex(
    hex_data: str,
    lines: int = TEXT_MAX_LINES,
    width: int = MONO_HEX_PER_LINE,
    middle: bool = False,
) -> Iterator[str]:
    if len(hex_data) >= width * lines:
        if middle:
            hex_data = (
                hex_data[: lines * width // 2 - 1]
                + "..."
                + hex_data[-lines * width // 2 + 2 :]
            )
        else:
            hex_data = hex_data[: (width * lines - 3)] + "..."
    return chunks(hex_data, width)


def _show_address(
    address: str,
    desc: str,
    network: str = None,
) -> Confirm:
    text = Text(desc)
    if network is not None:
        text.normal("%s network" % network)
    text.mono(*_split_address(address))

    return Confirm(text, confirm="CONTINUE", cancel="QR CODE")


def _show_xpub(xpub: str, desc: str, cancel: str) -> Confirm:
    return Confirm(Text("NOT IMPLEMENTED"), cancel=cancel.upper())


async def show_xpub(
    ctx: wire.GenericContext, xpub: str, desc: str, cancel: str
) -> None:
    await raise_if_cancelled(
        interact(
            ctx,
            _show_xpub(xpub, desc, cancel),
            "show_xpub",
            ButtonRequestType.PublicKey,
        )
    )


async def show_address(
    ctx: wire.GenericContext,
    address: str,
    address_qr: str | None = None,
    desc: str = "Confirm address",
    network: str | None = None,
    multisig_index: int | None = None,
    xpubs: Sequence[str] = [],
) -> None:
    is_multisig = len(xpubs) > 0
    while True:
        if is_confirmed(
            await interact(
                ctx,
                _show_address(address, desc, network),
                "show_address",
                ButtonRequestType.Address,
            )
        ):
            break
        if is_confirmed(
            await interact(
                ctx,
                _show_qr(
                    address if address_qr is None else address_qr,
                ),
                "show_qr",
                ButtonRequestType.Address,
            )
        ):
            break

        if is_multisig:
            for i, xpub in enumerate(xpubs):
                cancel = "NEXT" if i < len(xpubs) - 1 else "ADDRESS"
                desc_xpub = "XPUB #%d" % (i + 1)
                desc_xpub += " (yours)" if i == multisig_index else " (cosigner)"
                if is_confirmed(
                    await interact(
                        ctx,
                        _show_xpub(xpub, desc=desc_xpub, cancel=cancel),
                        "show_xpub",
                        ButtonRequestType.PublicKey,
                    )
                ):
                    return


async def _show_modal(
    ctx: wire.GenericContext,
    br_type: str,
    br_code: ButtonRequestType,
    header: str | None,
    subheader: str | None,
    content: str,
    button_confirm: str | None,
    button_cancel: str | None,
    exc: ExceptionType = wire.ActionCancelled,
) -> None:
    text = Text(header.upper(), icon, icon_color, new_lines=False)
    if subheader:
        text.bold(subheader)
        text.br()
        text.br_half()
    text.normal(content)
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text, confirm=button_confirm, cancel=button_cancel),
            br_type,
            br_code,
        ),
        exc,
    )


async def show_error_and_raise(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "FAIL!",
    subheader: str | None = None,
    button: str = "CLOSE",
    red: bool = False,
    exc: ExceptionType = wire.ActionCancelled,
) -> NoReturn:
    await _show_modal(
        ctx,
        br_type=br_type,
        br_code=ButtonRequestType.Other,
        header=header,
        subheader=subheader,
        content=content,
        button_confirm=None,
        button_cancel=button,
        exc=exc,
    )
    raise exc


def show_warning(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "WARNING!",
    subheader: str | None = None,
    button: str = "TRY AGAIN",
    br_code: ButtonRequestType = ButtonRequestType.Warning,
) -> Awaitable[None]:
    return _show_modal(
        ctx,
        br_type=br_type,
        br_code=br_code,
        header=header,
        subheader=subheader,
        content=content,
        button_confirm=button,
        button_cancel=None,
    )


def show_success(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    subheader: str | None = None,
    button: str = "CLOSE",
) -> Awaitable[None]:
    return _show_modal(
        ctx,
        br_type=br_type,
        br_code=ButtonRequestType.Success,
        header="SUCCESS!",
        subheader=subheader,
        content=content,
        button_confirm=button,
        button_cancel=None,
    )


async def confirm_output(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
) -> None:
    text = Text("TRANSACTION")
    text.normal("Send " + amount + " to")
    text.mono(*_split_address(address))
    await raise_if_cancelled(
        interact(ctx, Confirm(text), "confirm_output", ButtonRequestType.ConfirmOutput)
    )


async def confirm_hex(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    data: str,
    description: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str = ui.ICON_SEND,  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
    width: int = MONO_HEX_PER_LINE,
    truncate_middle: bool = False,
) -> None:
    text = Text(title, new_lines=False)
    description_lines = 0
    if description is not None:
        description_lines = Span(description, 0, ui.NORMAL).count_lines()
        text.normal(description)
        text.br()
    text.mono(
        *_truncate_hex(
            data,
            lines=TEXT_MAX_LINES - description_lines,
            width=width,
            middle=truncate_middle,
        )
    )
    content: ui.Layout = Confirm(text)
    await raise_if_cancelled(interact(ctx, content, br_type, br_code))


async def confirm_total(
    ctx: wire.GenericContext, total_amount: str, fee_amount: str
) -> None:
    text = Text("TRANSACTION")
    text.bold("Total amount:")
    text.mono(total_amount)
    text.bold("Fee included:")
    text.mono(fee_amount)
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text, confirm="HOLD TO CONFIRM", cancel="X"),
            "confirm_total",
            ButtonRequestType.SignTx,
        )
    )


async def confirm_joint_total(
    ctx: wire.GenericContext, spending_amount: str, total_amount: str
) -> None:
    text = Text("JOINT TRANSACTION")
    text.bold("You are contributing:")
    text.mono(spending_amount)
    text.bold("to the total amount:")
    text.mono(total_amount)
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text, confirm="HOLD TO CONFIRM", cancel="X"),
            "confirm_joint_total",
            ButtonRequestType.SignTx,
        )
    )


async def confirm_metadata(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    content: str,
    param: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.SignTx,
) -> None:
    text = Text(title.upper(), new_lines=False)
    text.format_parametrized(content, param if param is not None else "")
    text.br()
    text.normal("Continue?")

    await raise_if_cancelled(interact(ctx, Confirm(text), br_type, br_code))


async def show_error_and_raise(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "Error",
    subheader: str | None = None,
    button: str = "Close",
    red: bool = False,
    exc: ExceptionType = wire.ActionCancelled,
) -> NoReturn:
    raise NotImplementedError
