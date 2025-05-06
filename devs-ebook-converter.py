import streamlit as st
import ebooklib
from ebooklib import epub, mobi, azw3  # Import the format modules
import os
import tempfile
from io import BytesIO

# Supported input and output formats
INPUT_FORMATS = ["epub", "mobi", "azw3"]  # Add more if supported by ebooklib
OUTPUT_FORMATS = ["epub", "mobi", "azw3"] # Add more

def convert_ebook(input_file, output_format, output_name):
    """
    Converts an ebook from one format to another.

    Args:
        input_file (BytesIO): The uploaded ebook file (in bytes).
        output_format (str): The desired output format (e.g., "epub", "mobi").
        output_name (str): The name for the output file.

    Returns:
        BytesIO: The converted ebook file as bytes, ready for download.  Returns None on Error
    """
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
            temp_input_file.write(input_file.read())
            input_file_path = temp_input_file.name # Get the name of the temp file

        # Determine the input format from the file extension
        input_format = os.path.splitext(input_file_path)[1][1:].lower() #remove the '.' and lower case

        if input_format not in INPUT_FORMATS:
            st.error(f"Error: Input format '{input_format}' not supported.  Supported formats: {', '.join(INPUT_FORMATS)}")
            return None

        # Create a new file path with the desired output format
        output_file_path = f"{output_name}.{output_format}"

        # Conversion logic using ebooklib
        if input_format == output_format:
            #st.warning("Input and output formats are the same. No conversion needed.")
            # Create a BytesIO object and write the input file content to it
            output_file_bytes = BytesIO(input_file.read())
            return output_file_bytes

        if input_format == "epub" and output_format == "mobi":
            book = epub.read_epub(input_file_path)
            mobi.write_mobi(book, output_file_path)
        elif input_format == "epub" and output_format == "azw3":
            book = epub.read_epub(input_file_path)
            azw3.write_azw3(book, output_file_path)
        elif input_format == "mobi" and output_format == "epub":
            book = mobi.read_mobi(input_file_path)
            epub.write_epub(output_file_path, book)
        elif input_format == "mobi" and output_format == "azw3":
            book = mobi.read_mobi(input_file_path)
            #mobi to azw3 conversion is not directly supported by ebooklib.
            st.error(f"Error: Conversion from Mobi to AZW3 is not supported.")
            return None
        elif input_format == "azw3" and output_format == "epub":
            book = azw3.read_azw3(input_file_path)
            epub.write_epub(output_file_path, book)
        elif input_format == "azw3" and output_format == "mobi":
             book = azw3.read_azw3(input_file_path)
             mobi.write_mobi(book, output_file_path)
        else:
            st.error(f"Conversion from {input_format} to {output_format} is not supported.")
            return None

        # Read the converted file into bytes
        with open(output_file_path, "rb") as converted_file:
            output_file_bytes = BytesIO(converted_file.read())

        # Clean up the temporary files (both input and output)
        os.remove(temp_input_file.name)
        os.remove(output_file_path)
        return output_file_bytes

    except Exception as e:
        st.error(f"An error occurred during conversion: {e}")
        return None

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Ebook Converter")
    st.markdown("Convert ebooks between different formats (e.g., epub, mobi, azw3).")

    # File upload
    uploaded_file = st.file_uploader("Upload an ebook file", type=INPUT_FORMATS)

    # Input validation: Check if a file has been uploaded
    if uploaded_file is None:
        st.info("Please upload an ebook file to begin the conversion.")
        return  # Stop execution if no file is uploaded

    # Output format selection
    output_format = st.selectbox("Select the output format", OUTPUT_FORMATS)

    # Output file name input
    output_name = st.text_input("Enter the output file name (without extension)", "converted_ebook")

    # Convert button
    if st.button("Convert"):
        # Input validation: Check if the output name is valid
        if not output_name:
            st.error("Please enter a valid output file name.")
            return

        # Perform the conversion
        with st.spinner(f"Converting to {output_format}..."):
            converted_file = convert_ebook(uploaded_file, output_format, output_name)

        # Download the converted file
        if converted_file:
            st.success(f"Successfully converted to {output_format}!")
            st.download_button(
                label=f"Download {output_name}.{output_format}",
                data=converted_file,
                file_name=f"{output_name}.{output_format}",
                mime=f"application/{output_format}",  # Set appropriate MIME type
            )
        else:
            st.error("Conversion failed.")

if __name__ == "__main__":
    main()
