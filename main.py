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
            st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())

def edit_last_round():

    if not st.session_state.scores.empty:
        last_round = st.session_state.scores.iloc[-1]
        last_round_editable = last_round.copy()
        last_round_editable.name = "Bearbeitete Runde"

        # Erstelle Eingabefelder für die Bearbeitung der letzten Runde
        for name, score in last_round_editable.items():
            if name != "Spielart":
                last_round_editable[name] = st.number_input(f"{name} ({score})", value=score)

        if st.button("Runde bearbeiten und speichern"):
            # Aktualisiere die Spieler-Guthaben
            for name in last_round.index:
                if name != "Spielart":
                    st.session_state.player_balances[name] -= 10*last_round[name]
                    st.session_state.player_balances[name] += 10*last_round_editable[name]

            # Aktualisiere die letzte Runde in der Tabelle
            st.session_state.scores.iloc[-1] = last_round_editable

            st.success("Letzte Runde erfolgreich bearbeitet und gespeichert!")

            # Aktualisiere die Summe
            st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())

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
                round_scores[name] = tariff * (len(st.session_state.player_balances.keys()) - len(st.session_state.winners))

        # Füge die Spielart zur Runde hinzu
        round_scores['Spielart'] = st.session_state.game_type

        # Aktualisiere die Guthaben und füge die Rundenergebnisse zur Tabelle hinzu
        for name in st.session_state.player_balances.keys():
            st.session_state.player_balances[name] += round_scores[name]

        st.session_state.scores = pd.concat([st.session_state.scores, pd.DataFrame([round_scores])], ignore_index=True)


        # Zeige die aktualisierte Tabelle an
        st.write(st.session_state.scores)
        st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())

        #Quersumme pruefen
        total_balance = 0
        for name in st.session_state.player_balances.keys():
            total_balance += st.session_state.player_balances[name]
        if total_balance != 0:
            st.write("Es geht sich nicht mehr aus")
            st.write(total_balance)

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
