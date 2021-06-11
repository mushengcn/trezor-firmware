use core::convert::TryInto;

use crate::{
    micropython::obj::Obj,
    ui::{
        component::{ButtonContent, Component, Confirm, ConfirmMsg, Never, Text},
        display, theme,
    },
};

use super::layout::LayoutObj;

impl<T> Into<Obj> for ConfirmMsg<T>
where
    T: Component,
    T::Msg: Into<Obj>,
{
    fn into(self) -> Obj {
        match self {
            ConfirmMsg::Content(c) => c.into(),
            ConfirmMsg::LeftClicked => 1.try_into().unwrap(),
            ConfirmMsg::RightClicked => 2.try_into().unwrap(),
        }
    }
}

impl From<Never> for Obj {
    fn from(_: Never) -> Self {
        unreachable!()
    }
}

#[no_mangle]
extern "C" fn ui_layout_new_example() -> Obj {
    LayoutObj::new(Confirm::new(
        display::screen(),
        |area| {
            Text::new(area)
                .format("Testing text layout, with some text, and some more text. And {param}")
                .with(b"param", b"parameters!")
        },
        Some(ButtonContent::Text(b"Left")),
        theme::button_default(),
        Some(ButtonContent::Text(b"Right")),
        theme::button_default(),
    ))
    .into()
}
