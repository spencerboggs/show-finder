"""
OCR module to extract text from post images.
"""
import pytesseract
from PIL import Image
from typing import Optional, Dict
import os


class OCRExtractor:
    """Extracts text from images using OCR."""
    
    def __init__(self):
        # Try to find tesseract executable (common Windows paths)
        # User may need to set this manually if tesseract is installed elsewhere
        self.tesseract_available = False
        try:
            # Common Windows installation path
            if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                self.tesseract_available = True
            elif os.path.exists(r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'):
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                self.tesseract_available = True
            else:
                # Try to use tesseract from PATH
                try:
                    pytesseract.get_tesseract_version()
                    self.tesseract_available = True
                except:
                    self.tesseract_available = False
        except:
            self.tesseract_available = False
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not self.tesseract_available:
            return None
        
        if not image_path or not os.path.exists(image_path):
            return None
        
        try:
            image = Image.open(image_path)
            
            # Preprocess image for better OCR results
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(image)
            
            return text.strip() if text else None
            
        except Exception as e:
            print(f"Error extracting text from image {image_path}: {e}")
            return None
    
    def extract_show_info_from_image(self, image_path: str, post_timestamp) -> Dict[str, Optional[str]]:
        """
        Extract show information from image text.
        
        Args:
            image_path: Path to the image file
            post_timestamp: When the post was made (for date context)
            
        Returns:
            Dictionary with extracted date, location, and time
        """
        from text_parser import ShowTextParser
        
        info = {
            'date': None,
            'location': None,
            'time': None
        }
        
        extracted_text = self.extract_text_from_image(image_path)
        
        if not extracted_text:
            return info
        
        # Use the text parser to extract info from OCR text
        parser = ShowTextParser()
        
        parsed_date = parser.extract_date(extracted_text, post_timestamp)
        if parsed_date:
            info['date'] = parsed_date.strftime('%Y-%m-%d')
        
        info['location'] = parser.extract_location(extracted_text)
        info['time'] = parser.extract_time(extracted_text)
        
        return info
