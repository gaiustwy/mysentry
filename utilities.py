from collections import Counter

def format_object_detected(labels):
    """
    Takes a list of labels and returns a formatted string that counts the occurrence
    of each unique label. The output is a comma-separated string that lists each 
    object and its count.
    
    Example:
    - Input: ['person', 'person', 'toilet', 'vase']
    - Output: "2 persons, 1 toilet, 1 vase"
    
    If the list is empty, it returns "Unidentifiable object".
    
    Args:
    labels (list of str): A list of labels representing detected objects.
    
    Returns:
    str: A formatted string with counts and object names.
    """
    # Handle the case where no labels are provided
    if len(labels) == 0:
        return "Unidentifiable object"
    
    # Count the occurrences of each label using Counter
    object_counter = Counter(labels)

    # Format the count and label into a string for each unique label
    objects_detected = ", ".join([f"{count} {label}" for label, count in object_counter.items()])
    return objects_detected
