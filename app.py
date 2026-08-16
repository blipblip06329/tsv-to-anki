import streamlit as st
import genanki
import io
import csv
import tempfile

# Unique IDs for the Anki Note Model and Deck
# If you make your own decks later, keeping these stable prevents duplication.
MODEL_ID = 1607392320
DECK_ID = 2059400111

# Define the Anki card layout and styles
my_model = genanki.Model(
    MODEL_ID,
    'Pathology Quiz Model',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
        },
    ],
    css='''
    .card {
        font-family: Arial, sans-serif;
        font-size: 18px;
        text-align: left;
        color: #2c3e50;
        background-color: #ffffff;
        padding: 25px;
        line-height: 1.5;
    }
    b {
        color: #16a085;
    }
    '''
)

st.set_page_config(page_title="Anki APKG Converter", page_icon="📝")

st.title("📝 TSV to Anki APKG Converter")
st.write("Convert your Tab-Separated Values (TSV) directly into an Anki-compatible `.apkg` file.")

# Let the user set custom details
deck_name = st.text_input("Enter your desired Deck Name:", value="Pathology Quiz Deck")

# Main text input field
tsv_data = st.text_area(
    "Paste TSV Data here (with headers like 'Front' and 'Back' on the first line):", 
    height=350, 
    placeholder="Front\tBack\nQuestion 1\tAnswer 1"
)

if st.button("Generate Anki Package"):
    if tsv_data.strip():
        try:
            deck = genanki.Deck(DECK_ID, deck_name)
            
            # Read and parse text from the text area
            reader = csv.reader(io.StringIO(tsv_data), delimiter='\t')
            
            # Skip the first row (the header)
            header = next(reader, None)
            
            card_count = 0
            for row in reader:
                # Ensure the row actually has a front and a back
                if len(row) >= 2:
                    front, back = row[0], row[1]
                    # Create Note
                    note = genanki.Note(model=my_model, fields=[front, back])
                    deck.add_note(note)
                    card_count += 1
            
            if card_count > 0:
                package = genanki.Package(deck)
                
                # Write file temporarily on Streamlit's container
                with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as tmp:
                    package.write_to_file(tmp.name)
                    with open(tmp.name, "rb") as f:
                        apkg_data = f.read()
                
                st.success(f"Successfully compiled {card_count} flashcards!")
                
                # Download button
                st.download_button(
                    label="📥 Download .apkg File",
                    data=apkg_data,
                    file_name=f"{deck_name.replace(' ', '_')}.apkg",
                    mime="application/octet-stream"
                )
            else:
                st.error("No valid card rows were parsed. Make sure you used tabs to separate columns.")
        except Exception as e:
            st.error(f"An unexpected parsing error occurred: {e}")
    else:
        st.warning("The input field is empty. Please paste your TSV data first.")
