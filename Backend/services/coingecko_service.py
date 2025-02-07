import requests

class CoinGeckoService:
    @staticmethod
    def get_price(asset):
        """
        Fetch the price of an asset from CoinGecko.

        Parameters:
        - asset: The asset symbol (e.g., BTC, ETH).

        Returns:
        - The price as a float, or None if not found.
        """
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={asset.lower()}&vs_currencies=usd'
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            if asset.lower() in data:
                return float(data[asset.lower()]['usd'])

            print(f"Warning: {asset} is not available on CoinGecko.")
            return None  # If not found, return None

        except Exception as e:
            print(f"Error fetching price for {asset} from CoinGecko: {e}")
            return None  # No price found
