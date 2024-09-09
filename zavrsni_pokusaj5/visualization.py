#####Svi kodovi za izradu različitih grafova

#################################################

# Bar chart za pojedinu statistiku
# Prosjek svake statistike igraca za sezonu
# Prosjek tima tog igraca za sezonu
# Prosjek svih igrača u sezoni

'''import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import ipywidgets as widgets
from IPython.display import display
import plotly.io as pio
import re
from difflib import get_close_matches
import sys

pio.renderers.default = 'colab'

#######################################
# Handle button click functions
def get_selected_seasons():
    selected_values = [cb.description for cb in checkboxes_season if cb.value]
    return selected_values

def on_button_click(b):
    selected_seasons = get_selected_seasons()

    if selected_seasons:
        df_player = load_data(selected_seasons)
        print(f"Data loaded for: {', '.join(selected_seasons)}")
        return df_player
    else:
        print("No seasons selected.")
        return None

####################################################
# Get folder paths based on selected seasons
def get_folder_paths(selected_seasons):
    return [custom_values[season] for season in selected_seasons]

def load_data(selected_seasons):
    folder_paths = get_folder_paths(selected_seasons)

    player_data = []

    for folder in folder_paths:
        player_df = pd.read_csv(f'scraped_data/{folder}/players_data.csv')

        player_data.append(player_df)

    if len(player_data) > 1:
        df_player = pd.concat(player_data)
    else:
        df_player = player_data[0]

    return df_player

######################################################
# Check if player exists and get their team
def check_player_exists(df, player_name):
    matching_players = df[df['playerName'] == player_name]

    if matching_players.empty:
        player_names_list = df['playerName'].tolist()
        closest_match_array = get_close_matches(player_name, player_names_list, n=1, cutoff=0.6)
        if closest_match_array:
            closest_match = closest_match_array[0]
            print(f'Closest match for {player_name} is {closest_match}.')
            return closest_match
        else:
            print(f"Player {player_name} does not exist in the table.")
            sys.exit()

    if not matching_players.empty:
        return matching_players['playerName'].iloc[0]  # Return the found player
    else:
        print(f"Player '{player_name.title()}' does not exist in the table.")
        sys.exit()


def get_team_name(df, player_name):
    global selected_team

    filtered_df = df[df['playerName'] == player_name]
    team_name_array = filtered_df['team'].unique()

    if len(team_name_array) == 1:
        return team_name_array[0]

    elif len(team_name_array) > 1:
        print(f'Player played for these teams: {team_name_array} during selected time frame')
        print(f'Data for their last team: {team_name_array[0]} will be shown.')
        return team_name_array[0]

    else:
        print("No team found.")
        return None

# Custom values for seasons
custom_values = {
    "Season 23/24": "Season_2024",
    "Season 22/23": "Season_2023"
}

#########################################
# Plot graph
def plot_comparison(player_name, team_name, player_avg_stats, team_avg_stats, average_stats_all, **kwargs):    # Determine selected stats from checkboxes
    selected_stats = [col for col, checked in kwargs.items()
                  if (isinstance(checked, bool) and checked) or
                     (isinstance(checked, pd.Series) and checked.any())]

    if not selected_stats:
        print("Please select at least one stat to display.")
        return
    formatted_stats = [format_column_name(stat) for stat in selected_stats]

    comparison_df = pd.DataFrame({
        'Stat': formatted_stats,
        'Average Player Stats': player_avg_stats[selected_stats].values,
        'Average Team Stats': team_avg_stats[selected_stats].values,
        'Average All Players Stats': average_stats_all[selected_stats].values,
    })

    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=comparison_df['Stat'],
        y=comparison_df['Average Player Stats'],
        name='Player',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=comparison_df['Stat'],
        y=comparison_df['Average Team Stats'],
        name='Team',
        marker_color='green'
    ))

    fig.add_trace(go.Bar(
        x=comparison_df['Stat'],
        y=comparison_df['Average All Players Stats'],
        name='All Players',
        marker_color='orange'
    ))

    fig.update_layout(
        title=f'Average Stats: {player_name} vs. {team_name} vs. All Players',
        xaxis_title='Statistics',
        yaxis_title='Values',
        barmode='group',
        xaxis=dict(tickmode='linear')
    )

    fig.show()

player_name_input = str(input("Enter the name of the player: "))

# Create checkboxes for each season
checkboxes_season = []
for value in custom_values.keys():
    checkbox = widgets.Checkbox(value=False, description=value)
    checkboxes_season.append(checkbox)

checkbox_container = widgets.VBox(checkboxes_season)

# Button to confirm selection of seasons
button = widgets.Button(description="Confirm Selection")

# Display checkboxes and button
display(checkbox_container, button)

def format_column_name(name):
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.title()
    return name

def main():
    df_player = None

    def callback_handler(b):
        nonlocal df_player
        df_player = on_button_click(b)
        if df_player is not None:
          player_name = check_player_exists(df_player, player_name_input)
          team_name = get_team_name(df_player, player_name)

          average_stats_per_player = df_player.groupby('playerName').mean(numeric_only=True).reset_index()
          player_avg_stats = average_stats_per_player[average_stats_per_player['playerName'] == player_name].iloc[0]

          average_stats_per_team = df_player.groupby('team').mean(numeric_only = True).reset_index()
          team_avg_stats = average_stats_per_team[average_stats_per_team['team'] == team_name].iloc[0]

          average_stats_all_df = df_player.mean(numeric_only = True).reset_index()
          average_stats_all = average_stats_all_df.set_index('index')[0]  # Convert DataFrame to Series

          # Prepare checkboxes
          column_names = df_player.select_dtypes(include=['number']).columns
          column_name_mapping = {col: format_column_name(col) for col in column_names}
          checkboxes = {col: widgets.Checkbox(value=False, description=column_name_mapping.get(col, col)) for col in column_names}

          # Interactive widget to dynamically update the plot
          interactive_plot = widgets.interactive(plot_comparison, player_name=widgets.fixed(player_name),
                                                 team_name=widgets.fixed(team_name),
                                                 player_avg_stats=widgets.fixed(player_avg_stats),
                                                 team_avg_stats=widgets.fixed(team_avg_stats),
                                                 average_stats_all=widgets.fixed(average_stats_all),
                                                 **checkboxes)
          display(interactive_plot)


    button.on_click(callback_handler)

main()
'''

########################################
# Usporedba između dva tima
# Pie chart s postotcima pobjeda svakog tima
# Bar chart usporedba statistika između dva tima

'''import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import ipywidgets as widgets
from IPython.display import display
import plotly.io as pio
import re
from difflib import get_close_matches
import sys

pio.renderers.default = 'colab'

#######################################
# Handle button click functions
def get_selected_seasons():
    selected_values = [cb.description for cb in checkboxes_season if cb.value]
    return selected_values

def on_button_click(b):
    selected_seasons = get_selected_seasons()
    
    if selected_seasons:
        df_teams, df_games = load_data(selected_seasons)
        print(f"Data loaded for: {', '.join(selected_seasons)}")
        return df_teams, df_games
    else:
        print("No seasons selected.")
        return None, None


####################################################
# Get folder paths based on selected seasons
def get_folder_paths(selected_seasons):
    return [custom_values[season] for season in selected_seasons]

def load_data(selected_seasons):
    folder_paths = get_folder_paths(selected_seasons)
    
    # Load data from each season
    team_data = []
    game_data = []
    
    for folder in folder_paths:
        team_df = pd.read_csv(f'scraped_data/{folder}/teams_data.csv')
        game_df = pd.read_csv(f'scraped_data/{folder}/games_data.csv')
        
        team_data.append(team_df)
        game_data.append(game_df)
    
    # Merge data if multiple seasons are selected
    if len(team_data) > 1:
        df_teams = pd.concat(team_data)
        df_games = pd.concat(game_data)
    else:
        df_teams = team_data[0]
        df_games = game_data[0]
    
    return df_teams, df_games



#############################################
# Check if team exists functions
def validate_team(df, team_name):
    """Validates the existence of a team in the DataFrame, or finds the closest match."""
    matching_team = df[df['team'].str.strip().str.lower() == team_name.strip().lower()]
    if matching_team.empty:
        closest_match = get_closest_team_match(df, team_name)
        if closest_match:
            matching_team = df[df['team'].str.strip().str.lower() == closest_match.strip().lower()]
        else:
            print(f"Team '{team_name}' does not exist in the table.")
            sys.exit()
    return matching_team['team'].iloc[0]

def get_closest_team_match(df, team_name):
    """Returns the closest matching team name from the DataFrame."""
    team_name = team_name.strip().lower()
    team_names_list = df['team'].str.strip().str.lower().tolist()

    closest_match_array = get_close_matches(team_name, team_names_list, n=1, cutoff=0.6)
    if closest_match_array:
        closest_match = closest_match_array[0]
        print(f"Closest match for '{team_name}' is '{closest_match}'.")
        return closest_match

    matching_teams = df[df['team'].str.strip().str.lower().str.contains(team_name)]
    if not matching_teams.empty:
        closest_match = matching_teams.iloc[0]['team']
        print(f"Assuming you meant: '{closest_match}'.")
        return closest_match

    print(f"No close match found for '{team_name}'.")
    return None


############################################
# Calculating stats functions
def calculate_team_wins(df_games, team_1, team_2):
    """Calculates the number of wins for each team in head-to-head games."""
    team_1_wins, team_2_wins = 0, 0

    for _, game in df_games.iterrows():
        if (game['visitorsTeam'] == team_1 and game['visitorsTeamPoints'] > game['homeTeamPoints']) or \
           (game['homeTeam'] == team_1 and game['homeTeamPoints'] > game['visitorsTeamPoints']):
            team_1_wins += 1
        elif (game['visitorsTeam'] == team_2 and game['visitorsTeamPoints'] > game['homeTeamPoints']) or \
             (game['homeTeam'] == team_2 and game['homeTeamPoints'] > game['visitorsTeamPoints']):
            team_2_wins += 1

    total_games = len(df_games)
    if total_games == 0:
        print("These teams did not play against each other in the given time frame.")
        sys.exit()

    return team_1_wins, team_2_wins, total_games

def calculate_win_percentages(team_1_wins, team_2_wins, total_games):
    """Calculates win percentages for both teams."""
    team_1_win_percentage = (team_1_wins / total_games) * 100
    team_2_win_percentage = (team_2_wins / total_games) * 100
    return team_1_win_percentage, team_2_win_percentage

def get_average_team_stats(df_teams, team_name, opponent_name):
    """Returns the average statistics of a team against a specific opponent."""
    team_stats_df = df_teams[
        (df_teams['team'] == team_name) & (df_teams['opponentTeam'] == opponent_name)
    ]
    return team_stats_df.mean(numeric_only=True)


###############################################
# Plot functions
def plot_win_percentage_pie(team_1, team_2, team_1_win_percentage, team_2_win_percentage):
    """Plots a pie chart showing the win percentage of each team."""
    fig = go.Figure(data=[go.Pie(labels=[team_1, team_2],
                                 values=[team_1_win_percentage, team_2_win_percentage],
                                 hole=.3,
                                 marker=dict(colors=['blue', 'green']))])
    fig.update_layout(title_text=f'Win Percentage: {team_1} vs. {team_2}')
    fig.show()

def plot_team_stat_comparison(team_name_1, team_name_2, avg_stats_team_1, avg_stats_team_2, **kwargs):
    """Plots a bar chart comparing selected statistics between two teams."""
    selected_stats = [col for col, checked in kwargs.items() if checked]

    if not selected_stats:
        print("Please select at least one stat to display.")
        return

    formatted_stats = [format_column_name(stat) for stat in selected_stats]

    comparison_df = pd.DataFrame({
        'Stat': formatted_stats,
        'Team 1 Stats': avg_stats_team_1[selected_stats].values,
        'Team 2 Stats': avg_stats_team_2[selected_stats].values,
    })

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=comparison_df['Stat'],
        y=comparison_df['Team 1 Stats'],
        name=team_name_1,
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=comparison_df['Stat'],
        y=comparison_df['Team 2 Stats'],
        name=team_name_2,
        marker_color='green'
    ))

    fig.update_layout(
        title=f'Average Stats: {team_name_1} vs. {team_name_2}',
        xaxis_title='Statistics',
        yaxis_title='Values',
        barmode='group'
    )

    fig.show()



#######################################
# Custom values for seasons
custom_values = {
    "Season 23/24": "Season_2024",
    "Season 22/23": "Season_2023"
}

# Get teams input
team_1_input = str(input("Enter the name of the first team: "))
team_2_input = str(input("Enter the name of the second team: "))

# Create checkboxes for each season
checkboxes_season = []
for value in custom_values.keys():
    checkbox = widgets.Checkbox(value=False, description=value)
    checkboxes_season.append(checkbox)

checkbox_container = widgets.VBox(checkboxes_season)

# Button to confirm selection of seasons
button = widgets.Button(description="Confirm Selection")

# Display checkboxes and button
display(checkbox_container, button)

def format_column_name(name):
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.title()
    return name

# Main function to process the teams and display results
def main():
    df_teams, df_games = None, None
    
    def callback_handler(b):
        nonlocal df_teams, df_games
        df_teams, df_games = on_button_click(b)
        
        if df_teams is not None and df_games is not None:
            team_1 = validate_team(df_teams, team_1_input)
            team_2 = validate_team(df_teams, team_2_input)

            if team_1 == team_2:
                print("Please enter two different teams.")
                return

            team_1 = team_1.title()
            team_2 = team_2.title()

            team_1_vs_team_2_games = df_games[
                ((df_games['visitorsTeam'] == team_1) & (df_games['homeTeam'] == team_2)) |
                ((df_games['visitorsTeam'] == team_2) & (df_games['homeTeam'] == team_1))
            ]

            # Calculate wins and win percentages
            team_1_wins, team_2_wins, total_games = calculate_team_wins(df_games=team_1_vs_team_2_games, team_1=team_1, team_2=team_2)
            team_1_win_percentage, team_2_win_percentage = calculate_win_percentages(team_1_wins, team_2_wins, total_games)
            
            # Get average stats for both teams
            average_stats_team_1 = get_average_team_stats(df_teams, team_1, team_2)
            average_stats_team_2 = get_average_team_stats(df_teams, team_2, team_1)

            # Prepare checkboxes for statistic selection
            column_names = df_teams.select_dtypes(include=['number']).columns
            column_name_mapping = {col: format_column_name(col) for col in column_names}
            checkboxes = {col: widgets.Checkbox(value=False, description=column_name_mapping.get(col, col)) for col in column_names}
            
            plot_win_percentage_pie(team_1, team_2, team_1_win_percentage, team_2_win_percentage)
            # Interactive widget to dynamically update the plot
            interactive_plot = widgets.interactive(plot_team_stat_comparison, team_name_1=widgets.fixed(team_1), team_name_2=widgets.fixed(team_2), avg_stats_team_1=widgets.fixed(average_stats_team_1), avg_stats_team_2=widgets.fixed(average_stats_team_2), **checkboxes)
            display(interactive_plot)

    button.on_click(callback_handler)

main()
'''
#########################
# Statistika igrača za određeni vremenski period

'''import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import ipywidgets as widgets
from IPython.display import display
import plotly.io as pio
import re
from difflib import get_close_matches
import sys

pio.renderers.default = 'colab'

#######################################
# Handle button click functions
def get_selected_seasons():
    selected_season_key = radio_buttons_season.value
    selected_seasons_value = custom_values[selected_season_key]
    return selected_seasons_value

def on_button_click(b):
    selected_seasons = get_selected_seasons()

    if selected_seasons:
        df_player = load_data(selected_seasons)
        print(f"Data loaded for: {', '.join(selected_seasons)}")
        return df_player
    else:
        print("No seasons selected.")
        return None


###################################################
# Get folder paths based on selected seasons
def get_folder_paths(selected_seasons):
    return selected_seasons

def load_data(selected_seasons):
    folder_paths = get_folder_paths(selected_seasons)
    player_data = []

    for folder in folder_paths:
        player_df = pd.read_csv(f'scraped_data/{folder}/players_data.csv')
        player_data.append(player_df)
    if len(player_data) > 1:

        df_player = pd.concat(player_data)
    else:
        df_player = player_data[0]
    return df_player

########################################
# Check if the player exists
def check_player_exists(df, player_name):
    matching_players = df[df['playerName'] == player_name]

    if matching_players.empty:
        player_names_list = df['playerName'].tolist()
        closest_match_array = get_close_matches(player_name, player_names_list, n=1, cutoff=0.6)
        if closest_match_array:
            closest_match = closest_match_array[0]
            print(f'Closest match for {player_name} is {closest_match}.')
            return closest_match
        else:
            print(f"Player {player_name} does not exist in the table.")
            sys.exit()

    if not matching_players.empty:
        return matching_players['playerName'].iloc[0]  # Return the found player
    else:
        print(f"Player '{player_name.title()}' does not exist in the table.")
        sys.exit()

#####################################
# Calculate stats
def get_nba_season(date):
    year = date.year
    if date.month >= 10:
        return f'{year}-{year + 1}'
    else:
        return f'{year - 1}-{year}'

def calculate_average_stats(df, player_name, parameter):
    df_player = df.copy()
    df_player['gameDate'] = pd.to_datetime(df_player['gameDate'])

    if parameter == "season":
        df_player['NBA_Season'] = df_player['gameDate'].apply(get_nba_season)
        df_season_avg = df_player.groupby('NBA_Season').mean(numeric_only=True)
        return df_season_avg

    elif parameter == "month":
        df_player['Month_Year'] = df_player['gameDate'].dt.strftime('%B/%Y')  # E.g., "May/2023"
        df_player['Month_Year_dt'] = df_player['gameDate'].dt.to_period('M').dt.to_timestamp()

        df_months_avg = df_player.groupby('Month_Year').mean(numeric_only=True)
        df_months_avg = df_months_avg.sort_index(key=lambda x: pd.to_datetime(x, format='%B/%Y'))
        return df_months_avg


###############################
# Plot graph
def plot_avg_stats_for_timeframe(player, avg_stats, **kwargs):
    selected_stats = [col for col, checked in kwargs.items() if checked]

    if not selected_stats:
        print("Please select at least one stat to display.")
        return

    formatted_stats = [format_column_name(stat) for stat in selected_stats]

    # Create subplots
    fig = sp.make_subplots(rows=len(selected_stats), cols=1, subplot_titles=formatted_stats)

    for i, stat in enumerate(selected_stats):
        fig.add_trace(
            go.Scatter(x=avg_stats.index, y=avg_stats[stat], mode='lines+markers', name=format_column_name(stat)),
            row=i + 1, col=1
        )
        fig.update_yaxes(range=[0, avg_stats[stat].max() * 1.1], row=i + 1, col=1)

    fig.update_layout(height=300 * len(selected_stats), title_text=f'Average Stats for {player}', showlegend=True)

    fig.show()

###############################
# Custom values for seasons
custom_values = {
    "All Seasons": ["Season_2024", "Season_2023", "Season_2022"],
    "Season 23/24": ["Season_2024"],
    "Season 22/23": ["Season_2023"],
    "Season 21/21": ["Season_2022"]

}

player_input = str(input("Enter the name of the player: "))

# Create radio buttons for season selection
radio_buttons_season = widgets.RadioButtons(
    options=list(custom_values.keys()), 
    description='Select Season:',
    disabled=False
)

# Button to confirm selection of seasons
button = widgets.Button(description="Confirm Selection")

# Display checkboxes and button
display(radio_buttons_season, button)

def format_column_name(name):
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.title()
    return name

# Main function to process the teams and display results
def main():
    df_player = None

    def callback_handler(b):
        nonlocal df_player
        df_player = on_button_click(b)

        if df_player is not None:
            player_name = check_player_exists(df_player, player_input)
            player_stats_df = df_player[df_player['playerName'] == player_name]
            if len(get_selected_seasons()) > 1:
                df_avg = calculate_average_stats(player_stats_df, player_name, "season")
            else:
                df_avg = calculate_average_stats(player_stats_df, player_name, "month")

            column_names = df_player.select_dtypes(include=['number']).columns
            column_name_mapping = {col: format_column_name(col) for col in column_names}

            # Create checkboxes with formatted column names
            checkboxes = {col: widgets.Checkbox(value=False, description=column_name_mapping.get(col, col)) for col in column_names}
            interactive_plot = widgets.interactive(plot_avg_stats_for_timeframe, player=widgets.fixed(player_name), avg_stats=widgets.fixed(df_avg), **checkboxes)
            display(interactive_plot)

    button.on_click(callback_handler)

main()'''

#################################
# Statistika tima za određeni vremenski period

'''import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import ipywidgets as widgets
from IPython.display import display
import plotly.io as pio
import re
from difflib import get_close_matches
import sys


pio.renderers.default = 'colab'

#######################################
# Handle button click functions
def get_selected_seasons():
    selected_season_key = radio_buttons_season.value
    selected_seasons_value = custom_values[selected_season_key]
    return selected_seasons_value

def on_button_click(b):
    selected_seasons = get_selected_seasons()

    if selected_seasons:
        df_team = load_data(selected_seasons)
        print(f"Data loaded for: {', '.join(selected_seasons)}")
        return df_team
    else:
        print("No seasons selected.")
        return None

###################################################
# Load data based on selected seasons
def get_folder_paths(selected_seasons):
    return selected_seasons

def load_data(selected_seasons):
    folder_paths = get_folder_paths(selected_seasons)
    team_data = []

    for folder in folder_paths:
        team_df = pd.read_csv(f'scraped_data/{folder}/teams_data.csv')
        team_data.append(team_df)

    if len(team_data) > 1:
        df_team = pd.concat(team_data)
    else:
        df_team = team_data[0]
    return df_team

########################################
# Check if team exists
def validate_team(df, team_name):
    matching_team = df[df['team'].str.strip().str.lower() == team_name.strip().lower()]
    if matching_team.empty:
        closest_match = get_closest_team_match(df, team_name)
        if closest_match:
            matching_team = df[df['team'].str.strip().str.lower() == closest_match.strip().lower()]
        else:
            print(f"Team '{team_name}' does not exist.")
            sys.exit()
    return matching_team['team'].iloc[0]

def get_closest_team_match(df, team_name):
    team_name = team_name.strip().lower()
    team_names_list = df['team'].str.strip().str.lower().tolist()
    closest_match_array = get_close_matches(team_name, team_names_list, n=1, cutoff=0.6)
    if closest_match_array:
        closest_match = closest_match_array[0]
        print(f"Closest match for '{team_name}' is '{closest_match}'.")
        return closest_match
    matching_teams = df[df['team'].str.strip().str.lower().str.contains(team_name)]
    if not matching_teams.empty:
        closest_match = matching_teams.iloc[0]['team']
        print(f"Assuming you meant: '{closest_match}'.")
        return closest_match
    print(f"No close match found for '{team_name}'.")
    return None

#####################################
# Calculate stats
def get_nba_season(date):
    year = date.year
    if date.month >= 10:
        return f'{year}-{year + 1}'
    else:
        return f'{year - 1}-{year}'

def calculate_average_stats(df, team_name, parameter):
    df_team = df.copy()
    df_team['gameDate'] = pd.to_datetime(df_team['gameDate'])

    if parameter == "season":
        df_team['NBA_Season'] = df_team['gameDate'].apply(get_nba_season)
        df_season_avg = df_team.groupby('NBA_Season').mean(numeric_only=True)
        return df_season_avg

    elif parameter == "month":
        df_team['Month_Year'] = df_team['gameDate'].dt.strftime('%B/%Y')  # "May/2023"
        df_team['Month_Year_dt'] = df_team['gameDate'].dt.to_period('M').dt.to_timestamp()

        df_months_avg = df_team.groupby('Month_Year').mean(numeric_only=True)
        df_months_avg = df_months_avg.sort_index(key=lambda x: pd.to_datetime(x, format='%B/%Y'))
        return df_months_avg


###############################
# Plot graph
def plot_avg_stats_for_timeframe(team, avg_stats, **kwargs):
    selected_stats = [col for col, checked in kwargs.items() if checked]

    if not selected_stats:
        print("Please select at least one stat to display.")
        return

    formatted_stats = [format_column_name(stat) for stat in selected_stats]

    # Create subplots
    fig = sp.make_subplots(rows=len(selected_stats), cols=1, subplot_titles=formatted_stats)

    for i, stat in enumerate(selected_stats):
        fig.add_trace(
            go.Scatter(x=avg_stats.index, y=avg_stats[stat], mode='lines+markers', name=format_column_name(stat)),
            row=i + 1, col=1
        )

        fig.update_yaxes(range=[0, avg_stats[stat].max() * 1.1], row=i + 1, col=1)

    fig.update_layout(height=300 * len(selected_stats), title_text=f'Average Stats for {team}', showlegend=True)
    fig.show()


###############################
# Custom values for seasons
custom_values = {
    "All Seasons": ["Season_2024", "Season_2023", "Season_2022"],
    "Season 23/24": ["Season_2024"],
    "Season 22/23": ["Season_2023"],
    "Season 21/22": ["Season_2022"]
}

team_input = str(input("Enter the name of the team: "))

# Create radio buttons for season selection
radio_buttons_season = widgets.RadioButtons(
    options=list(custom_values.keys()),
    description='Select Season:',
    disabled=False
)

# Button to confirm selection of seasons
button = widgets.Button(description="Confirm Selection")

# Display checkboxes and button
display(radio_buttons_season, button)

def format_column_name(name):
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.title()
    return name

# Main function
def main():
    df_team = None

    def callback_handler(b):
        nonlocal df_team
        df_team = on_button_click(b)

        if df_team is not None:
            team_name = validate_team(df_team, team_input)
            team_name = team_name.title()
            team_stats_df = df_team[df_team['team'] == team_name]
            if len(get_selected_seasons()) > 1:
                df_avg = calculate_average_stats(team_stats_df, team_name, "season")
            else:
                df_avg = calculate_average_stats(team_stats_df, team_name, "month")

            column_names = df_team.select_dtypes(include=['number']).columns
            column_name_mapping = {col: format_column_name(col) for col in column_names}

            # Create checkboxes with formatted column names
            checkboxes = {col: widgets.Checkbox(value=False, description=column_name_mapping.get(col, col)) for col in column_names}
            interactive_plot = widgets.interactive(plot_avg_stats_for_timeframe, team=widgets.fixed(team_name), avg_stats=widgets.fixed(df_avg), **checkboxes)
            display(interactive_plot)

    button.on_click(callback_handler)
main()'''