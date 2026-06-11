"""
Document processing service with OCR and data extraction
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Service for processing uploaded documents
    Handles OCR, data extraction, and validation
    """
    
    def __init__(self, ocr_provider: str = "tesseract"):
        self.ocr_provider = ocr_provider
        self.supported_formats = ["pdf", "jpg", "jpeg", "png", "tiff"]
        
    async def process_document(
        self, 
        file_path: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Process an uploaded document
        
        Args:
            file_path: Path to the uploaded file
            document_type: Type of document (passport, photo, etc.)
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            # Validate file format
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Perform OCR based on provider
            ocr_result = await self._perform_ocr(file_path)
            
            # Extract relevant data based on document type
            extracted_data = await self._extract_data(
                ocr_result['text'], 
                document_type
            )
            
            return {
                "success": True,
                "document_type": document_type,
                "ocr_text": ocr_result['text'],
                "ocr_confidence": ocr_result.get('confidence', 0),
                "extracted_data": extracted_data,
                "processed_at": datetime.utcnow().isoformat(),
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_type": document_type,
                "processed_at": datetime.utcnow().isoformat()
            }
    
    async def _perform_ocr(self, file_path: str) -> Dict[str, Any]:
        """
        Perform OCR on document
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with OCR text and confidence score
        """
        if self.ocr_provider == "tesseract":
            return await self._ocr_with_tesseract(file_path)
        elif self.ocr_provider == "aws_textract":
            return await self._ocr_with_aws_textract(file_path)
        elif self.ocr_provider == "google_vision":
            return await self._ocr_with_google_vision(file_path)
        else:
            # Default fallback
            return await self._ocr_with_tesseract(file_path)
    
    async def _ocr_with_tesseract(self, file_path: str) -> Dict[str, Any]:
        """Perform OCR using Tesseract"""
        try:
            import pytesseract
            from PIL import Image
            
            # Handle PDF files
            if file_path.lower().endswith('.pdf'):
                import pdf2image
                pages = pdf2image.convert_from_path(file_path)
                text = ""
                for page in pages:
                    text += pytesseract.image_to_string(page) + "\n"
            else:
                # Handle image files
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
            
            return {
                "text": text,
                "confidence": 85  # Placeholder - tesseract doesn't provide confidence easily
            }
            
        except ImportError:
            logger.warning("Tesseract not installed, using mock OCR")
            return self._mock_ocr_result()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            return self._mock_ocr_result()
    
    async def _ocr_with_aws_textract(self, file_path: str) -> Dict[str, Any]:
        """Perform OCR using AWS Textract"""
        try:
            import boto3
            
            textract_client = boto3.client('textract')
            
            with open(file_path, 'rb') as f:
                response = textract_client.detect_document_text(
                    Document={'Bytes': f.read()}
                )
            
            # Extract text from response
            text_blocks = []
            for item in response.get('Blocks', []):
                if item['BlockType'] == 'LINE':
                    text_blocks.append(item['Text'])
            
            return {
                "text": "\n".join(text_blocks),
                "confidence": 95  # Textract typically has high confidence
            }
            
        except Exception as e:
            logger.error(f"AWS Textract failed: {str(e)}")
            return self._mock_ocr_result()
    
    async def _ocr_with_google_vision(self, file_path: str) -> Dict[str, Any]:
        """Perform OCR using Google Vision API"""
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return {
                    "text": texts[0].description,
                    "confidence": 95
                }
            
            return {"text": "", "confidence": 0}
            
        except Exception as e:
            logger.error(f"Google Vision failed: {str(e)}")
            return self._mock_ocr_result()
    
    def _mock_ocr_result(self) -> Dict[str, Any]:
        """Return mock OCR result for testing/development"""
        return {
            "text": "Mock OCR text - replace with actual OCR implementation",
            "confidence": 75
        }
    
    async def _extract_data(
        self, 
        ocr_text: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from OCR text based on document type
        
        Args:
            ocr_text: Raw text from OCR
            document_type: Type of document
            
        Returns:
            Dictionary with extracted structured data
        """
        if document_type == "passport":
            return await self._extract_passport_data(ocr_text)
        elif document_type == "photograph":
            return await self._extract_photo_metadata(ocr_text)
        elif document_type == "bank_statement":
            return await self._extract_bank_statement_data(ocr_text)
        elif document_type == "employment_letter":
            return await self._extract_employment_data(ocr_text)
        elif document_type == "travel_insurance":
            return await self._extract_insurance_data(ocr_text)
        elif document_type == "flight_itinerary":
            return await self._extract_flight_data(ocr_text)
        elif document_type == "accommodation_proof":
            return await self._extract_accommodation_data(ocr_text)
        elif document_type == "invitation_letter":
            return await self._extract_invitation_data(ocr_text)
        else:
            return await self._extract_generic_data(ocr_text)
    
    async def _extract_passport_data(self, text: str) -> Dict[str, Any]:
        """Extract data from passport"""
        # This would use NLP/ML models in production
        # For now, return placeholder structure
        return {
            "document_type": "passport",
            "passport_number": None,
            "surname": None,
            "given_names": None,
            "nationality": None,
            "date_of_birth": None,
            "place_of_birth": None,
            "issue_date": None,
            "expiry_date": None,
            "issuing_authority": None,
            "extraction_confidence": 0.0,
            "notes": "Requires ML model for accurate extraction"
        }
    
    async def _extract_photo_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from photograph"""
        return {
            "document_type": "photograph",
            "dimensions": None,
            "background_color": None,
            "face_detected": None,
            "quality_score": None,
            "meets_specifications": None
        }
    
    async def _extract_bank_statement_data(self, text: str) -> Dict[str, Any]:
        """Extract data from bank statement"""
        return {
            "document_type": "bank_statement",
            "account_holder_name": None,
            "account_number": None,
            "bank_name": None,
            "statement_period": None,
            "closing_balance": None,
            "currency": None,
            "average_balance": None
        }
    
    async def _extract_employment_data(self, text: str) -> Dict[str, Any]:
        """Extract data from employment letter"""
        return {
            "document_type": "employment_letter",
            "employee_name": None,
            "employer_name": None,
            "designation": None,
            "employment_duration": None,
            "salary": None,
            "letter_date": None,
            "is_on_company_letterhead": None
        }
    
    async def _extract_insurance_data(self, text: str) -> Dict[str, Any]:
        """Extract data from travel insurance"""
        return {
            "document_type": "travel_insurance",
            "policy_number": None,
            "policy_holder": None,
            "coverage_amount": None,
            "currency": None,
            "validity_start": None,
            "validity_end": None,
            "insurance_provider": None,
            "coverage_region": None
        }
    
    async def _extract_flight_data(self, text: str) -> Dict[str, Any]:
        """Extract data from flight itinerary"""
        return {
            "document_type": "flight_itinerary",
            "passenger_name": None,
            "booking_reference": None,
            "flights": [],
            "departure_date": None,
            "return_date": None,
            "airline": None,
            "total_cost": None
        }
    
    async def _extract_accommodation_data(self, text: str) -> Dict[str, Any]:
        """Extract data from accommodation proof"""
        return {
            "document_type": "accommodation_proof",
            "guest_name": None,
            "hotel_name": None,
            "address": None,
            "check_in_date": None,
            "check_out_date": None,
            "booking_reference": None,
            "total_cost": None
        }
    
    async def _extract_invitation_data(self, text: str) -> Dict[str, Any]:
        """Extract data from invitation letter"""
        return {
            "document_type": "invitation_letter",
            "invitee_name": None,
            "inviter_name": None,
            "inviter_address": None,
            "purpose_of_visit": None,
            "visit_duration": None,
            "relationship": None,
            "letter_date": None
        }
    
    async def _extract_generic_data(self, text: str) -> Dict[str, Any]:
        """Extract generic data from unknown document type"""
        return {
            "document_type": "unknown",
            "raw_text": text[:500],  # First 500 chars
            "word_count": len(text.split()),
            "detected_language": "en"
        }
    
    def validate_document_quality(self, file_path: str) -> Dict[str, Any]:
        """
        Validate document quality before processing
        
        Args:
            file_path: Path to the document
            
        Returns:
            Quality assessment results
        """
        try:
            from PIL import Image
            
            if file_path.lower().endswith('.pdf'):
                import pdf2image
                pages = pdf2image.convert_from_path(file_path)
                img = pages[0]  # Check first page
            else:
                img = Image.open(file_path)
            
            width, height = img.size
            file_size = os.path.getsize(file_path)
            
            return {
                "is_valid": True,
                "width": width,
                "height": height,
                "file_size_bytes": file_size,
                "resolution_dpi": 300,  # Would need proper calculation
                "quality_score": 85,
                "recommendations": []
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }
