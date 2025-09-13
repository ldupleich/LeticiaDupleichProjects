#! /usr/bin/env python

import sys
import math
from string import ascii_lowercase
from pyeda.inter import *

"""
For Part 1 of the assignment we were challenged to 1) parse a truth table, 2) produce a simplified boolen expression.

Our intial idea was: 
- parse the table for the number of variables and column of outputs
- decide whether to focus on the conditions that lead to True or False and return the negation 
- compare each pair of lines of interest looking for a single difference and ignore that bit
  e.g. (a, b, c), (a, b, ~c) --> (a, b)
- construct the boolean expression with OR, AND

Problems with this approach:
- We were not further trying to simplify the simplified expressions.... WE NEED SOME TYPE OF WHILE SOMETHING_MERGED loop
- It made it impossible to simplify groups that have only one difference amongst each other... LOOK FOR
  SIMPLIFICATION GROUPS INSTEAD OF PAIRS

In accordance with the established Quine-McCluskey method, we followed the following steps:
- parse() - to get number of variables and output column
- get_condition(): Identify which rows of the truth table (minterms) are relevant
  (either the rows of true or false output, depending on which is less frequent).
- patterns() - Compute a pattern string for a group, with 0 or 1 if all the numbers in that group share that bit,
  otherwise '-' indicating don't care.
- get_groups(): Each group is represented as a set of indices. This function uses get_pattern() to compute a pattern
  for each group and merges any two groups whose patterns differ by exactly one bit.
- pyeda_expression(): Convert each merged group into a Boolean term, and combine these terms using OR
  to form the final simplified expression (using Pyeda library for basic boolean components).

References:
GeeksforGeeks. (2022, April 22). Quine-McCluskey method. https://www.geeksforgeeks.org/quine-mccluskey-method/
"""

def parse(table):
    table_rows = table.splitlines()
    # Get the integer that comes after the separator (" || "), for all lines but the header
    outs = [int(row.split(" || ")[1][0]) for row in table_rows[1:]]

    # The are as many elements in outs as rows, which are 2^n_vars, so we can reverse it to find n_vars
    n_vars = int(math.log2(len(outs)))
    return n_vars, outs


def get_condition(outs):
    """
    Checking whether there are more true or false outputs
    and return indexes of lines of interest
    """
    if outs.count(0) < outs.count(1):
        indexes = [index for index, value in enumerate(outs) if value == 0]
        condition = False
    else:
        indexes = [index for index, value in enumerate(outs) if value == 1]
        condition = True

    return indexes, condition


def get_pattern(group, n_vars):
    """
    Compute a pattern string for a group.
    Each position in the pattern is '0' or '1' if all numbers in the group share that bit,
    otherwise '-' indicating a don't-care.
    """

    # Save the binary version of the indexes in the group.
    bin_list = [format(num, f'0{n_vars}b') for num in group]
    pattern = ""

    # Iterate through each bit position from 0 to n_vars-1.
    for pos in range(n_vars):
	
	# Take the bit from the first binary string at position pos for comparison.
        bit = bin_list[0][pos]
        
        # Check if all binary strings have the same bit at position pos.
        # If so, add bit to pattern, otherwise add a don't-care.
        if all(b[pos] == bit for b in bin_list):
             pattern += bit
        else:
             pattern += "-"
	    
    return pattern


def get_groups(indexes, n_vars):
    """
    Merge groups of indices that differ by exactly one bit.
    
    Each group is represented as a set of indices. This function uses get_pattern() to compute a pattern
    for each group and merges any two groups whose patterns differ by exactly one bit.
    
    Parameters:
      groups (list): List of groups, each a set of indices.
      n_vars (int): Number of boolean variables.
    
    Returns:
      List of merged groups.
    """

    # Start with each index as its own group
    groups = [{i} for i in indexes]

    # Keep trying to merge groups further, until a complete pass does not merge anything.
    merged_something = True
    while merged_something:
        merged_something = False  # Assume no merges until we find one
        new_groups = []
        used = [False] * len(groups)

        # Attempt to merge each pair of groups.
        # STEP 1: Retrieve the pattern for both groups.
        for i in range(len(groups)):
            pat_i = get_pattern(groups[i], n_vars)
            # index j must be bigger than index i to not repeat comparisons
            for j in range(i + 1, len(groups)):
                pat_j = get_pattern(groups[j], n_vars)
                diff = 0

                # STEP 2: Compare the two patterns bit by bit, and count differences
                for a, b in zip(pat_i, pat_j):
                    if a != b:
                        # If either position is '-', skip merging in this pass
                        if a == '-' or b == '-':
                            diff = 2  # Force non-mergeable
                            break
                        else:
                            diff += 1

                # Merge if exactly one bit differs (excluding '-')
                if diff == 1:
                    new_group = groups[i] | groups[j]

                    # The same new group of minterms can be generated by merging different pairs of existing groups.
                    # Checking whether new_group is already in new_groups prevents inserting duplicates. 
                    if new_group not in new_groups:
                        new_groups.append(new_group)
                    used[i] = used[j] = True
                    merged_something = True

        # Add groups that were not merged
        for idx, group in enumerate(groups):
            if not used[idx] and group not in new_groups:
                new_groups.append(group)

        # Update groups for the next iteration
        groups = new_groups

    # Once a full pass completes with no merges, return the final groups
    return groups


def pyeda_expressions(groups, condition, n_vars, Part_2=False):
    """
    Generate a PyEDA expression based on groups of indexes.
    For each group, common literals are extracted for each bit position.
    If no common literal is found for the group, the function constructs
    an expression as the OR of the original minterms corresponding to each number in the group.
    """
    # Create expression variables (a, b, c, ...).
    letters = [exprvar(ch) for ch in ascii_lowercase[:n_vars]]
    final_expr = None
    terms_Part2 = []

    # Convert each group to a boolean expression.
    for group in groups:
        lits_Part2 = []
        bin_list = [format(num, f'0{n_vars}b') for num in group]
        term = None

        # Try to extract common literals for each bit position.
        for pos in range(n_vars):

            # If all numbers in this group have '1' at position pos,
            # then the corresponding variable is a common literal.
            if all(b[pos] == '1' for b in bin_list):
                lit = letters[pos]

	    # If all numbers in this group have '0' at position pos,
            # then the corresponding variable's negation is a common literal.
            elif all(b[pos] == '0' for b in bin_list):
                lit = ~letters[pos]
	
	    # Otherwise, there's no common literal for this bit position.
            else:
                lit = None

	    # If a literal was found for this bit position, append it to the term with AND.
            if lit is not None:
                lits_Part2.append(lit)
                term = lit if term is None else term & lit

        # If no common literal was found, build the term as OR of individual minterms.
        if term is None:
            for member in group:
                binary = format(member, f'0{n_vars}b')
                minterm = None

                # Iterate through the binary representation of each member of the group
                for pos, bit in enumerate(binary):
                    l = letters[pos] if bit == '1' else ~letters[pos]

                    # Build the minterms that fully describes this member.
                    minterm = l if minterm is None else minterm & l
                
                lits_Part2.append(minterm)
                term = minterm if term is None else Or(term, minterm)
        
        terms_Part2.append(lits_Part2)

        # Join terms by disjunction
        final_expr = term if final_expr is None else Or(final_expr, term)

    if Part_2:
        return terms_Part2, letters

    return final_expr if condition else Not(final_expr)


if __name__ == "__main__":
    table = sys.stdin.read()
    print(table)
    n_vars, outs = parse(table)
    indexes, condition = get_condition(outs)
    groups = get_groups(indexes, n_vars)
    simplified_expression = pyeda_expressions(groups, condition, n_vars)
    print(simplified_expression)

