import streamlit as st
import pandas as pd

def init():
    # Initialize the round counter
    if 'round_counter' not in st.session_state:
        st.session_state.round_counter = 0  # Start with round 1

    # Initialisiere die Datenstrukturen im session_state, falls noch nicht vorhanden
    if 'scores' not in st.session_state:
        st.session_state.scores = pd.DataFrame()
    if 'player_balances' not in st.session_state:
        st.session_state.player_balances = {}
    if 'game_type' not in st.session_state:
        st.session_state.game_type = ''
    if 'winners' not in st.session_state:
        st.session_state.winners = []

# Function to update session state
def update_session_state(key, value):
    st.session_state[key] = value
    # Store the updated session state in the browser storage
    session_browser_storage.setItem(key, value)

init()

def determine_players_to_play(round_counter):
    num_players = len(st.session_state.player_balances)

    if num_players == 4:
        # All 4 players play all the time
        active_players = st.session_state.active_players if 'active_players' in st.session_state else list(
            st.session_state.player_balances.keys())
        return active_players[:4]

    elif num_players == 5:
        # One player sits out each round in order (a, b, c, d, e, a, b, ...)
        sit_out_player_index = (round_counter)% num_players
        active_players = st.session_state.active_players if 'active_players' in st.session_state else list(
            st.session_state.player_balances.keys())

        # Determine the player to sit out in this round
        sit_out_player = active_players[sit_out_player_index]

        # Determine the players who will play in the current round
        players_to_play = [player for player in active_players if player != sit_out_player]

        return players_to_play

    elif num_players == 6:
        # One player sits out each round in order (a, b, c, d, e, f, a, b, ...)
        sit_out_player_index = round_counter % num_players
        sit_out_player_index2 = (round_counter + 3) % num_players
        active_players = st.session_state.active_players if 'active_players' in st.session_state else list(
            st.session_state.player_balances.keys())

        # Determine the player to sit out in this round
        sit_out_player = active_players[sit_out_player_index]
        sit_out_player2 = active_players[sit_out_player_index2]

        # Determine the players who will play in the current round
        players_to_play = [player for player in active_players if player != sit_out_player and player != sit_out_player2]

        return players_to_play

    elif num_players == 7:
        # One player sits out each round in order (a, b, c, d, e, f, a, b, ...)
        sit_out_player_index = round_counter % num_players
        sit_out_player_index2 = (round_counter + 3) % num_players
        sit_out_player_index3 = (round_counter + 4) % num_players
        active_players = st.session_state.active_players if 'active_players' in st.session_state else list(
            st.session_state.player_balances.keys())

        # Determine the player to sit out in this round
        sit_out_player = active_players[sit_out_player_index]
        sit_out_player2 = active_players[sit_out_player_index2]
        sit_out_player3 = active_players[sit_out_player_index3]

        # Determine the players who will play in the current round
        players_to_play = [player for player in active_players if player != sit_out_player and player != sit_out_player2 and player != sit_out_player3]

        return players_to_play

def print_table():
    # Berechne die Summe und füge sie als letzte Zeile hinzu
    sum_row = st.session_state.scores.drop(columns='Spielart').sum().to_dict()
    sum_row['Spielart'] = 'Summe'
    sum_df = pd.DataFrame([sum_row])
    combined_table = pd.concat([st.session_state.scores, sum_df], ignore_index=True)

    # Zeige die kombinierte Tabelle an mit farblich hervorgehobener letzter Zeile
    st.write(combined_table.style.apply(
        lambda x: ['background-color: darkgray' if x.name == len(combined_table) - 1 else '' for _ in x], axis=1))

    # Quersumme pruefen
    total_balance = 0
    for name in st.session_state.player_balances.keys():
        total_balance += st.session_state.player_balances[name]
    if total_balance != 0:
        st.write("Es geht sich nicht mehr aus: ", total_balance)

def register_players():
    st.title("Spielerregistrierung")
    num_players = st.number_input("Anzahl der Spieler (4-7)", min_value=4, max_value=7, value=4, step=1)
    player_names = [st.text_input(f"Spieler {i + 1} Name", key=f'player_{i}') for i in range(num_players)]

    if st.button("Spieler registrieren"):
        st.session_state.player_balances = {name: 0 for name in player_names if name}
        st.session_state.scores = pd.DataFrame(columns=player_names + ['Spielart'])
        st.success("Spieler erfolgreich registriert!")

def remove_last_round():
    if not st.session_state.scores.empty:
        if st.button("Letzte Runde löschen"):
            last_round_scores = st.session_state.scores.iloc[-1].drop("Spielart")
            for name, score in last_round_scores.items():
                st.session_state.player_balances[name] -= score
            st.session_state.scores = st.session_state.scores.iloc[:-1]
            st.session_state.round_counter -= 1
            st.success("Letzte Runde erfolgreich gelöscht!")

            # Aktualisiere die Summe
            print_table()

    #bugfixing
    st.write(st.session_state.scores)
    st.write(st.session_state.player_balances)

def edit_last_round():
    if not st.session_state.scores.empty:
        last_round_index = st.session_state.scores.index[-1]  # Get the actual index of the last row
        last_round = st.session_state.scores.loc[last_round_index]
        last_round_editable = last_round.copy()
        last_round_editable.name = "Bearbeitete Runde"

        # Determine the number of columns needed (one for each score plus one for the button)
        num_cols = sum(name != "Spielart" for name in last_round_editable.index)

        # Create columns for the input fields
        cols = st.columns(num_cols)

        i = 0  # Initialize a counter for the columns
        for name, score in last_round_editable.items():
            if name != "Spielart":
                with cols[i]:
                    last_round_editable[name] = st.number_input(f"{name} ({score})", value=score, key=name, step = 10)
                i += 1  # Move to the next column

        if st.button("Runde bearbeiten und speichern"):
            # Aktualisiere die Spieler-Guthaben
            for name in last_round.index:
                if name != "Spielart":
                    st.session_state.player_balances[name] -= last_round[name]
                    st.session_state.player_balances[name] += last_round_editable[name]

            # Aktualisiere die letzte Runde in der Tabelle
            print_table()

            st.success("Letzte Runde erfolgreich bearbeitet und gespeichert!")

        # Button zum Ändern der Punkte der letzten Runde
        if st.button("Gewinner hat verloren"):
            # Ändere das Vorzeichen der Punkte der letzten Runde
            for name in last_round.index:
                if name != "Spielart":
                    st.session_state.scores.at[last_round_index, name] *= -1
                    st.session_state.player_balances[name] -= 2 * last_round[name]

            st.success("Punkte der letzten Runde erfolgreich geändert!")

            # Aktualisiere die Summe
            print_table()

def record_rounds():
    st.title("Spielrunden Aufzeichnung")

    # Determine the players who will play in the next round
    players_to_play = determine_players_to_play(st.session_state.round_counter)

    # Display the list of players who will play in the next round
    st.write(f"Ihr spielt jetzt: {', '.join(players_to_play)}")

    # Tarife für verschiedene Spiele festlegen
    game_tariffs = {
        "Sauspiel": 10,
        "Farbwenz": 30,
        "Wenz": 60,
        "Geier": 30,
        "Solo": 60,
        "Ramsch": 20
    }

    # Dropdown-Menü für die Auswahl des Spiels
    game_options = list(game_tariffs.keys())
    game_index = game_options.index(st.session_state.game_type) if st.session_state.game_type in game_options else 0
    st.session_state.game_type = st.selectbox("Spielart wählen", options=game_options, index=game_index)

    # Auswahl des/der Gewinner basierend auf Spielart
    max_winners = 2 if st.session_state.game_type == "Sauspiel" else 1
    st.session_state.winners = st.multiselect("Gewinner auswählen", options=st.session_state.player_balances.keys(), default=st.session_state.winners, max_selections=max_winners)

    # Runden aktualisieren
    if st.button("Runde eintragen"):
        st.session_state.round_counter += 1

        tariff = game_tariffs[st.session_state.game_type]
        round_scores = {name: -tariff for name in players_to_play}
        for name in st.session_state.player_balances.keys():
            round_scores[name] = 0
        for name in players_to_play:
            round_scores[name] = -tariff
        if st.session_state.game_type == "Ramsch":
            for name in round_scores:
                round_scores[name] = 20
            for name in st.session_state.winners:
                round_scores[name] = -60
        elif st.session_state.game_type == "Sauspiel":
            for name in st.session_state.winners:
                round_scores[name] = tariff
        else:
            for name in st.session_state.winners:
                round_scores[name] = tariff * (4 - len(st.session_state.winners))

        # Füge die Spielart zur Runde hinzu
        round_scores['Spielart'] = st.session_state.game_type

        # Aktualisiere die Guthaben und füge die Rundenergebnisse zur Tabelle hinzu
        for name in st.session_state.player_balances.keys():
            st.session_state.player_balances[name] += round_scores[name]

        st.session_state.scores = pd.concat([st.session_state.scores, pd.DataFrame([round_scores])], ignore_index=True)

        print_table()

        # Setze die Spielart und Gewinner zurück
        st.session_state.game_type = ''
        st.session_state.winners = []

        st.button("NÄCHSTE RUNDE!")

def main():

    page = st.sidebar.radio("Seite auswählen", ["Spielerregistrierung", "Spielrunden Aufzeichnung"])

    if page == "Spielerregistrierung":
        register_players()
    elif page == "Spielrunden Aufzeichnung":
        record_rounds()
        remove_last_round()
        edit_last_round()

if __name__ == "__main__":
    main()
