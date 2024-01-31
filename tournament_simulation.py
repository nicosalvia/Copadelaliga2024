import pandas as pd
import random
from itertools import combinations
import tkinter as tk
from tkinter import filedialog
from Copadelaliga2024.import_results import collect_and_process_data

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsib2F1dGgyX3hzY29yZXNfYXBwbGljYXRpb24iXSwidXNlcl9uYW1lIjoic2liZXJzIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIl0sImV4cCI6MTcwNjkzODY5MCwiYXV0aG9yaXRpZXMiOlsiUk9MRV9DT01QQVQiLCJST0xFX1BSSVZJTEVHRUQiLCJST0xFX0FETUlOIl0sImp0aSI6IjcwYTk2ZTRmLTkxOGMtNDAzYy04ZWFkLTRhZTliNTMxYjRiMCIsImNsaWVudF9pZCI6InhzY29yZXMtYXBwIn0.Y0zlTrWZzMKx13MDFxSNw5v9jtS7-1urQjR9Y-xy5rg',
}


url = "https://api-amazon.xscores.com/m_leagueresult1"


teams_zone_a = {
    "HURACAN", "RIVER PLATE", "BANFIELD", "ROSARIO CENTRAL", "INDEPENDIENTE",
    "VELEZ SARSFIELD", "INSTITUTO CORDOBA", "INDEPENDIENTE RIVADAVIA", "TALLERES CORDOBA", "ATLETICO TUCUMAN",
    "GIMNASIA LA PLATA", "ARGENTINOS JRS", "BARRACAS CENTRAL", "DEPORTIVO RIESTRA"
}

teams_zone_b = {
    "RACING CLUB", "GODOY CRUZ", "BELGRANO CORDOBA", "PLATENSE", "CENTRAL CORDOBA",
    "NEWELLS OLD BOYS", "BOCA JUNIORS", "SAN LORENZO", "ESTUDIANTES L.P.",
    "SARMIENTO JUNIN", "UNION SANTA FE'", "DEFENSA Y JUSTICIA", "TIGRE", "LANUS"
}

#file_path = r'C:\Users\Nico\Downloads\matches - original.csv'


# Define a function to determine the winner based on the 'Resultado' column
def determine_winner(Resultado):
    # Split the result into home and away goals
    if Resultado != '':  # If the game hasn't been played yet, return ''
        home_goals, away_goals = map(int, Resultado.split('-'))
        if home_goals > away_goals:
            return 'Local'
        elif home_goals < away_goals:
            return 'Visitante'
        elif home_goals == away_goals:
            return 'Empate'
        else:
            return ''
    else:
        return ''


# Collect and process the data
data = collect_and_process_data(url, headers)
data['Ganador'] = data['Resultado'].apply(determine_winner)
results_df = data



def assign_zone(team):
    '''Assign zone based on the team's name.'''
    if team in teams_zone_a:
        return 'A'
    elif team in teams_zone_b:
        return 'B'
    else:
        return None  # In case the team is not found in either set

def update_transitivity_matrix(matrix, winner, loser):
    """Update the transitivity matrix based on a match result."""
    if winner not in matrix or loser not in matrix:
        return

    matrix[winner][loser] = True
    for team in matrix:
        if matrix[loser][team]:
            matrix[winner][team] = True
        if matrix[team][winner]:
            matrix[team][loser] = True

def simulate_match_based_on_transitivity(team1, team2, matrix):
    """Simulate a match outcome based on the transitivity matrix."""

    # This is an educated guess, the base probability distribution for locals was [0.48, 0.34, 0.18] for 2023, I assume that the transitivity increases by ~10% probability of winning
    if matrix[team1][team2]:
        outcomes = ['Local', 'Empate', 'Visitante']
        probabilities = [0.6, 0.3, 0.1]
    elif matrix[team2][team1]:
        outcomes = ['Local', 'Empate', 'Visitante']
        probabilities = [0.4, 0.3, 0.3]
    else:
        outcomes = ['Local', 'Empate', 'Visitante']
        probabilities = [0.48, 0.34, 0.18]
    return random.choices(outcomes, probabilities, k=1)[0]


all_teams = set(results_df['Local'].unique()).union(set(results_df['Visitante'].unique()))


# Initialize a single transitivity matrix for all teams
transitivity_matrix = {team: {other_team: False for other_team in all_teams} for team in all_teams}



def simulate_tournament(results_df):
    '''Simulate the tournament and return the standings and transitivity matrix.'''

    # Sort the dataframe by 'Fecha'
    results_df = results_df.sort_values(by='Fecha')

    # Initialize all unique teams from the matches
    all_teams = set(results_df['Local'].unique()).union(set(results_df['Visitante'].unique()))

    # Initialize standings and transitivity matrix for all teams
    standings = {team: {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0} for team in all_teams}
    #transitivity_matrix = {team: {other_team: False for other_team in all_teams if other_team != team} for team in all_teams}

    # Update standings and transitivity matrix with actual results
    for _, row in results_df.iterrows():
        team1, team2 = row['Local'], row['Visitante']
        result = row['Ganador']
        
        if result == '':
            result = simulate_match_based_on_transitivity(team1, team2, transitivity_matrix)

        update_standings(standings, team1, team2, result)
        update_transitivity_matrix(transitivity_matrix, team1, team2)

    return standings


def update_standings(standings, team1, team2, result):
    """Update the standings based on the match result."""
    if result == 'Local':
        standings[team1]['wins'] += 1
        standings[team1]['points'] += 3
        standings[team2]['losses'] += 1
    elif result == 'Visitante':
        standings[team2]['wins'] += 1
        standings[team2]['points'] += 3
        standings[team1]['losses'] += 1
    elif result == 'Empate':
        standings[team1]['draws'] += 1
        standings[team1]['points'] += 1 
        standings[team2]['draws'] += 1
        standings[team2]['points'] += 1

def print_standings(standings):
    """Print the final standings for each zone."""
    df = pd.DataFrame.from_dict(standings, orient='index')
    
    # Assuming 'teams_zone_a' and 'teams_zone_b' are defined globally or passed to this function
    df_zone_a = df[df.index.isin(teams_zone_a)]
    df_zone_b = df[df.index.isin(teams_zone_b)]

    print("Standings for Zona A:")
    print(df_zone_a.sort_values(by='points', ascending=False))
    print("\nStandings for Zona B:")
    print(df_zone_b.sort_values(by='points', ascending=False))

        



def calculate_fechas_info(results_df):
    """Calculate and print information about played and simulated 'fechas' for each zone."""
    grouped = results_df.groupby('Fecha')

    for zone, group in grouped:
        total_fechas = group['Fecha'].nunique()
        played_fechas = group.dropna(subset=['Ganador'])['Fecha'].nunique()
        simulated_fechas = total_fechas - played_fechas

        print(f"\nZone {zone}:")
        print(f"  Total Fechas: {total_fechas}")
        print(f"  Played Fechas: {played_fechas}")
        print(f"  Simulated Fechas: {simulated_fechas}")

def validate_results_column(df):
    """Validate the 'Ganador' column in the dataframe, allowing NaN values."""
    allowed_values = {'Local', 'Visitante', 'Empate', ''}
    # Filter out NaN values using pandas notna() before checking for invalid values
    invalid_values = set(df[df['Ganador'].notna()]['Ganador']) - allowed_values

    if invalid_values:
        print(f"Error: Invalid values found in 'Ganador' column: {invalid_values}")
        return False
    return True

def validate_complete_fechas(df):
    """Validate that for all fechas with more than zero results, 
       the count of rows is equal to the count of non-null results."""
    grouped = df.groupby(['Fecha'])

    for (Fecha), group in grouped:
        if not group['Ganador'].isna().all():  # Check if there's at least one non-null result
            total_rows = len(group)
            non_null_results = group['Ganador'].notna().sum()

            if total_rows != non_null_results:
                print(f"Error: Incomplete results for Fecha {Fecha}.")
                return False
    return True

def predict_or_display_fecha_results(Fecha, results_df, zone_transitivity_matrix):
    """Predicts or displays results for a specific Fecha."""
    fecha_matches = results_df[results_df['Fecha'] == Fecha]

    # Check if the Fecha has been played (i.e., results are not NaN)
    if not fecha_matches['Ganador'].all() == '':
        print(f"Results for Fecha {Fecha} (already played):")
        print(fecha_matches[['Zona', 'Local', 'Visitante', 'Ganador']])
    else:
        print(f"Predicted results for Fecha {Fecha} (not yet played):")
        for _, row in fecha_matches.iterrows():
            zone = row['Zona']
            team1 = row['Local']
            team2 = row['Visitante']
            predicted_result = simulate_match_based_on_transitivity(team1, team2, zone_transitivity_matrix[zone])
            print(f"Zone {zone}: {team1} vs {team2} - {predicted_result}")


# [Rest of the functions remain the same]

if __name__ == "__main__":
    # ... [any other initializations or simulations] ...

    print("Select an option:")
    print("1. Predict or display results for a specific Fecha.")
    print("2. Show the full table.")
    choice = input("Enter your choice (1 or 2): ")

    if results_df is not None:
        # Run the simulation or processing to get zone_standings and zone_transitivity_matrix
        standings = simulate_tournament(results_df)
       # zone_transitivity_matrix = {'A': {}, 'B': {}}

        print("Select an option:")
        print("1. Predict or display results for a specific Fecha.")
        print("2. Show the full table.")
        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            print("OK")
            fecha_to_predict = input("Enter the Fecha you want to predict or display: ")
            try:
                fecha_to_predict = int(fecha_to_predict)
                predict_or_display_fecha_results(fecha_to_predict, results_df, zone_standings, zone_transitivity_matrix)
            except ValueError:
                print("Invalid input. Please enter a numerical value for Fecha.")
        elif choice == '2':
    
            if results_df is not None and validate_results_column(results_df):
                if validate_complete_fechas(results_df):
                    standings = simulate_tournament(results_df)
                    calculate_fechas_info(results_df)
                    print_standings(standings)
                else:
                    print("Incomplete data in the tournament results.")
            else:
                print("Failed to process the tournament results.")
        else:
            print("Invalid choice. Please enter 1 or 2.")
    else:
        print("Failed to load the tournament results.")

