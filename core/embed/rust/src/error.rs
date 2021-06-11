use core::convert::Infallible;
use core::fmt;

use cstr_core::CStr;

pub enum Error {
    Missing,
    OutOfRange,
    InvalidType,
    NotBuffer,
    NotInt,
    InvalidOperation,
}

impl Error {
    pub fn as_cstr(&self) -> &'static CStr {
        // SAFETY: Safe because we are passing in \0-terminated literals.
        unsafe {
            let cstr = |s: &'static [u8]| CStr::from_bytes_with_nul_unchecked(s);
            match self {
                Error::Missing => cstr(b"Missing\0"),
                Error::OutOfRange => cstr(b"OutOfRange\0"),
                Error::InvalidType => cstr(b"InvalidType\0"),
                Error::NotBuffer => cstr(b"NotBuffer\0"),
                Error::NotInt => cstr(b"NotInt\0"),
                Error::InvalidOperation => cstr(b"InvalidOperation\0"),
            }
        }
    }
}

impl From<Error> for &'static CStr {
    fn from(val: Error) -> Self {
        val.as_cstr()
    }
}

impl fmt::Debug for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.as_cstr().fmt(f)
    }
}

// Implements a conversion from `core::convert::Infallible` to `Error` to so
// that code generic over `TryFrom` can work with values covered by the blanket
// impl for `Into`: `https://doc.rust-lang.org/std/convert/enum.Infallible.html`
impl From<Infallible> for Error {
    fn from(_: Infallible) -> Self {
        unreachable!()
    }
}
