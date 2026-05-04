import os
import uuid


def save_uploaded_file(uploaded_file, upload_dir):
    """
    Save uploaded file safely with unique name
    """

    ext = uploaded_file.name.split(".")[-1]

    filename = f"{uuid.uuid4()}.{ext}"

    filepath = os.path.join(
        upload_dir,
        filename
    )

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return filepath