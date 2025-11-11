
import streamlit as st
import tempfile
import os
import time
import cv2
import numpy as np
from azure.storage.blob import BlobServiceClient

# ---------------------------
# Azure Configuration (edit these)
# ---------------------------
AZURE_STORAGE_CONNECTION_STRING = "YOUR_AZURE_STORAGE_CONNECTION_STRING"
AZURE_CONTAINER_NAME = "videos"

# Initialize Azure Blob client
def upload_to_blob(local_path, blob_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        return f"https://<your_storage_account>.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_name}"
    except Exception as e:
        st.error(f"Azure upload failed: {e}")
        return None

# ---------------------------
# Video Enhancement Placeholder
# ---------------------------
def enhance_video(input_path, output_path):
    # TODO: Replace with your real AI model logic from the notebook
    st.info("Enhancing video using AI model... (placeholder)")
    time.sleep(3)  # Simulate processing time
    # For demo, just copy the input to output
    import shutil
    shutil.copy(input_path, output_path)
    return output_path

# ---------------------------
# PSNR & SSIM Calculation
# ---------------------------
def calculate_psnr_ssim(original, enhanced):
    import skimage.metrics as metrics
    try:
        frame1 = cv2.resize(original, (256, 256))
        frame2 = cv2.resize(enhanced, (256, 256))
        psnr = metrics.peak_signal_noise_ratio(frame1, frame2)
        ssim = metrics.structural_similarity(frame1, frame2, multichannel=True)
        return psnr, ssim
    except Exception as e:
        return None, None

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="AI Video Enhancement", layout="wide")
st.title("🎥 AI-Based Video Enhancement System")

uploaded_file = st.file_uploader("Upload a video (MP4 format)", type=["mp4"])

if uploaded_file:
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_input.write(uploaded_file.read())
    temp_input.close()

    st.video(temp_input.name, format="video/mp4")
    st.write("### Original Video Preview")

    if st.button("🚀 Enhance Video"):
        with st.spinner("Enhancing video... please wait ⏳"):
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            enhanced_path = enhance_video(temp_input.name, temp_output.name)

            # Display both videos
            col1, col2 = st.columns(2)
            with col1:
                st.write("#### Original Video")
                st.video(temp_input.name)
            with col2:
                st.write("#### Enhanced Video")
                st.video(enhanced_path)

            # Extract sample frames for PSNR/SSIM
            cap1 = cv2.VideoCapture(temp_input.name)
            cap2 = cv2.VideoCapture(enhanced_path)
            success1, frame1 = cap1.read()
            success2, frame2 = cap2.read()
            if success1 and success2:
                psnr, ssim = calculate_psnr_ssim(frame1, frame2)
                if psnr and ssim:
                    st.success(f"✅ PSNR: {psnr:.2f}, SSIM: {ssim:.3f}")
                else:
                    st.warning("Could not calculate PSNR/SSIM")
            cap1.release()
            cap2.release()

            # Upload to Azure
            st.write("Uploading enhanced video to Azure...")
            blob_url = upload_to_blob(enhanced_path, os.path.basename(enhanced_path))
            if blob_url:
                st.success(f"✅ Uploaded to Azure: [View Enhanced Video]({blob_url})")

            st.download_button("⬇️ Download Enhanced Video", open(enhanced_path, "rb"), "enhanced.mp4")

st.markdown("---")
st.caption("Developed by Pramod | AI-Based Video Enhancement Project")
