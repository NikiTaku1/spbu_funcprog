from data_loader import load_books
from preferences import process_preferences

def calculate_score(book, preferences):
    score = 0
    if preferences["genres"]: # Only check if genres are specified
        if any(genre in book["genre"] for genre in preferences["genres"]):
            score += 1
    if preferences["authors"]: #Only check if authors are specified
        if any(author in book["author"] for author in preferences["authors"]):
            score += 1
    if preferences["keywords"]: #Only check if keywords are specified
        if any(keyword in book["description"].lower() for keyword in preferences["keywords"]):
            score += 1
    return score

def get_recommendations(preferences, year_filter=None, sort_by="Rating"):
    books = load_books()
    scored_books = []

    for book in books:
        if year_filter is None or book['first_publish_year'] >= year_filter:
            score = calculate_score(book, preferences)
            if score > 0:
                scored_books.append((book, score))

    if not scored_books:
        return []

    if sort_by == "Rating":
        scored_books.sort(key=lambda item: item[1], reverse=True)
    elif sort_by == "Year":
        scored_books.sort(key=lambda item: (-item[1], item[0]['first_publish_year']))
    elif sort_by == "Name":
        scored_books.sort(key=lambda item: (-item[1], item[0]['title']))

    return scored_books