class SearchManager:
    def __init__(self, search_engine):
        self.search_engine = search_engine

    def search(self, query):
        return self.search_engine.search(query)

    def get_search_results(self, query):
        results = self.search(query)
        return results if results else "No results found."
