class ArithmeticLatexGenerator:
    """
    A utility class to generate formatted LaTeX arrays for vertical 
    arithmetic operations (addition, subtraction, multiplication, and division).
    """

    def generate_column_addition_latex(self, numbers):
        """
        Takes a list of integers and returns a formatted LaTeX array 
        for vertical addition with carries and unbolded totals, robustly 
        handling multi-digit carries and exact column alignment.
        """
        if not numbers:
            return ""

        # Convert numbers to strings and find max length
        num_strs = [str(n) for n in numbers]
        max_len = max(len(s) for s in num_strs)

        # Pad all numbers with leading spaces to match the maximum width
        padded = [s.rjust(max_len) for s in num_strs]

        carries = {} # maps column index to carry string/digits
        result_digits = []
        carry = 0

        # Right-to-left addition loop
        for col in range(max_len - 1, -1, -1):
            col_sum = carry + sum(
                int(padded[row][col]) if padded[row][col] != ' ' else 0 
                for row in range(len(padded))
            )
            digit = col_sum % 10
            carry = col_sum // 10
            
            result_digits.insert(0, str(digit))
            
            if carry > 0:
                target_col = col - 1
                # Handle multi-digit carries or direct left-column placement
                carries[target_col] = str(carry)

        # Handle final carry overflow if sum exceeds max width digits
        while carry > 0:
            result_digits.insert(0, str(carry % 10))
            carry = carry // 10
            max_len += 1
            padded = [s.rjust(max_len) for s in num_strs]
            # Shift all existing carry keys to the right to accommodate new column
            carries = {k + 1: v for k, v in carries.items()}
            if carry > 0:
                carries[0] = str(carry)

        # Build the carry row ensuring exact column mapping
        carry_row_cells = []
        for c in range(max_len):
            if c in carries:
                carry_row_cells.append(r"\scriptstyle{" + carries[c] + "}")
            else:
                carry_row_cells.append("")
        carry_row_str = " & ".join(carry_row_cells)

        # Build the addend rows
        addend_rows = []
        for i, p_str in enumerate(padded):
            row_chars = list(p_str)
            if i == len(padded) - 1:
                # Place '+' sign cleanly before the first non-space character
                first_idx = next((idx for idx, char in enumerate(row_chars) if char != ' '), 0)
                if first_idx > 0:
                    row_chars[first_idx - 1] = "+"
                else:
                    row_chars[0] = "+"
            addend_rows.append(" & ".join(row_chars))

        # Build the result row (unbolded)
        result_row_str = " & ".join(result_digits)

        # Assemble the LaTeX array structure
        col_spec = r"r@{\hspace{2pt}}" * (max_len - 1) + "r"
        
        latex_code = [
            r"\begin{center}",
            r"{\large",
            r"$\begin{array}{" + col_spec + "}"
        ]
        
        if carries:
            latex_code.append(carry_row_str + r" \\")
        
        for row in addend_rows:
            latex_code.append(row + r" \\")
            
        latex_code.append(r"\hline")
        latex_code.append(result_row_str)
        latex_code.append(r"\end{array}$")
        latex_code.append(r"}")
        latex_code.append(r"\end{center}")

        return "\n".join(latex_code)

    def generate_column_subtraction_latex(self, a, b):
        """
        Takes two positive integers (minuend a, subtrahend b, with a >= b) 
        and returns a formatted LaTeX array for vertical subtraction using 
        the column method, mirroring the robust architecture of the addition generator.
        """
        str_a = str(a)
        str_b = str(b)
        max_len = max(len(str_a), len(str_b))
        
        padded_a = str_a.rjust(max_len)
        padded_b = str_b.rjust(max_len)
        
        # Check if we need an extra column on the left for the minus sign
        first_sub_idx = next((idx for idx, char in enumerate(padded_b) if char != ' '), 0)
        if first_sub_idx == 0:
            max_len += 1
            padded_a = str_a.rjust(max_len)
            padded_b = str_b.rjust(max_len)
            first_sub_idx = next((idx for idx, char in enumerate(padded_b) if char != ' '), 0)

        # Convert to working list of integer digits
        digits = [int(ch) if ch != ' ' else 0 for ch in padded_a]
        sub_digits = [int(ch) if ch != ' ' else 0 for ch in padded_b]
        
        cancellations = {} # maps col -> (old_val, new_val)
        borrows = {}       # maps col -> borrowed value (e.g., 10 or 13)
        
        # Right-to-left subtraction with borrowing simulation
        for col in range(max_len - 1, -1, -1):
            if digits[col] < sub_digits[col]:
                # Find nearest non-zero column to borrow from
                b_col = col - 1
                while b_col >= 0 and digits[b_col] == 0:
                    b_col -= 1
                
                # Perform borrow cascade
                orig_b = digits[b_col]
                digits[b_col] -= 1
                cancellations[b_col] = (orig_b, digits[b_col])
                
                # Intermediate zeros become 9
                for z_col in range(b_col + 1, col):
                    orig_z = digits[z_col]
                    digits[z_col] = 9
                    cancellations[z_col] = (orig_z, 9)
                    borrows[z_col] = 9
                    
                digits[col] += 10
                borrows[col] = digits[col]

        # Build top row cells with cancellations and superscripts
        top_row_cells = []
        for c in range(max_len):
            orig_char = padded_a[c]
            if orig_char == ' ':
                top_row_cells.append("")
                continue
                
            base_val = int(orig_char)
            if c in cancellations:
                old_v, new_v = cancellations[c]
                cell_str = rf"\cancel{{{old_v}}}^{{{new_v}}}"
            elif c in borrows:
                val = borrows[c]
                tens_str = rf"^{{{val // 10}}}" if val >= 10 else ""
                units_str = str(val % 10)
                cell_str = f"{tens_str}{units_str}"
            else:
                cell_str = str(base_val)
            top_row_cells.append(cell_str)

        # Build subtrahend row placing '-' cleanly before the first non-space character
        sub_chars = list(padded_b)
        if first_sub_idx > 0:
            sub_chars[first_sub_idx - 1] = "-"
        else:
            sub_chars[0] = "-"
        sub_row_str = " & ".join(sub_chars)

        # Compute actual result digits (unbolded)
        result_val = a - b
        result_str = str(result_val).rjust(max_len, ' ')
        result_row_str = " & ".join([d if d != ' ' else ' ' for d in result_str])

        # Assemble the LaTeX array structure mirroring addition layout
        col_spec = r"r@{\hspace{2pt}}" * (max_len - 1) + "r"
        
        latex_code = [
            r"\begin{center}",
            r"{\large",
            r"$\begin{array}{" + col_spec + "}",
            " & ".join(top_row_cells) + r" \\",
            sub_row_str + r" \\",
            r"\hline",
            result_row_str,
            r"\end{array}$",
            r"}",
            r"\end{center}"
        ]
        
        return "\n".join(latex_code)

    def generate_column_multiplication_latex(self, a, b):
        """
        Takes two positive integers (multiplicand a, multiplier b) 
        and returns a formatted LaTeX array for vertical multiplication 
        using the standard column method with partial products, 
        multiplication carries, and addition carries with custom spacing.
        """
        str_a = str(a)
        str_b = str(b)
        
        final_result = a * b
        max_len = len(str(final_result))
        
        padded_a = str_a.rjust(max_len)
        
        # 1. Calculate multiplication carries using the units digit of the multiplier
        units_digit = int(str_b[-1])
        mult_carries = {}
        carry = 0
        digits_a = [int(c) if c != ' ' else 0 for c in padded_a]
        
        for col in range(max_len - 1, -1, -1):
            d = digits_a[col]
            prod = d * units_digit + carry
            carry = prod // 10
            if carry > 0 and col - 1 >= 0:
                mult_carries[col - 1] = str(carry)
                
        # Build multiplication carry row cells
        mult_carry_cells = []
        for c in range(max_len):
            if c in mult_carries:
                mult_carry_cells.append(r"\scriptstyle{" + mult_carries[c] + "}")
            else:
                mult_carry_cells.append("")
        carry_row_str = " & ".join(mult_carry_cells)
        
        # 2. Build multiplicand and multiplier rows
        top_row_chars = list(padded_a)
        top_row_str = " & ".join(top_row_chars)
        
        mult_str = str_b.rjust(max_len)
        mult_chars = list(mult_str)
        first_idx = next((idx for idx, char in enumerate(mult_chars) if char != ' '), 0)
        if first_idx > 0:
            mult_chars[first_idx - 1] = r"\times"
        else:
            mult_chars[0] = r"\times " + mult_chars[0]
        mult_row_str = " & ".join(mult_chars)
        
        # 3. Compute partial products
        multiplier_digits = [int(ch) for ch in str_b]
        rev_digits = list(reversed(multiplier_digits))
        
        partial_products = []
        for i, d in enumerate(rev_digits):
            pp = a * d * (10 ** i)
            partial_products.append(pp)
            
        pp_rows = []
        for pp in partial_products:
            pp_padded = str(pp).rjust(max_len)
            pp_chars = [ch if ch != ' ' else ' ' for ch in pp_padded]
            pp_rows.append(" & ".join(pp_chars))
            
        # 4. Calculate addition carries if there are multiple partial products
        addition_carries = {}
        if len(partial_products) > 1:
            padded_pps = [str(pp).rjust(max_len) for pp in partial_products]
            add_carry = 0
            for col in range(max_len - 1, -1, -1):
                col_sum = sum(int(pp[col]) if pp[col] != ' ' else 0 for pp in padded_pps) + add_carry
                add_carry = col_sum // 10
                if add_carry > 0 and col - 1 >= 0:
                    addition_carries[col - 1] = str(add_carry)
                    
            add_carry_cells = []
            for c in range(max_len):
                if c in addition_carries:
                    add_carry_cells.append(r"\scriptstyle{" + addition_carries[c] + "}")
                else:
                    add_carry_cells.append("")
            add_carry_row_str = " & ".join(add_carry_cells)

        # Build final result row (unbolded)
        result_str = str(final_result).rjust(max_len)
        result_chars = [ch if ch != ' ' else ' ' for ch in result_str]
        result_row_str = " & ".join(result_chars)
        
        # 5. Assemble LaTeX array structure
        col_spec = r"r@{\hspace{2pt}}" * (max_len - 1) + "r"
        
        latex_code = [
            r"\begin{center}",
            r"{\large",
            r"$\begin{array}{" + col_spec + "}"
        ]
        
        if mult_carries:
            latex_code.append(carry_row_str + r" \\")
            
        latex_code.append(top_row_str + r" \\")
        latex_code.append(mult_row_str + r" \\")
        latex_code.append(r"\hline")
        
        # Add partial product rows with custom spacing on the last one if addition carries exist
        for idx, row in enumerate(pp_rows):
            if len(partial_products) > 1 and idx == len(pp_rows) - 1:
                if addition_carries:
                    latex_code.append(row + r" \\[-0.6em]")
                    latex_code.append(add_carry_row_str + r" \\[-0.3em]")
                else:
                    latex_code.append(row + r" \\")
            else:
                latex_code.append(row + r" \\")
            
        if len(partial_products) > 1:
            latex_code.append(r"\hline")
            
        latex_code.append(result_row_str)
        latex_code.append(r"\end{array}$")
        latex_code.append(r"}")
        latex_code.append(r"\end{center}")
        
        return "\n".join(latex_code)

    def generate_column_division_latex(self, dividend, divisor):
        """
        Takes a dividend and divisor and returns a formatted LaTeX array 
        for short division (bus stop method) with correct carry superscripts, 
        proper bus stop bracket, unbolded quotient, and vertical spacing.
        """
        clean_str = str(dividend).replace(",", "")
        digits = [int(c) for c in clean_str]
        
        quotient = dividend // divisor
        quotient_str = str(quotient)
        
        parts = []
        current = 0
        buffer_str = ""
        
        for i, d in enumerate(digits):
            current = current * 10 + d
            buffer_str += str(d)
            
            # If current is less than the divisor, keep accumulating digits
            if current < divisor and i < len(digits) - 1:
                continue
                
            q = current // divisor
            rem = current % divisor
            
            parts.append(buffer_str)
            if rem > 0 and i < len(digits) - 1:
                parts.append(f"^{{\\scriptscriptstyle{{{rem}}}}}")
                
            current = rem
            buffer_str = ""
            
        parts.append(buffer_str)
        result_str = "".join(parts)
        
        # Assemble LaTeX array structure with the division bracket ')' included
        latex_code = [
            r"\begin{center}",
            r"{\large",
            r"$\begin{array}{r}",
            f"    {quotient_str} \\\\",
            f"    {divisor} \\overline{{\\smash{{)}}\\strut {result_str}}}",
            r"\end{array}$",
            r"}",
            r"\end{center}"
        ]
        
        return "\n".join(latex_code)