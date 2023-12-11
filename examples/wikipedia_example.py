from social_signals.wikipedia.source import WikipediaSource

# Create an instance of the WikipediaSource class
source = WikipediaSource()

# Specify the search term
search_term = "hamas-israel war"

# Get Wikipedia page names based on the search term, limiting to 10 pages
search_results = source.search(search_term, n_pages=10)
print("Search results:")
print(search_results)

# Get data from a single Wikipedia page ("2023 Israel-Hamas war")
source.get_wikipedia_page_data("2023 Israel-Hamas war")
print("Data fetched from a single Wikipedia page:")
print(source.data)

# Get data from multiple related Wikipedia pages based on the search term, limiting to 10 pages
source.get_related_wikipedia_pages_data(search_term, n_pages=10)
print("Fetched data from related pages:")
print(source.data)