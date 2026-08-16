import streamlit as st
import io
import csv
import genanki
import tempfile

# Unique IDs for genanki
MODEL_ID = 1607392322
DECK_ID = 2059400113

my_model = genanki.Model(
    MODEL_ID,
    'Plain Text Model',
    fields=[{'name': 'Front'}, {'name': 'Back'}],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
    }]
)

st.set_page_config(page_title="Flashcard Converter", page_icon="📝")

st.title("📝 Noji & Anki Flashcard Converter")
st.write("Since **Noji** strips lines when importing `.apkg` files, please use the **CSV** option below for Noji.")

deck_name = st.text_input("Enter Deck Name:", value="Pathology Quiz Deck")

tsv_data = st.text_area(
    "Paste TSV Data here (with headers on the first line):", 
    height=300, 
    placeholder="Front\tBack\nQuestion 1\tAnswer 1"
)

if st.button("Process Flashcards"):
    if tsv_data.strip():
        try:
            # Parse the inputs
            reader = csv.reader(io.StringIO(tsv_data), delimiter='\t')
            header = next(reader, None)
            
            raw_cards = []
            for row in reader:
                if len(row) >= 2:
                    front, back = row[0], row[1]
                    
                    # Clean the HTML tags and format to clean plain text
                    front_clean = front.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
                    back_clean = back.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
                    
                    raw_cards.append((front_clean, back_clean))
            
            if len(raw_cards) > 0:
                st.success(f"Successfully processed {len(raw_cards)} cards!")
                
                # --- OPTION 1: GENERATE NOJI COMPATIBLE CSV ---
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["Front", "Back"]) # Header
                for front, back in raw_cards:
                    csv_writer.writerow([front, back])
                
                # --- OPTION 2: GENERATE APKG ---
                deck = genanki.Deck(DECK_ID, deck_name)
                for front, back in raw_cards:
                    note = genanki.Note(model=my_model, fields=[front, back])
                    deck.add_note(note)
                
                package = genanki.Package(deck)
                with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as tmp:
                    package.write_to_file(tmp.name)
                    with open(tmp.name, "rb") as f:
                        apkg_data = f.read()

                # Display two clear download choices
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download CSV (Use this for Noji)",
                        data=csv_buffer.getvalue(),
                        file_name=f"{deck_name.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    st.download_button(
                        label="📦 Download APKG (Standard Anki)",
                        data=apkg_data,
                        file_name=f"{deck_name.replace(' ', '_')}.apkg",
                        mime="application/octet-stream"
                    )
            else:
                st.error("No valid card rows were parsed. Make sure you used tabs to separate columns.")
        except Exception as e:
            st.error(f"Error parsing data: {e}")
    else:
        st.warning("Please paste your TSV data first.")
