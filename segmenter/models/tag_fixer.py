from typing import List


def get_error_importance(window, correct_tag):
    """
    Returns an error importance for window. 
    window is assumed to be an invalid BIOES combination.
    
    window: Window owith an error in the middle tag
    correct_tag: Correct tag
    """
    
    wrong_tag = window[1]
    assert wrong_tag != correct_tag
    
    # Only invalid combinations should go here
    # Greater importance implies that the error is more likely to be fixed
    error_importance = {
        # I is B error
        ("O", "I", "I"): 5,
        ("O", "I", "E"): 5,
        ("E", "I", "I"): 5,
        ("E", "I", "E"): 5,
        ("S", "I", "I"): 5,
        ("S", "I", "E"): 5,
        
        # I is E error
        ("I", "I", "O"): 5,
        ("I", "I", "B"): 5,
        ("I", "I", "S"): 5,
        ("B", "I", "O"): 5,
        ("B", "I", "B"): 5,
        ("B", "I", "S"): 5,
        
        # Single entity error
        ("O", "B", "O"): 5,
        ("O", "E", "O"): 5,
        ("O", "I", "O"): 5,
    }

    return error_importance.get(tuple(window), 1) # 1 is default

def fix_error(pos, window, c_tag, tags, fix, verbose=True):
    if verbose:
        print(f"Wrong tag {window[1]} at position {pos + 1} in window {window}{f' changed to {c_tag}' if fix else ''}")
    if fix:
        if c_tag == "O":
            # No metatags
            tags[pos+1] = c_tag
        else:
            # Updating with metatags
            tags[pos+1] = c_tag + tags[pos+1][1:]
    return get_error_importance(window, c_tag)

def fix_window(window, i, tags, fix=True, verbose=True):
    """
    Fix the tags if in window exist an error returning its relevance.
    """
    if window[0] in ["E", "S", "O"]:
        if window[2] in ["B", "O", "S"]:
            # [E, S, O] _ [B, O, S] => [E, S, O] [S,O] [B, O, S]
            if window[1] not in ["S", "O"]:
                # This is very unlikely in argumentation, so an O is the most likely option
                return fix_error(i, window, "O", tags, fix, verbose)
        elif window[2] in ["I", "E"]:
            # [E, S, O] _ [I, E] => [E, S, O] B [I, E]
            if window[1] not in ["B"]:
                return fix_error(i, window, "B", tags, fix, verbose)
    elif window[0] in ["B", "I"]:
        if window[2] in ["B", "O", "S"]:
            # [B, I] _ [B, O, S] => [B, I] E [B, O, S]
            if window[1] not in ["E"]:
                return fix_error(i, window, "E", tags, fix, verbose)
        elif window[2] in ["I", "E"]:
            # [B, I] _ [I, E] => [B, I] I [I, E]
            if window[1] not in ["I"]:
                return fix_error(i, window, "I", tags, fix, verbose)

    return 0 # Not an error

def fix_tags(tags: List[str], verbose=True) -> List[str]:
    """
    Transform a possible invalid BIOES tag sequence into a valid one
    
    tags: List of tags
    
    return: A list with a valid BIOES sequence
    """
    
    
    tags = ["O"] + tags + ["O"]
    range_errors = []
    for i in range(len(tags) - 2):
        window = [t[0] for t in tags[i:i+3]] # Removing metatags
        error_importance = fix_window(window, i, tags, fix=False, verbose=verbose)
        
        if error_importance > 0: # Window with error
            range_errors.append((error_importance, i, window))
        elif len(range_errors) == 1: # No window error and the previous had an error
            value, i, window = range_errors[0]
            fix_window(window, i, tags, verbose=verbose)
            range_errors.clear()
            
        if len(range_errors) == 2: # The previous and current windows have errors
            # If the first two errors in a list are next to each other
            # then the both errors can be fixed by fixing only one of them
            
            # If importance are equal the the right error will be fixed
            range_errors.sort(reverse=True)
            value, i, window = range_errors[0]
            fix_window(window, i, tags, verbose=verbose)
            range_errors.clear()
            
    if len(range_errors) == 1: # Can be 0 or 1
        value, i, window = range_errors[0]
        fix_window(window, i, tags, verbose=verbose)
        range_errors.clear()
    
    return tags[1:-1]
