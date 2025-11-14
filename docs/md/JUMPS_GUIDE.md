# AIBasic Jump/Goto Instructions Guide

## Overview

AIBasic supports **jump** and **goto** instructions for control flow, allowing you to create loops, conditional branches, and implement complex program logic similar to classic BASIC programming.

## Syntax

### Unconditional Jumps

Jump to a specific line without any condition:

```aibasic
goto <line_number>
jump to <line_number>
jump to line <line_number>
```

**Examples:**
```aibasic
10 set x to 5
20 goto 40
30 print "This is skipped"
40 print "Execution continues here"
```

### Conditional Jumps

Jump to a line only if a condition is met:

```aibasic
if <condition> jump to <line_number>
if <condition> jump to line <line_number>
if <condition> goto <line_number>
```

**Examples:**
```aibasic
10 set age to 25
20 if age is greater than 18 jump to line 40
30 print "Minor"
40 print "Adult check complete"
```

### Error Handling (On Error Goto)

Set an error handler that catches exceptions and jumps to a specific line:

```aibasic
on error goto <line_number>
on error jump to <line_number>
```

**Key Features:**
- Catches all exceptions that occur after the directive
- Can be changed multiple times in the program
- Each `on error goto` updates the current error handler
- Error information stored in `_last_error` and `_last_error_line` variables

**Examples:**
```aibasic
10 set x to 10
20 set y to 0
30 on error goto 100
40 divide x by y and store in result
50 print "This won't execute"
60 goto 200

100 print "ERROR: Division by zero caught!"
110 print "Error occurred at line" and _last_error_line
120 print "Error message:" and _last_error
130 print "Continuing program..."

200 print "Program complete"
```

**Multiple Error Handlers:**
```aibasic
10 on error goto 100
20 # ... risky operation 1 ...
30 on error goto 200
40 # ... risky operation 2 ...
50 on error goto 300
60 # ... risky operation 3 ...
```

### Subroutines (CALL and RETURN)

Create reusable code blocks with CALL and RETURN statements:

```aibasic
call <line_number>
return
```

**Key Features:**
- Jump to a subroutine and automatically return to the next line
- Uses a call stack to track return addresses
- Supports nested subroutine calls
- Each RETURN pops the last return address from the stack

**Simple Example:**
```aibasic
10 print "Main program"
20 set x to 5
30 call 1000
40 print "Back in main, x =" and x
50 goto 999

1000 print "In subroutine"
1010 multiply x by 2
1020 return

999 print "Done"
```

**Nested Calls:**
```aibasic
10 call 100
20 print "Done"
30 goto 999

100 print "Subroutine A"
110 call 200
120 return

200 print "Subroutine B"
210 return

999 print "End"
```

## How It Works

When the compiler detects jump/goto instructions in your program:

1. **Detection**: The parser identifies jump instructions and their target line numbers
2. **Code Generation**: The compiler generates Python code with:
   - A dedicated function for each line of code (`_line_10()`, `_line_20()`, etc.)
   - A program counter (`_current_line`) tracking the current executing line
   - A next line pointer (`_next_line`) for jump targets
   - A dispatch table mapping line numbers to their functions
   - A main loop that calls the appropriate function for each line
3. **Jump Execution**: When a jump is triggered:
   - Unconditional: Sets `_next_line` to the target line number
   - Conditional: LLM evaluates the condition into `_aibasic_jump_condition`, then sets `_next_line` if true
   - After each line function executes, if no jump occurred, `_next_line` is set to the next sequential line
   - The main loop continues with `_current_line = _next_line` and calls the next function

**Example Generated Code Structure:**
```python
def _line_10():
    global _next_line, counter
    counter = 0
    if _next_line is None:
        _next_line = 20

def _line_20():
    global _next_line, counter
    print(counter)
    if _next_line is None:
        _next_line = 30

def main():
    global _next_line, counter
    _current_line = 10
    _next_line = None

    _line_functions = {
        10: _line_10,
        20: _line_20,
        # ...
    }

    while _current_line is not None:
        _next_line = None
        line_func = _line_functions.get(_current_line)
        if line_func:
            line_func()
        _current_line = _next_line
```

## Common Patterns

### 1. Simple Loop

Create a loop that repeats a fixed number of times:

```aibasic
10 set counter to 0
20 print "Iteration" and counter
30 increment counter by 1
40 if counter is less than 5 jump to line 20
50 print "Loop complete"
```

**Output:**
```
Iteration 0
Iteration 1
Iteration 2
Iteration 3
Iteration 4
Loop complete
```

### 2. While-Like Loop

Implement a while loop pattern:

```aibasic
10 set sum to 0
20 set i to 1
30 if i is greater than 10 jump to line 60
40 add i to sum
50 increment i by 1 and goto 30
60 print "Sum of 1 to 10 is" and sum
```

### 3. Conditional Branch

Branch to different code paths based on conditions:

```aibasic
10 set score to 85
20 if score is greater than or equal to 90 jump to line 50
30 if score is greater than or equal to 80 jump to line 60
40 goto 70
50 print "Grade A" and goto 80
60 print "Grade B" and goto 80
70 print "Grade C or below"
80 print "Grading complete"
```

### 4. Early Exit

Exit early from a section of code:

```aibasic
10 set data to empty list
20 if data is empty jump to line 50
30 print "Processing data..."
40 print "Data processed"
50 print "Done"
```

### 5. Skip Section

Skip a section of code unconditionally:

```aibasic
10 set debug_mode to false
20 if debug_mode jump to line 50
30 goto 60
40 rem This section is only for debugging
50 print "Debug information here"
60 print "Continue normal execution"
```

### 6. Nested Conditions

Implement nested if-else logic:

```aibasic
10 set a to 5
20 set b to 10
30 if a is less than 10 jump to line 50
40 print "a is large" and goto 80
50 if b is less than 10 jump to line 70
60 print "a is small, b is large" and goto 80
70 print "Both are small"
80 print "Done"
```

### 7. Search Loop

Find the first element matching a condition:

```aibasic
10 set numbers to list 5 12 8 15 3
20 set index to 0
30 if index equals length of numbers jump to line 70
40 get item at index from numbers as current
50 if current is greater than 10 jump to line 80
60 increment index and goto 30
70 print "Not found" and goto 90
80 print "Found" and current and "at index" and index
90 print "Search complete"
```

### 8. Multiple Exit Points

Use jumps to exit from different points:

```aibasic
10 set value to 0
20 if value is less than 0 jump to line 60
30 if value equals 0 jump to line 70
40 print "Positive value"
50 goto 80
60 print "Negative value" and goto 80
70 print "Zero value"
80 print "Validation complete"
```

## Best Practices

### ✅ DO:

1. **Use meaningful line numbers**: Space them (10, 20, 30...) for easier insertion
2. **Comment your jumps**: Explain why the jump happens
3. **Keep jump targets visible**: Don't jump too far away
4. **Use for control flow**: Loops, branches, early exits
5. **Test edge cases**: Ensure jumps work with empty data, boundaries

### ❌ DON'T:

1. **Create infinite loops accidentally**: Always have an exit condition
2. **Jump backwards without a counter**: This creates infinite loops
3. **Make spaghetti code**: Too many jumps make code hard to follow
4. **Jump into the middle of complex operations**: Jump to clean entry points
5. **Forget the exit condition**: Every loop needs a way to exit
6. **Ignore error handlers**: Always set error handlers for risky operations
7. **Create error handler loops**: Ensure error handlers don't cause new errors
8. **Forget to clear error info**: Reset error state after handling

### Error Handling Best Practices:

✅ **DO:**
1. Set error handlers before risky operations (file I/O, network, division, etc.)
2. Log error details using `_last_error` and `_last_error_line`
3. Update error handlers as needed throughout the program
4. Provide graceful degradation or recovery mechanisms
5. Always have a cleanup section after error handling

❌ **DON'T:**
1. Set error handlers inside loops without careful consideration
2. Jump to an error handler that might cause another error
3. Forget that error handlers are global and affect all subsequent code
4. Re-raise errors without handling them (defeats the purpose)

### Subroutine Best Practices:

✅ **DO:**
1. Use line numbers 1000+, 2000+, etc. for subroutines (keeps them organized)
2. Document each subroutine with comments explaining purpose and parameters
3. Use consistent naming patterns for subroutine variables (e.g., `gcd_result`, `sum_result`)
4. Always include a RETURN statement at the end of each subroutine
5. Test subroutines individually before integrating into main program
6. Keep subroutines focused on a single task (single responsibility principle)

❌ **DON'T:**
1. Forget the RETURN statement (program will continue into next code)
2. Mix main program logic with subroutine code without clear separation
3. Modify global variables without documenting side effects
4. Use GOTO within subroutines to jump outside the subroutine
5. Create deeply nested calls (>5 levels) as it becomes hard to debug
6. RETURN from the main program (only from subroutines)

## Common Pitfalls

### Infinite Loop

**Problem:**
```aibasic
10 print "Hello"
20 goto 10  # Infinite loop!
```

**Solution:** Add a counter or condition:
```aibasic
10 set count to 0
20 if count is greater than 5 jump to line 50
30 print "Hello"
40 increment count and goto 20
50 print "Done"
```

### Wrong Jump Target

**Problem:**
```aibasic
10 set x to 5
20 if x is greater than 0 jump to line 99  # Line 99 doesn't exist!
30 print "Continue"
```

**Solution:** Ensure target line exists:
```aibasic
10 set x to 5
20 if x is greater than 0 jump to line 40
30 print "x is not positive"
40 print "Continue"
```

### Jumping Over Variable Initialization

**Problem:**
```aibasic
10 goto 30
20 set total to 0  # Skipped!
30 add 5 to total  # Error: total not defined
```

**Solution:** Initialize before jumps:
```aibasic
10 set total to 0
20 goto 40
30 print "Skipped"
40 add 5 to total
```

## Advanced Examples

### Factorial Calculator

```aibasic
10 set n to 5
20 set factorial to 1
30 set i to 1
40 if i is greater than n jump to line 70
50 multiply factorial by i
60 increment i and goto 40
70 print "Factorial of" and n and "is" and factorial
```

### Error Handling with Recovery

```aibasic
10 print "File processing with error handling"
20 set attempts to 0
30 set max_attempts to 3
40 on error goto 100

50 increment attempts by 1
60 print "Attempt" and attempts
70 read file "data.txt" into data
80 print "File read successfully!"
90 goto 200

100 print "ERROR:" and _last_error
110 print "Occurred at line" and _last_error_line
120 if attempts is greater than or equal to max_attempts jump to line 150
130 print "Retrying..."
140 goto 50

150 print "Maximum attempts reached, giving up"
160 goto 200

200 print "Program complete"
```

### Nested Error Handlers

```aibasic
10 on error goto 100
20 print "Opening database connection..."
30 connect to database

40 on error goto 200
50 print "Executing query..."
60 execute query "SELECT * FROM users"

70 on error goto 300
80 print "Writing results to file..."
90 write results to file "output.txt"

95 print "All operations successful!"
96 goto 400

100 print "ERROR: Database connection failed"
110 print _last_error
120 goto 400

200 print "ERROR: Query execution failed"
210 print _last_error
220 print "Closing connection..."
230 goto 400

300 print "ERROR: File write failed"
310 print _last_error
320 print "Closing connection..."
330 goto 400

400 print "Cleanup complete"
```

### Subroutine Library Pattern

```aibasic
10 print "Math Operations Library Example"
20 set a to 12
30 set b to 8

40 print "GCD of" and a and "and" and b
50 call 1000
60 print "GCD result:" and gcd_result

70 print "LCM of" and a and "and" and b
80 call 2000
90 print "LCM result:" and lcm_result

100 goto 9999

# Subroutine: GCD (Greatest Common Divisor)
1000 set x to a
1010 set y to b
1020 if y equals 0 jump to line 1060
1030 set temp to x modulo y
1040 set x to y
1050 set y to temp and goto 1020
1060 set gcd_result to x
1070 return

# Subroutine: LCM (Least Common Multiple)
# Uses GCD subroutine
2000 call 1000
2010 multiply a by b and store in product
2020 divide product by gcd_result and store in lcm_result
2030 return

9999 print "Program complete"
```

### FizzBuzz

```aibasic
10 set i to 1
20 if i is greater than 20 jump to line 100
30 set output to empty string
40 if i modulo 3 equals 0 then add "Fizz" to output
50 if i modulo 5 equals 0 then add "Buzz" to output
60 if output is empty then set output to i
70 print output
80 increment i
90 goto 20
100 print "FizzBuzz complete"
```

### Binary Search (Simplified)

```aibasic
10 set list to sorted numbers 1 3 5 7 9 11 13
20 set target to 7
30 set low to 0
40 set high to length of list minus 1
50 if low is greater than high jump to line 120
60 set mid to low plus high divided by 2
70 get element at mid from list as value
80 if value equals target jump to line 110
90 if value is less than target then set low to mid plus 1
100 if value is greater than target then set high to mid minus 1
105 goto 50
110 print "Found" and target and "at index" and mid and goto 130
120 print "Not found"
130 print "Search complete"
```

## Comparison with Modern Constructs

| AIBasic Jump | Python Equivalent |
|--------------|-------------------|
| `goto 50` | Not directly available (AIBasic uses program counter) |
| `if x > 10 jump to 50` | `if x > 10: # execute line 50` |
| Loop with goto | `while condition:` or `for i in range():` |
| Early exit with goto | `break` or `return` |
| Skip section with goto | `continue` or conditional blocks |

## Performance Considerations

- **Jump detection**: The compiler automatically detects if jumps are used
- **No jumps**: Linear code generation (faster, direct execution)
- **With jumps**: Function-based dispatch with lookup table (efficient O(1) dispatch)
- **Optimization**: The compiler only generates jump infrastructure when needed
- **Implementation**: Uses pure Python without external goto libraries for maximum compatibility
- **Function benefits**:
  - Clean separation of code for each line
  - Easy to debug and trace execution
  - Better code organization and readability
  - Potential for future optimizations (caching, JIT compilation)
  - Each line is a separate scope with explicit global declarations

## Debugging Tips

1. **Print line numbers**: Add print statements with line numbers to track execution
2. **Use comments**: Annotate jump targets with `# Jump target for X`
3. **Trace execution**: Print variables before conditional jumps
4. **Check boundaries**: Verify loop counters and conditions
5. **Test incrementally**: Start with simple jumps, add complexity gradually

## See Also

- [examples/example_jumps.aib](examples/example_jumps.aib) - Complete examples
- [README.md](README.md) - General AIBasic documentation
- [TASK_TYPES.md](TASK_TYPES.md) - Available task types
