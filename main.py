import streamlit as st
import pandas as pd

# Initialisiere die Datenstrukturen im session_state, falls noch nicht vorhanden
if 'scores' not in st.session_state:
    st.session_state.scores = pd.DataFrame()
if 'player_balances' not in st.session_state:
    st.session_state.player_balances = {}
if 'game_type' not in st.session_state:
    st.session_state.game_type = ''
if 'winners' not in st.session_state:
    st.session_state.winners = []

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

            st.success("Letzte Runde erfolgreich gelöscht!")

            # Aktualisiere die Summe
            st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())

def edit_last_round():
    st.title("Letzte Runde bearbeiten")

    if not st.session_state.scores.empty:
        last_round = st.session_state.scores.iloc[-1]
        last_round_editable = last_round.copy()
        last_round_editable.name = "Bearbeitete Runde"

        # Erstelle Eingabefelder für die Bearbeitung der letzten Runde
        for name, score in last_round_editable.iteritems():
            if name != "Spielart":
                last_round_editable[name] = st.number_input(f"{name} ({score})", value=score)

        if st.button("Runde bearbeiten und speichern"):
            # Aktualisiere die Spieler-Guthaben
            for name in last_round.index:
                if name != "Spielart":
                    st.session_state.player_balances[name] -= last_round[name]
                    st.session_state.player_balances[name] += last_round_editable[name]

            # Aktualisiere die letzte Runde in der Tabelle
            st.session_state.scores.iloc[-1] = last_round_editable

            st.success("Letzte Runde erfolgreich bearbeitet und gespeichert!")

            # Aktualisiere die Summe
            st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())


def record_rounds():
    st.title("Spielrunden Aufzeichnung")

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
    if st.button("Runde abschließen"):
        tariff = game_tariffs[st.session_state.game_type]
        round_scores = {name: -tariff for name in st.session_state.player_balances.keys()}
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
        st.session_state.scores = st.session_state.scores.append(round_scores, ignore_index=True)

        # Zeige die aktualisierte Tabelle an
        st.write(st.session_state.scores)
        st.write("Summe:", st.session_state.scores.drop(columns='Spielart').sum())

        # Setze die Spielart und Gewinner zurück
        st.session_state.game_type = ''
        st.session_state.winners = []

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