#!/usr/bin/env python3

def test_function():
    """A simple test function."""
    return "Test successful"

def another_test():
    """Another test function."""
    return "Second test passed"

def third_test():
    """A third test function."""
    return "Third test completed successfully"

def fourth_test():
    """A fourth test function to test hooks."""
    return "Fourth test - hooks are working!"

if __name__ == "__main__":
    result = test_function()
    print(result)
    
    result2 = another_test()
    print(result2)
    
    result3 = third_test()
    print(result3)
    
    result4 = fourth_test()
    print(result4)