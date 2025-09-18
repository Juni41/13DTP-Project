import random
from collections import defaultdict

def create_random_matches(players, num_courts):
    # Create a new list from the players list to change it without changing original list.
    available = list(players)
    matches = [] # Initialize an empty list.
    random.shuffle(available)
    
    # Loop from 1 up to the total number of courts to create a match for each court.
    for court_num in range(1, num_courts + 1):
        if len(available) < 4: break # If there are fewer than 4 players left, we can't make a full match, so exit the loop.
        selected = [available.pop() for _ in range(4)] # Remove and select the last 4 players from the shuffled list to form a match.
        
        # Add a new match dictionary to the 'matches' list, splitting the 4 selected players into two teams.
        matches.append({'court': court_num, 'team1': selected[:2], 'team2': selected[2:]})
    return matches

def create_skill_based_matches(players, num_courts):
    # Create a dictionary to map skill level strings to numerical values for sorting.
    skill_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
    
    # Initialize a defaultdict where each key (a skill level) will have a list as its default value.
    tiers = defaultdict(list)
    
    # Loop through each player in the input list.
    for player in players:
        tiers[player.skill].append(player) # Group players into lists based on their skill level.

    # Iterate through the lists of players in each skill tier.
    for skill_tier in tiers.values():
        random.shuffle(skill_tier) # Shuffle the players within each skill tier.
        
    # Create a single list of all players, ordered from highest skill to lowest.
    available_players = tiers.get('Advanced', []) + \
                        tiers.get('Intermediate', []) + \
                        tiers.get('Beginner', [])
    matches = []
    possible_courts = min(num_courts, len(available_players) // 4)

    # Loop through the number of courts fillable.
    for court_num in range(1, possible_courts + 1):
        
        # Take the top 4 players from the ordered list for the current court.
        court_group = available_players[:4]
        
        # Remove those 4 players from the list of available players.
        available_players = available_players[4:]

        # Sort just the 4 players in this group by their skill score.
        court_group.sort(key=lambda p: skill_map.get(p.skill, 0), reverse=True)
        
        # Create team 1 by pairing the best player '0' with the worst player '3' in the group.
        team1 = [court_group[0], court_group[3]]
        # Create team 2 by pairing the second-best '1' and third-best '2' players.
        team2 = [court_group[1], court_group[2]]
        
        # Add the newly formed match (with court number and teams) to the matches list.
        matches.append({'court': court_num, 'team1': team1, 'team2': team2})
    return matches

def create_mixed_gender_matches(players, num_courts):
    males = [p for p in players if p.gender == 'male'] # Create a list containing only the male players.
    females = [p for p in players if p.gender == 'female'] # Create a list containing only the female players.
    
    others = [p for p in players if p.gender not in ['male', 'female']] # Create a list for any players not identified as 'Male' or 'Female'.
    random.shuffle(males)
    random.shuffle(females)
    all_teams = []
    
    # Loop as long as there is at least one male and one female player available.
    while males and females:
        # Create a team by taking one player from the end of the males list and one from the females list.
        team = [males.pop(), females.pop()]
        # Add the mixed-gender team to the list of all teams.
        all_teams.append(team)
        
    matches = []
    
    # Loop from 1 up to the total number of courts to create a match.
    for court_num in range(1, num_courts + 1):
        if len(all_teams) < 2:
            break
        
        # Pop a team from the list to be team 1 for the match.
        team1 = all_teams.pop()
        # Pop another team from the list to be team 2 for the match.
        team2 = all_teams.pop()
        
        # Add the new match to the list of matches.
        matches.append({
            'court': court_num,
            'team1': team1,
            'team2': team2
        })
    return matches
