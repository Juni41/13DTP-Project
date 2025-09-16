import random
from collections import defaultdict

def create_random_matches(players, num_courts):
    available = list(players)
    matches = []
    random.shuffle(available)
    for court_num in range(1, num_courts + 1):
        if len(available) < 4: break
        selected = [available.pop() for _ in range(4)]
        matches.append({'court': court_num, 'team1': selected[:2], 'team2': selected[2:]})
    return matches

def create_skill_based_matches(players, num_courts):
    skill_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3} # Define the skill-to-score mapping.
    tiers = defaultdict(list)
    for player in players:
        tiers[player.skill].append(player)

    for skill_tier in tiers.values(): # Shuffle within Strata: Shuffle players within each skill tier.
        random.shuffle(skill_tier)
        
    # Create a single, ordered list of all players.
    available_players = tiers.get('Advanced', []) + \
                        tiers.get('Intermediate', []) + \
                        tiers.get('Beginner', [])

    matches = []
    
    possible_courts = min(num_courts, len(available_players) // 4) # Build Courts from the stratified and shuffled list as the parameters.

    for court_num in range(1, possible_courts + 1):
        court_group = available_players[:4] # Take the next 4 players for this court.
        available_players = available_players[4:] # Update the list of available players

        court_group.sort(key=lambda p: skill_map.get(p.skill, 0), reverse=True) # Sort only the 4 players in this group by their skill score.
        
        team1 = [court_group[0], court_group[3]] # Use the criss cross split.
        team2 = [court_group[1], court_group[2]]
        
        matches.append({'court': court_num, 'team1': team1, 'team2': team2})
        
    return matches

def create_mixed_gender_matches(players, num_courts):
    males = [p for p in players if p.gender == 'Male']
    females = [p for p in players if p.gender == 'Female']
    others = [p for p in players if p.gender not in ['Male', 'Female']] # Leftover players put on rest.
    random.shuffle(males)
    random.shuffle(females)
    all_teams = []
    while males and females:
        team = [males.pop(), females.pop()] # Create a team by taking one player from each list.
        all_teams.append(team)
        
    matches = []
    for court_num in range(1, num_courts + 1):
        if len(all_teams) < 2: # We need at least two teams to form a court.
            break
        team1 = all_teams.pop()
        team2 = all_teams.pop()
        
        matches.append({
            'court': court_num,
            'team1': team1,
            'team2': team2
        })
    return matches
