# arithmetic-latex-generator

A Python library for rendering addition, subtraction, multiplication, and division of natural numbers in LaTeX.

## Project Structure

* **`latex_arithmetic.py`**: Contains the core Python functions.
* **`examples.ipynb`**: Contains Jupyter notebook examples demonstrating how to output the LaTeX.
* **`output.tex`**: Stores the generated code in a ready-to-compile LaTeX file. Note \usepackage{cancel} is required for the cancellation marks in subtraction.

## Usage

```python
import latex_arithmetic

# Instantiate the generator
generator = latex_arithmetic.ArithmeticLatexGenerator()

# 1. Addition Example
addition_latex = generator.generate_column_addition_latex([456, 789])

# 2. Subtraction Example
subtraction_latex = generator.generate_column_subtraction_latex(1000, 345)

# 3. Multiplication Example
multiplication_latex = generator.generate_column_multiplication_latex(45, 12)

# 4. Division Example
division_latex = generator.generate_column_division_latex(145, 4)
```
