import os
from typing import List
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF


class PDFLoader:
    """A class to load and extract text from PDF files using multiple methods."""
    
    def __init__(self, path: str, method: str = "pdfplumber"):
        """
        Initialize PDF loader.
        
        Args:
            path: Path to PDF file or directory containing PDF files
            method: Method to use for PDF extraction ("pdfplumber", "pymupdf", "pypdf2")
        """
        self.documents = []
        self.path = path
        self.method = method
        self.supported_methods = ["pdfplumber", "pymupdf", "pypdf2"]
        
        if method not in self.supported_methods:
            raise ValueError(f"Method must be one of {self.supported_methods}")

    def load(self):
        """Load PDF files from path."""
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.lower().endswith(".pdf"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .pdf file."
            )

    def load_file(self):
        """Load a single PDF file."""
        try:
            text = self._extract_text(self.path)
            if text.strip():  # Only add non-empty text
                self.documents.append(text)
        except Exception as e:
            print(f"Error loading PDF {self.path}: {e}")

    def load_directory(self):
        """Load all PDF files from a directory."""
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    try:
                        text = self._extract_text(file_path)
                        if text.strip():  # Only add non-empty text
                            self.documents.append(text)
                    except Exception as e:
                        print(f"Error loading PDF {file_path}: {e}")

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using the specified method."""
        if self.method == "pdfplumber":
            return self._extract_with_pdfplumber(file_path)
        elif self.method == "pymupdf":
            return self._extract_with_pymupdf(file_path)
        elif self.method == "pypdf2":
            return self._extract_with_pypdf2(file_path)

    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (best for tables and layout)."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_with_pymupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF (fastest and most reliable)."""
        text = ""
        doc = fitz.open(file_path)
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text() + "\n"
        doc.close()
        return text

    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2 (basic extraction)."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text

    def load_documents(self):
        """Load documents and return them."""
        self.load()
        return self.documents


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path):
            if self.path.lower().endswith(".txt"):
                self.load_file()
            elif self.path.lower().endswith(".pdf"):
                # Use PDFLoader for PDF files
                pdf_loader = PDFLoader(self.path)
                self.documents = pdf_loader.load_documents()
            else:
                raise ValueError(
                    "File must be either .txt or .pdf format."
                )
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a supported file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())
                elif file.lower().endswith(".pdf"):
                    # Use PDFLoader for PDF files
                    file_path = os.path.join(root, file)
                    pdf_loader = PDFLoader(file_path)
                    pdf_docs = pdf_loader.load_documents()
                    self.documents.extend(pdf_docs)

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


if __name__ == "__main__":
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
