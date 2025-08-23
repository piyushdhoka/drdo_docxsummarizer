import os
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2 or pypdf as fallback.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from all pages, or empty string if extraction fails
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found"
    
    # Check if file is a PDF
    if not file_path.lower().endswith('.pdf'):
        return f"Error: File '{file_path}' is not a PDF"
    
    extracted_text = ""
    
    # Try PyPDF2 first
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text.strip()
                    extracted_text += "\n"
            
            if extracted_text.strip():
                return extracted_text.strip()
                
    except ImportError:
        # PyPDF2 not available, try pypdf
        pass
    except Exception as e:
        # PyPDF2 failed, try pypdf
        pass
    
    # Try pypdf as fallback
    try:
        import pypdf
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text.strip()
                    extracted_text += "\n"
            
            if extracted_text.strip():
                return extracted_text.strip()
                
    except ImportError:
        return "Error: Neither PyPDF2 nor pypdf is installed"
    except Exception as e:
        return f"Error: Failed to extract text from PDF: {str(e)}"
    
    # If we get here, no text was extracted
    return "Warning: No text could be extracted from the PDF. The file might be image-based or corrupted."

def get_pdf_info(file_path: str) -> Optional[dict]:
    """
    Get basic information about a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: PDF information including page count, file size, etc.
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        # Try PyPDF2 first
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return {
                    'page_count': len(pdf_reader.pages),
                    'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'extractor': 'PyPDF2'
                }
        except ImportError:
            pass
        
        # Try pypdf as fallback
        try:
            import pypdf
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                return {
                    'page_count': len(pdf_reader.pages),
                    'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'extractor': 'pypdf'
                }
        except ImportError:
            pass
            
    except Exception:
        pass
    
    return None
