# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: spy
#     language: python
#     name: python3
# ---

# # Example notebook
#
# This notebook demonstrates how to import and use the `spyglass_workshop` package.
# After forking and renaming the template, replace `spyglass_workshop` with your
# own package name.
#
# The `fibonacci` module provides two functions:
#
# - `f(n)` — returns the nth Fibonacci number
# - `f_list(n)` — returns a list of the first n Fibonacci numbers

# +
from spyglass_workshop.examples.fibonacci import f, f_list

print(f"f(10) = {f(10)}")
print(f"f_list(10) = {f_list(10)}")
