import json
import os
import re

# Elo ranges for each rank
elo_ranges = {
    'E': (400, 699.99),
    'D': (700, 999.99),
    'C': (1000, 1299.99),
    'B': (1300, 1599.99),
    'A': (1600, 1899.99),
    'S': (1900, float('inf'))
}

# K-factor for Elo calculation
K = 32

# Load previous Elo range and match log
if os.path.exists('elo_range.json'):
    with open('elo_range.json', 'r') as f:
        narju_min_elo, narju_max_elo = json.load(f)
else:
    narju_min_elo, narju_max_elo = elo_ranges['C']

# Match log
if os.path.exists('match_log.json'):
    with open('match_log.json', 'r') as f:
        match_log = json.load(f)
else:
    match_log = []

# Function to calculate Elo change
def calculate_elo_change(Ra, Rb, Sa):
    Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
    return K * (Sa - Ea)

# Main loop
while True:
    try:
        # Ask for opponent's rank or to quit
        command = input("Enter opponent's rank, 'reset' to reset Elo, or 'q' to quit: ")

        if command.lower() == 'q':
            break
        elif command.lower() == 'reset':
            narju_min_elo, narju_max_elo = elo_ranges['C']
            print(f"narju_min_elo and narju_max_elo have been reset to {narju_min_elo} and {narju_max_elo} respectively.")
            continue

        opponent_rank = command.upper()

        # Ask for match score
        match_score = input("Enter match score (your score - opponent's score): ")

        if not re.match(r'\d+-\d+', match_score):
            raise ValueError

        # Calculate Elo change for each scenario
        elo_changes = []
        for my_elo in (narju_min_elo, narju_max_elo):
            for opponent_elo in elo_ranges[opponent_rank]:
                Sa = 1 if int(match_score.split('-')[0]) > int(match_score.split('-')[1]) else 0
                elo_change = calculate_elo_change(my_elo, opponent_elo, Sa)
                elo_change = round(elo_change, 2)  # Round to 2 decimal places
                elo_changes.append(elo_change)
                print(f'Elo change for my Elo {my_elo} and opponent Elo {opponent_elo}: {elo_change}')

        # Adjust narju_min_elo and narju_max_elo
        if min(elo_changes) < 0:
            response = input("Did your rank drop (yes/no)? ")
            if response.lower() == 'no':
                # Ensure narju_min_elo doesn't drop below the lower limit of the current rank's Elo range
                min_elo_change_at_min_elo = max(elo_changes[:2])  # Get the less negative Elo change when your Elo was at its minimum
                narju_min_elo = narju_min_elo - min_elo_change_at_min_elo
        if max(elo_changes) > 0:
            response = input("Did your rank increase (yes/no)? ")
            if response.lower() == 'no':
                # Ensure narju_max_elo doesn't exceed the upper limit of the current rank's Elo range
                min_elo_change_at_max_elo = min(elo_changes[2:])  # Get the minimum Elo change when your Elo was at its maximum
                narju_max_elo = min(narju_max_elo, elo_ranges[opponent_rank][1] - min_elo_change_at_max_elo)

        # Save Elo range and match log
        with open('elo_range.json', 'w') as f:
            json.dump((narju_min_elo, narju_max_elo), f)
        match_log.append((opponent_rank, match_score, min(elo_changes), max(elo_changes)))
        with open('match_log.json', 'w') as f:
            json.dump(match_log, f)

        # Print narju_min_elo and narju_max_elo
        print(f"narju_min_elo: {narju_min_elo}, narju_max_elo: {narju_max_elo}")

    except KeyError:
        print("Invalid Elo range. Please check your Elo ranges.")
    except ValueError:
        print("Invalid response. Please enter 'yes' or 'no'.")