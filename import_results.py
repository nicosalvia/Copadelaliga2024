import requests
import pandas as pd
import logging


# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers extracted from the browser's network request
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsib2F1dGgyX3hzY29yZXNfYXBwbGljYXRpb24iXSwidXNlcl9uYW1lIjoic2liZXJzIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIl0sImV4cCI6MTcwNjkzODY5MCwiYXV0aG9yaXRpZXMiOlsiUk9MRV9DT01QQVQiLCJST0xFX1BSSVZJTEVHRUQiLCJST0xFX0FETUlOIl0sImp0aSI6IjcwYTk2ZTRmLTkxOGMtNDAzYy04ZWFkLTRhZTliNTMxYjRiMCIsImNsaWVudF9pZCI6InhzY29yZXMtYXBwIn0.Y0zlTrWZzMKx13MDFxSNw5v9jtS7-1urQjR9Y-xy5rg',
}


url = "https://api-amazon.xscores.com/m_leagueresult1"

def get_api_data(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logging.error(f'Other error occurred: {err}')

def collect_and_process_data(url, headers):
    all_data = []
    for round_num in range(1, 15):
        params = {
            'sport': '1',
            'league_code': '64117',
            'round': str(round_num),
            'country_name': 'ARGENTINA',
            'seasonName': '2023/2024'
        }
        
        api_response = get_api_data(url, headers=headers, params=params)
        if api_response:
            scores = api_response[0].get('scores', [])
            for game in scores:
                game_data = {
                    'Local': game.get('home'),
                    'Visitante': game.get('away'),
                    'Resultado': game.get('ftScore', ''),
                    'Fecha': game.get('round')
                }
                all_data.append(game_data)
        else:
            logging.warning(f'No data for round {round_num}')

    return pd.DataFrame(all_data)
