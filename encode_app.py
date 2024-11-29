import streamlit as st
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from io import BytesIO

# Generate and store encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

def embed_message(image, message):
    """Embeds a binary message into an image using LSB steganography."""
    img = np.array(image)
    binary_message = ''.join(format(byte, '08b') for byte in message) + '1111111111111110'  # End marker
    msg_len = len(binary_message)
    
    flat_img = img.flatten()
    for i in range(msg_len):
        flat_img[i] = (flat_img[i] & 254) | int(binary_message[i])  # Modify LSB
    embedded_img = flat_img.reshape(img.shape)
    return Image.fromarray(embedded_img.astype('uint8'))


def extract_message(image):
    """Extracts a hidden binary message from an image using LSB steganography."""
    img = np.array(image).flatten()
    binary_message = ""
    for pixel in img:
        binary_message += str(pixel & 1)
        if binary_message[-16:] == "1111111111111110":  # End marker
            break
    byte_array = bytearray(
        int(binary_message[i:i + 8], 2) for i in range(0, len(binary_message) - 16, 8)
    )
    return bytes(byte_array)  # Return as bytes


# Streamlit UI
st.title("LSB-Based Message Hiding and Extraction")

tab1, tab2 = st.tabs(["Hide Message", "Extract Message"])


if "encryption_key" not in st.session_state:
    st.session_state.encryption_key = Fernet.generate_key()
cipher = Fernet(st.session_state.encryption_key)

with tab1:
    st.header("Hide a Message in an Image")
    uploaded_file = st.file_uploader("Upload an image file (BMP or PNG)", type=["bmp", "png"])
    message = st.text_input("Enter the message you want to hide:")
    if uploaded_file and message:
      image = Image.open(uploaded_file)
      encrypted_message = cipher.encrypt(message.encode())  # Do not decode to string
      embedded_image = embed_message(image, encrypted_message)
      st.image(embedded_image, caption="Message embedded in the image.", use_column_width=True)

    # Save the embedded image to memory
      img_byte_arr = BytesIO()
      embedded_image.save(img_byte_arr, format="PNG")
      img_byte_arr = img_byte_arr.getvalue()

    # Provide download button
      st.download_button(
         label="Download Embedded Image",
         data=img_byte_arr,
         file_name="embedded_image.png",
         mime="image/png"
      )




# Extract Message
with tab2:
    st.header("Extract a Hidden Message from an Image")
    uploaded_embedded_file = st.file_uploader("Upload an embedded image file (BMP or PNG)", type=["bmp", "png"])
    if uploaded_embedded_file:
        try:
            embedded_image = Image.open(uploaded_embedded_file)
            extracted_message = extract_message(embedded_image)
            st.write(f"Extracted Encrypted Message (binary): {extracted_message}")

        # Decrypt the binary message
            decrypted_message = cipher.decrypt(extracted_message).decode()
            st.success(f"Hidden Message: {decrypted_message}")
        except Exception as e:
            st.error(f"Unable to decrypt the message. Please ensure the correct image is uploaded. Error: {e}")

