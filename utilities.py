from collections import Counter

def format_object_detected(labels):
	"""
	Counts the frequency of each label and formats it as a comma-separated string.
	Example: "2 persons, 1 toilet, 1 vase"
	"""
	if len(labels) == 0:
		return "Unidentifiable object"
	
	object_counter = Counter(labels)
	objects_detected = ", ".join([f"{count} {label}" for label, count in object_counter.items()])
	return objects_detected
