import streamlit as st
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from PIL import Image
import requests
import io
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Streamlit app
st.title("Image Extension with Cloudinary's Gen Fill")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Generate a unique filename to avoid caching issues
    unique_filename = f"temp_image_{uuid.uuid4().hex}.jpg"

    # Save uploaded file temporarily
    with open(unique_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display uploaded image
    st.image(unique_filename, caption="Uploaded Image", use_column_width=True)

    # Select aspect ratio
    aspect_ratio = st.selectbox(
        "Select Aspect Ratio",
        options=["1:1", "4:3", "16:9"],
        index=0
    )

    # Select gravity
    gravity = st.selectbox(
        "Select Gravity",
        options=["center", "north", "south", "east", "west"],
        index=0
    )

    # Select extension size
    size = st.slider("Select Extension Size (in pixels)", 100, 1000, 500)

    # Generate button
    if st.button("Extend Image"):
        # Upload the image to Cloudinary with a unique public ID
        public_id = f"genfill-image-{uuid.uuid4().hex}"
        upload_result = cloudinary.uploader.upload(unique_filename, public_id=public_id)

        # Generate the extended image URL
        extended_image_url, _ = cloudinary_url(
            public_id,
            aspect_ratio=aspect_ratio,
            gravity=gravity,
            background="gen_fill",
            crop="pad",
            width=size
        )

        # Load images
        original_image = Image.open(unique_filename)

        # Fetch the extended image from the generated URL
        response = requests.get(extended_image_url)
        extended_image = Image.open(io.BytesIO(response.content))

        # Display images
        st.subheader("Compare Images")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(original_image, caption="Original Image", use_column_width=True)

        with col2:
            st.image(extended_image, caption="Extended Image", use_column_width=True)

    # Clean up the temporary file
    os.remove(unique_filename)
