// rustimport:pyo3

//:
//: [dependencies]
//: rust-fuzzy-search = "0.1.1"

use pyo3::prelude::*;

#[pyfunction]
fn square(n: i32) -> i32 {
    n * n
}
