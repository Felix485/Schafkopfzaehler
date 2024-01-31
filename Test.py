import pandas as pd
import base64

def encode_dataframe(df):
    # Ensure player names are in the columns
    player_names = df.columns.tolist()
    # Join player names with a delimiter
    player_names_str = ','.join(player_names)
    
    # Flatten DataFrame values and convert to string
    values = df.values.flatten()
    values_str = ','.join(map(str, values))
    
    # Concatenate player names and values, separated by a unique delimiter
    encoded_str = player_names_str + ';' + values_str
    
    # Encode the combined string with base64
    b64_encoded = base64.b64encode(encoded_str.encode('utf-8')).decode('utf-8')
    return b64_encoded

def decode_to_dataframe(encoded_str):
    # Decode the base64 string
    decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
    decoded_str = decoded_bytes.decode('utf-8')
    
    # Split the decoded string to extract player names and values
    player_names_str, values_str = decoded_str.split(';')
    player_names = player_names_str.split(',')
    values = list(map(int, values_str.split(',')))
    
    # Reshape the values to match the DataFrame structure and create the DataFrame
    num_players = len(player_names)
    num_rows = len(values) // num_players
    df = pd.DataFrame(data=reshape(values, (num_rows, num_players)), columns=player_names)
    return df

def reshape(lst, shape):
    return [lst[i:i + shape[1]] for i in range(0, len(lst), shape[1])]

# Example Usage
df = pd.DataFrame({
    'Alice': [10, 20, 30],
    'Bob': [40, 50, 60]
})

encoded_str = encode_dataframe(df)
print(f'Encoded String: {encoded_str}')

decoded_df = decode_to_dataframe(encoded_str)
print(decoded_df)
