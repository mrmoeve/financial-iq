from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {"pdf", "txt", "md"}


def extract_text_from_upload(uploaded_file) -> str:
    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    if extension == "pdf":
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
    else:
        text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

    cleaned = " ".join(text.split())
    if not cleaned:
        raise ValueError("No extractable text was found in the uploaded file.")
    return cleaned
