import streamlit as st

def register_players():
    st.title("Spielerregistrierung")

    # Spieleranzahl auswählen
    num_players = st.slider("Anzahl der Spieler (4-7)", 4, 7)

    # Liste für Spieler erstellen
    player_names = [st.text_input(f"Spieler {i + 1} Name", f"Spieler {i + 1}") for i in range(num_players)]

    # Button, um die Spieler zu registrieren
    if st.button("Spieler registrieren"):
        st.success("Spieler erfolgreich registriert!")

    return player_names

def record_rounds(player_names):
    st.title("Spielrunden Aufzeichnung")

    # Überprüfen, ob Spieler registriert wurden
    if not player_names[0]:
        st.warning("Bitte geben Sie zuerst die Spieler ein und klicken Sie dann auf 'Spieler registrieren'.")
        return

    # Runden aktualisieren
    if st.button("Runde abschließen"):
        player_balances = [0] * len(player_names)
        for i in range(len(player_names)):
            change = st.number_input(f"{player_names[i]} Veränderung", key=f"change_{i}", value=0, step=1)
            player_balances[i] += change

        # Anzeige der aktuellen Guthaben
        st.write("\nAktuelle Guthaben:")
        for i in range(len(player_names)):
            st.write(f"{player_names[i]}: {player_balances[i]}")

def main():
    page = st.sidebar.radio("Seiten", ["Spielerregistrierung", "Spielrunden Aufzeichnung"])
    player_names = ["eins","zwei","drei","vier"]
    if page == "Spielerregistrierung":
        player_names = register_players()
    elif page == "Spielrunden Aufzeichnung":
        #player_names = register_players()
        record_rounds(player_names)

if __name__ == "__main__":
    main()
