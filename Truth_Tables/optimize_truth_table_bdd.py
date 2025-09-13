#! /usr/bin/env python

import sys
import simplify_truth_table
from pyeda.inter import *
from collections import defaultdict
from sympy import symbols, Not

'''
For Part 2 of the assignment we had to find and return a better, non-trivial BDD variable order based on the resulting expression from part 1.

We found two heuristics which guided our approach, in order of priority:

"2. The input that affects the output functions the most should be ordered first (10]. However, there is no exact solution to measure which input affects the output most.
 3. Those inputs that are topologically near to one another in the circuit should be close in the order [10]. This rule is similar to the idea in [7)
    that the locations of the primary inputs in circuit diagrams imply a good ordering if the number of crosspoints is small." (Chung et. al, 1993)

To address the first point, we decided to:
- Start the ordering from the node that occurred the most in the expression given from part 1
- In case many nodes appeared the same amount of times, find a node with the variance (e.g. [a,b], [~a,b], a would be prioritized)

To address the second point, we decided to:
- Check which variable occurs more often in conjunction with the root
- This was implemented by means of an adjacency matrix ~ dictionary of dictionaries

    Example for [[~a, c], [~b, c], [~a, b], [a, ~b]]:

        adjacency_matrix {
            a: {a: 0, b: 2, c: 1}
            b: {a: 2, b: 0, c: 1},
            c: {a: 1, b: 1, c: 0}
        }

- The adjacency matrix is a dictionary of dictionaries
    - General dictionary has keys containing variables and values containing dictionaries
    - Smaller dictionaries have keys containing adjacent variables and values containing the number of conjunctions
- After having the root node, we could just look at the dictionary of that variable and find the variable with the highest value and then go to that dictionary to find the highest value
- This recursive function, stores the already visited variables to not repeat them until all variables have been used

In accordance with the research mentioned above, we followed the following steps:
1. normlize_literal(): if given a negative literal (e.g. ~a), it returns the normalized literal (a) and simply returns the original literal otherwise
2. count_literals(): counts the occurrences of each of the normalized variables (only a,b,c and not ~a,~b,~c)
3. find_most_frequent_literal(): finds the root node by comparing the frequencies and returning the most influential node (appears the most in the expression)
    and if there is a draw (e.g. same amount of a and b), then the first variable with variance would be returned
4. create_adjacency_matrix(): creates the dictionary of dictionaries to store variable relationships
5. rest_order(): goes through the adjacency matrix and creates the order

References:
Bryant, R. E. (1986). Graph-Based Algorithms for Boolean Function Manipulation.
Kulhari, S., & Khatri, S. P. (2006). Static Heuristics for Constructing Efficient Binary Decision Diagrams.
Chung, M. J., & Somenzi, F. (1993). A New Algorithm for the Construction of Reduced Ordered Binary Decision Diagrams
'''

def normalize_literal(literal):
    """
    Normalizes a literal to its base variable.
    If the literal has a negative symbol, namely "~", then return True and its base expression (literal without "~")
    If the literal does not have a negative symbol, then just return False and the literal itself
    """
    # Converts the expression to a string to determine whether "~" is at position 0
    if str(literal)[0] == '~':
        str_literal = str(literal)[1] 
        return True, exprvar(str_literal)
    return False, literal 

def count_literals(literal_lists, variables):
    """
    Count the occurrences of each normalized variable and store this in a dictionary containing its negative and positive counts
    An example pos_neg_count dictionary is {a: [2, 1], b: [0, 1], c: [2, 0]}
    """
    # Initating a dictionary to keep track of variables with negations
    pos_neg_count = {var: [0, 0] for var in variables}

    # Iterate through the list of literals to count the amount of negative and positive ones and add them to the pos_neg_count list
    for literal_pair in literal_lists:
        for literal in literal_pair:
            is_not, normalized_literal = normalize_literal(literal)

            if is_not:
                pos_neg_count[normalized_literal][0] += 1  # Adding to the negated count
            else:
                pos_neg_count[normalized_literal][1] += 1  # Adding to the positive count

    return pos_neg_count

def find_most_frequent_literal(pos_neg_count, literal_lists):
    """
    Find the most frequent literal by looking at which variable appears in the expression more often - this will be the root of the BDD.

    If all variables appear one time, then return the first variable.

    If there are more than one variables that have the same count >1 return the variable with most variance (e.g. a and ~a)

    """
    max_count = float('-inf');

    # Iterate through the list and find the literal that has the highest combined positive and negative counts
    for variable, values in pos_neg_count.items():
        current_count = values[0] + values[1]
        if current_count > max_count:
            max_count = current_count

    candidates = []

    # Iterate through the list and add all the literals with the max count to the candidates list
    for variable, values in pos_neg_count.items():
        count = values[0] + values[1]
        if count == max_count:
            candidates.append(variable)
    
    # If there's only one candidate (maximum value) or there are no varying literals, the return the first candidate
    if len(candidates) == 1 or all(value for value in pos_neg_count.values() if value[0] == 0 or value[1] == 0):
        return candidates[0]
    
    else:
        for i in range(len(candidates)):
            literal = candidates[i] 
            # Checking whether the variable has both a negated and non-negated instance
            if pos_neg_count[literal][0] != 0 and pos_neg_count[literal][1] != 0:
                # Returning the literal that had the most variance 
                return literal

def create_adjacency_matrix(literal_lists, variables):
    """
    Creates the adjacency matrix treating positive and negative variables (a and ~a) as the same.

    The matrix is a dictionary which contains smaller dictionaries of the form variable: {adj_var1: count1, adj_var2: count2 ...}
    """
    base_vars = {normalize_literal(var)[1] for var in variables}
    matrix = {var: {other: 0 for other in base_vars} for var in base_vars}

    # Iterate through the literals list and normalize each one
    for literals in literal_lists:
        normalized_literals = [normalize_literal(lit)[1] for lit in literals]

        # Iterate through each individual literal in the literal pairs
        for i in range(len(normalized_literals)):
            for j in range(i + 1, len(normalized_literals)):
                var1, var2 = normalized_literals[i], normalized_literals[j]

                # If both variables exist in the matrix update its count value in both directions since positive and negative values are represented the same
                if var1 in matrix and var2 in matrix[var1]:
                    matrix[var1][var2] += 1
                    matrix[var2][var1] += 1

    return matrix

def rest_order(root, adj_matrix, order):
    """
    Determines the most frequent occurring literal.

    First it stores the root node in the order list which will be returned at the end

    Goes through the dictionary to find the root node.

    Goes through the smaller dictionary of the root node to find the adjacent variable with the highest conjunction count and store it in max_literal_adj.

    Recursively call the function but with the root node now being the max_literal_adj.
    """
    # Check if the root is None or not a valid key
    if root is None:
        print("Error: The root is None.")
        return

    if root not in adj_matrix:
        print(f"Error: {root} is not found in the adjacency matrix.")
        return
    
    if root in order:
        print(order)
        return

    # Append the root node to the list and set it as the current
    order.append(root)
    current_node = root

    # Initialize the max adjacency value and the literal that will correspond to this value
    max_value = 0
    max_literal_adj = None

    # Iterate through the matrix looking for the mostly adjacent literal to root and set it to the max
    for literal_adj, value in adj_matrix[current_node].items():
        if value > max_value and literal_adj not in order:
            max_value = value
            max_literal_adj = literal_adj

    # Recursively call the function with the new maximum
    if max_literal_adj:
        rest_order(max_literal_adj, adj_matrix, order)
        
    return order

            
def main():
    table = sys.stdin.read()
    print(table)
    
    n_vars, outs = simplify_truth_table.parse(table)
    indexes = [index for index, value in enumerate(outs) if value == 0]
    groups = simplify_truth_table.get_groups(indexes, n_vars)
    literal_lists, letters = simplify_truth_table.pyeda_expressions(groups, True, n_vars, True)

    pos_neg_count = count_literals(literal_lists, letters)
    most_frequent = find_most_frequent_literal(pos_neg_count, literal_lists)

    adj_matrix = create_adjacency_matrix(literal_lists, letters)
    order = rest_order(most_frequent, adj_matrix, order = [])
    print(order)
    

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Exit if the pipe is broken
        sys.stderr.close()  # Closing stderr to avoid further errors
        sys.exit(0)
    

