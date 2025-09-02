from name_parser import parse_names
from price_parser import parse_prices

def match_names_and_prices(name_str, price_str):
    names = parse_names(name_str)
    prices = parse_prices(price_str)

    results = []
    for i, price_data in enumerate(prices):
        name = names[i] if i < len(names) else names[0]
        results.append({
            "name": name,
            "price": price_data["price"],
            "brand": price_data["brand"]
        })
    return results
