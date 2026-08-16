import streamlit as st
import genanki
import io
import csv
import tempfile

# Unique IDs for Noji import stability
MODEL_ID = 1607392321
DECK_ID = 2059400112

# Plain text model structure (Noji does not require HTML/CSS styling)
my_model = genanki.Model(
    MODEL_ID,
    'Noji Plain Text Model',
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
    ]
)

st.set_page_config(page_title="Noji APKG Converter", page_icon="📝")

st.title("📝 Noji-Compatible APKG Converter")
st.write("This version automatically replaces HTML formatting with plain-text line breaks to look clean in **Noji**.")

deck_name = st.text_input("Enter your desired Deck Name:", value="Pathology Quiz Deck")

tsv_data = st.text_area(
    "Paste TSV Data here (with headers like 'Front' and 'Back' on the first line):", 
    height=350, 
    placeholder="Front\tBack\nQuestion 1\tAnswer 1"
)

if st.button("Generate Noji Package"):
    if tsv_data.strip():
        try:
            deck = genanki.Deck(DECK_ID, deck_name)
            
            # Read and parse text from the text area
            reader = csv.reader(io.StringIO(tsv_data), delimiter='\t')
            
            # Skip the first row (the header)
            header = next(reader, None)
            
            card_count = 0
            for row in reader:
                if len(row) >= 2:
                    front, back = row[0], row[1]
                    
                    # Clean up HTML tags and replace them with plain-text newlines for Noji
                    front_clean = front.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
                    back_clean = back.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
                    
                    # Create Note
                    note = genanki.Note(model=my_model, fields=[front_clean, back_clean])
                    deck.add_note(note)
                    card_count += 1
            
            if card_count > 0:
                package = genanki.Package(deck)
                with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as tmp:
                    package.write_to_file(tmp.name)
                    with open(tmp.name, "rb") as f:
                        apkg_data = f.read()
                
                st.success(f"Successfully compiled {card_count} Noji-compatible flashcards!")
                
                st.download_button(
                    label="📥 Download Noji .apkg File",
                    data=apkg_data,
                    file_name=f"{deck_name.replace(' ', '_')}_noji.apkg",
                    mime="application/octet-stream"
                )
            else:
                st.error("No valid card rows were parsed. Make sure you used tabs to separate columns.")
        except Exception as e:
            st.error(f"An unexpected parsing error occurred: {e}")
    else:
        st.warning("The input field is empty. Please paste your TSV data first.")
