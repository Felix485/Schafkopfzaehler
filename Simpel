import streamlit as st
import pandas as pd

def print_table(df):
    # Calculate the sum and append it as the last row
    # Adjust column names based on your DataFrame's structure
    sum_row = df.sum().to_dict()
    #sum_row['Spielart'] = 'Summe'  # Replace 'Spielart' with the appropriate column name from your DataFrame
    sum_df = pd.DataFrame([sum_row])
    combined_table = pd.concat([df, sum_df], ignore_index=True)

    # Display the combined table with the last row highlighted
    st.write(combined_table.style.apply(
        lambda x: ['background-color: darkgray' if x.name == len(combined_table) - 1 else '' for _ in x], axis=1))

def add_row_to_df(df, row):
    new_df = pd.DataFrame([row])
    return pd.concat([df, new_df], ignore_index=True)

def calculate_auto_fill_values(player_inputs, active_player_names, col_names):
    # Filter inputs for active players
    active_inputs = [value for name, value in zip(col_names, player_inputs) if name in active_player_names]

    # Calculate the sum of the active inputs
    total_sum = sum(active_inputs)

    # If the sum is already zero, no need to autofill
    if total_sum == 0:
        return player_inputs

    # Determine the number of active inputs that are zero
    num_zeros = active_inputs.count(0)

    # If there are no zeros or all are zeros, no need to autofill
    if num_zeros == 0 or num_zeros == len(active_inputs):
        return player_inputs

    # Calculate the value to autofill
    fill_value = -total_sum // num_zeros

    # Update the original inputs with the autofilled values
    updated_inputs = []
    for name, value in zip(col_names, player_inputs):
        if name in active_player_names and value == 0:
            updated_inputs.append(fill_value)
        else:
            updated_inputs.append(value)

    return updated_inputs

def register_players():
    st.title("Player Registration")

    # Allow user to choose the number of players (between 4 and 7)
    num_players = st.number_input("Number of Players (4-7)", min_value=4, max_value=7, value=4, step=1)

    # Create input fields for player names based on num_players
    player_names = [st.text_input(f"Player {i + 1} Name", key=f'player_{i}') for i in range(num_players)]

    if st.button("Register Players"):
        # Update session state with player names
        st.session_state['player_names'] = [name for name in player_names if name]

        # Initialize the scores DataFrame with new player names
        st.session_state['data'] = pd.DataFrame(columns=st.session_state['player_names'])

        st.success("Players successfully registered!")

def determine_players_to_play(round_counter):
    # Retrieve player names
    player_names = st.session_state.get('player_names', [])

    num_players = len(player_names)

    if num_players == 4:
        # All 4 players play all the time
        return player_names

    elif num_players == 5:
        # One player sits out each round in order
        sit_out_player_index = round_counter % num_players
        return [player for i, player in enumerate(player_names) if i != sit_out_player_index]

    elif num_players == 6:
        # Two players sit out each round in order
        sit_out_player_indices = {round_counter % num_players, (round_counter + 3) % num_players}
        return [player for i, player in enumerate(player_names) if i not in sit_out_player_indices]

    elif num_players == 7:
        # Three players sit out each round in order
        sit_out_player_indices = {round_counter % num_players, (round_counter + 3) % num_players, (round_counter + 4) % num_players}
        return [player for i, player in enumerate(player_names) if i not in sit_out_player_indices]

    else:
        return []

def create_input_form(col_names, active_player_names):
    inputs = []
    num_columns = 2
    cols = st.columns(num_columns)

    for i, name in enumerate(col_names):
        with cols[i % num_columns]:
            # Disable the input field if the player is not active and set its value to 0
            disabled = name not in active_player_names
            value = 0 if disabled else st.session_state.get(f'num{i}', 0)
            inputs.append(st.number_input(name, step=10, format='%d', key=f'num{i}', disabled=disabled, value=value))

    return inputs

def main_game():
    st.title('Simple Schafkopf App')

    col_names = st.session_state.get('player_names', [f'Number {i + 1}' for i in range(4)])

    # Determine active players for the current round
    round_counter = len(st.session_state['data'])  # Assuming each row in the DataFrame represents a round
    active_player_names = determine_players_to_play(round_counter)

    # Creating the input form with dynamic number of input fields
    player_inputs = create_input_form(col_names, active_player_names)

    if 'data' not in st.session_state:
        st.session_state['data'] = pd.DataFrame(columns=col_names)

    column1, column2, column3 = st.columns(3)

    with column1:
        if st.button('Submit'):
            # Call autofill function with only active player inputs
            player_inputs = calculate_auto_fill_values(player_inputs, active_player_names, col_names)
            # Update the values for active players based on autofill results

            # Check if all numbers are divisible by 10 and sum to zero
            all_divisible_by_10 = all(n % 10 == 0 for n in player_inputs)
            if sum(player_inputs) == 0 and all_divisible_by_10:
                # Create a new row with dynamic column names
                new_row = {col_names[i]: player_inputs[i] for i in range(len(col_names))}
                temp_df = add_row_to_df(st.session_state['data'], new_row)

                # Update the session state DataFrame
                st.session_state['data'] = temp_df
            else:
                st.error("The sum must be zero & numbers must be multiples of 10")

    with column3:
        if st.button('Remove Last Row'):
            if not st.session_state['data'].empty:
                st.session_state['data'] = st.session_state['data'].iloc[:-1]
                st.success("Last row removed successfully.")
            else:
                st.warning("The DataFrame is already empty.")
    with column2:
        # 'Next Round' button (currently does not perform any action)
        st.button('Next Round')

    # Display the DataFrame
    print_table(st.session_state['data'])

def main():
    page = st.sidebar.radio("Select Page", ["Player Registration", "Main Game"])

    if page == "Player Registration":
        register_players()
    elif page == "Main Game":
        main_game()

if __name__ == "__main__":
    main()
