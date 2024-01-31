import streamlit as st
import pandas as pd
import base64
from io import StringIO

def reshape(lst, shape):
    # Reshape the list into a list of lists with the given shape
    return [lst[i:i + shape[1]] for i in range(0, len(lst), shape[1])]

def encode_dataframe(df):
    # Convert DataFrame to CSV string
    csv_str = df.to_csv(index=False)
    # Encode the CSV string with base64
    b64_encoded = base64.urlsafe_b64encode(csv_str.encode()).decode()
    return b64_encoded



def decode_to_dataframe(encoded_str):
    padding = 4 - (len(encoded_str) % 4)
    encoded_str += "=" * padding

    try:
        # Decode the base64 string
        decoded_bytes = base64.urlsafe_b64decode(encoded_str)
        #st.write("Decoded bytes:", decoded_bytes)  # DEBUG: Print the decoded bytes
        
        # Convert CSV string to DataFrame
        csv_str = decoded_bytes.decode()
        #st.write("CSV string:", csv_str)  # DEBUG: Print the CSV string before converting to DataFrame
        
        df = pd.read_csv(StringIO(csv_str))
        return df
    except Exception as e:
        # Handle exceptions (like incorrect padding or other decoding issues)
        print(f"Error decoding data: {e}")
        return pd.DataFrame()



def write_to_url(df):
    # Store the encoded DataFrame in the URL
    encoded_str = encode_dataframe(df)
    #st.write("writing:",encoded_str) #DEBUG
    st.query_params['data'] = encoded_str
    # Rerun the app to reflect changes in the URL
    # st.experimental_rerun()

def read_and_decode_from_url():
    # Retrieve the encoded DataFrame from the URL
    query_params = st.query_params.to_dict()
    encoded_str = query_params.get('data', [''])
    if encoded_str:
        # Decode the DataFrame
        #st.write("reading raw:",encoded_str) # DEBUG
        decoded_df = decode_to_dataframe(encoded_str)
        #st.write(decoded_df)
        return decoded_df
    else:
        # Return an empty DataFrame if there's no data in the URL
        st.write("Error in read_and_decode_from_URL: else case")
        return pd.DataFrame()


def print_table(df):    
    # Calculate the sum and append it as the last row
    # Adjust column names based on your DataFrame's structure
    decoded_string = read_and_decode_from_url()
    #st.write("reading:",decoded_string) # DEBUG
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
            # Disable the input field if the player is not active
            disabled = name not in active_player_names
            # Initialize all input fields with a default value of 0
            value = 0 if disabled else st.session_state.get(f'num{i}', 0)
            inputs.append(st.number_input(name, step=10, format='%d', key=f'num{i}', disabled=disabled, value=value))

    return inputs



def main_game():
    st.title('Simple Schafkopf App')

    # Load player names and DataFrame from URL at the start
    player_names, df = read_and_decode_from_url()

    if not player_names:
        # Fallback if player names are not in URL
        player_names = [f'Number {i + 1}' for i in range(4)]

    if df.empty:
        # Initialize an empty DataFrame with player names as columns if no data is present
        df = pd.DataFrame(columns=player_names)

    # Check if reset flag is set and reset input values if needed
    if st.session_state.get('reset_inputs', False):
        for i in range(len(player_names)):
            st.session_state[f'num{i}'] = 0
        st.session_state['reset_inputs'] = False

     # Determine active players for the current round
    round_counter = len(df)
    active_player_names = determine_players_to_play(round_counter, player_names)

    # Creating the input form with dynamic number of input fields
    player_inputs = create_input_form(player_names, active_player_names)

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
                new_row = {player_names[i]: player_inputs[i] for i in range(len(player_names))}
                df = add_row_to_df(df, new_row)

                # Write updated DataFrame to URL
                write_to_url(df)
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
        if st.button('Reset Fields'):
            # Set the reset flag
            st.session_state['reset_inputs'] = True
            # Rerun the script to reflect the reset state
            st.experimental_rerun()

    # Display the DataFrame
    print_table(df)

def main():
    page = st.sidebar.radio("Select Page", ["Player Registration", "Main Game"])

    if page == "Player Registration":
        register_players()
    elif page == "Main Game":
        main_game()

if __name__ == "__main__":
    main()
