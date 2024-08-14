PATTERNS = {
    "tags": r"(-)?\[(.*?)]",
    "strict": r"(title|body)?:?\"(.*?)\"",
    "score": r"score:"
             r"(?P<min_score>-?\d+)?"
             r"(?P<operator>-|\.\.)?"
             r"(?P<max_score>-?\d+)?",
    "user": r"user:(\d+)",
    "dates": r"(?P<field>created|lastactive):"
             r"(?P<start_date>\d{4}(?:-\d{2}(?:-\d{2})?)?)"
             r"(?P<operator>\.\.)?"
             r"(?P<end_date>\d{4}(?:-\d{2}(?:-\d{2})?)?)?",
    'booleans': r"(hasaccepted|isanswered):(true|false|yes|no|1|0)"
}
