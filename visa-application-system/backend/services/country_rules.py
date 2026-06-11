"""
Country-specific visa requirements and rule engine
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class CountryRuleEngine:
    """
    Engine for managing country-specific visa requirements and validation rules
    Handles compliance with data protection regulations for each country
    """
    
    def __init__(self):
        self.country_requirements = self._load_country_requirements()
    
    def _load_country_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load country-specific requirements"""
        return {
            "SCH": {
                "country_code": "SCH",
                "country_name": "Schengen Area",
                "visa_required": True,
                "required_documents": [
                    "passport",
                    "photograph",
                    "travel_insurance",
                    "flight_itinerary",
                    "accommodation_proof",
                    "financial_proof",
                    "employment_letter",
                    "bank_statements"
                ],
                "passport_validity_months": 6,
                "min_financial_proof": 50000,  # BDT equivalent
                "requires_biometric": True,
                "requires_interview": False,
                "processing_time_days": 15,
                "gdpr_compliant": True,
                "data_retention_days": 90,
                "photo_specifications": {
                    "size": "35mm x 45mm",
                    "background": "white",
                    "format": "JPEG/PNG"
                },
                "insurance_requirements": {
                    "min_coverage_eur": 30000,
                    "coverage_type": "medical_emergency"
                }
            },
            "CHN": {
                "country_code": "CHN",
                "country_name": "China",
                "visa_required": True,
                "required_documents": [
                    "passport",
                    "photograph",
                    "invitation_letter",
                    "flight_itinerary",
                    "hotel_booking",
                    "financial_proof",
                    "employment_certificate"
                ],
                "passport_validity_months": 6,
                "min_financial_proof": 30000,
                "requires_biometric": True,
                "requires_interview": False,
                "processing_time_days": 7,
                "gdpr_compliant": False,
                "data_retention_days": 60,
                "photo_specifications": {
                    "size": "33mm x 48mm",
                    "background": "white",
                    "format": "JPEG"
                },
                "special_requirements": [
                    "Invitation letter from Chinese host",
                    "Business visa requires company registration"
                ]
            },
            "THA": {
                "country_code": "THA",
                "country_name": "Thailand",
                "visa_required": True,
                "required_documents": [
                    "passport",
                    "photograph",
                    "flight_itinerary",
                    "accommodation_proof",
                    "financial_proof"
                ],
                "passport_validity_months": 6,
                "min_financial_proof": 20000,
                "requires_biometric": False,
                "requires_interview": False,
                "processing_time_days": 5,
                "gdpr_compliant": False,
                "data_retention_days": 30,
                "photo_specifications": {
                    "size": "35mm x 45mm",
                    "background": "white",
                    "format": "JPEG/PNG"
                },
                "visa_exemption": {
                    "enabled": True,
                    "max_days": 30,
                    "conditions": ["Tourist purpose only", "Return ticket required"]
                }
            },
            "MYS": {
                "country_code": "MYS",
                "country_name": "Malaysia",
                "visa_required": True,
                "required_documents": [
                    "passport",
                    "photograph",
                    "flight_itinerary",
                    "accommodation_proof",
                    "financial_proof",
                    "return_ticket"
                ],
                "passport_validity_months": 6,
                "min_financial_proof": 15000,
                "requires_biometric": False,
                "requires_interview": False,
                "processing_time_days": 3,
                "gdpr_compliant": False,
                "data_retention_days": 30,
                "photo_specifications": {
                    "size": "35mm x 50mm",
                    "background": "white",
                    "format": "JPEG"
                },
                "evissa_enabled": True
            },
            "SGP": {
                "country_code": "SGP",
                "country_name": "Singapore",
                "visa_required": True,
                "required_documents": [
                    "passport",
                    "photograph",
                    "flight_itinerary",
                    "accommodation_proof",
                    "financial_proof",
                    "local_contact_info"
                ],
                "passport_validity_months": 6,
                "min_financial_proof": 30000,
                "requires_biometric": False,
                "requires_interview": False,
                "processing_time_days": 5,
                "gdpr_compliant": False,
                "data_retention_days": 60,
                "photo_specifications": {
                    "size": "35mm x 45mm",
                    "background": "white",
                    "format": "JPEG"
                },
                "safetravel_compliant": True
            }
        }
    
    def get_requirements(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get requirements for a specific country"""
        return self.country_requirements.get(country_code.upper())
    
    def get_required_documents(self, country_code: str) -> List[str]:
        """Get list of required documents for a country"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return []
        return requirements.get("required_documents", [])
    
    def check_missing_documents(
        self, 
        country_code: str, 
        uploaded_documents: List[Any]
    ) -> List[str]:
        """
        Check which required documents are missing
        
        Args:
            country_code: Destination country code
            uploaded_documents: List of Document objects with document_type attribute
            
        Returns:
            List of missing document types
        """
        required_docs = set(self.get_required_documents(country_code))
        uploaded_docs = set(doc.document_type for doc in uploaded_documents)
        
        missing_docs = required_docs - uploaded_docs
        return list(missing_docs)
    
    def validate_passport_validity(
        self, 
        country_code: str, 
        passport_expiry_date: datetime
    ) -> bool:
        """Validate passport has sufficient validity remaining"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return True
        
        required_months = requirements.get("passport_validity_months", 6)
        min_validity_date = datetime.now().replace(
            year=datetime.now().year + (required_months // 12),
            month=datetime.now().month + (required_months % 12)
        )
        
        return passport_expiry_date > min_validity_date
    
    def validate_financial_proof(
        self, 
        country_code: str, 
        amount: float
    ) -> bool:
        """Validate financial proof meets minimum requirement"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return True
        
        min_amount = requirements.get("min_financial_proof", 0)
        return amount >= min_amount
    
    def validate_data_consistency(
        self, 
        documents: List[Any]
    ) -> List[str]:
        """
        Validate consistency of extracted data across documents
        
        Args:
            documents: List of Document objects with extracted_data
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Extract key data points from all documents
        names = []
        passport_numbers = []
        dates_of_birth = []
        
        for doc in documents:
            if hasattr(doc, 'extracted_data') and doc.extracted_data:
                data = doc.extracted_data
                
                if 'name' in data:
                    names.append(data['name'])
                if 'passport_number' in data:
                    passport_numbers.append(data['passport_number'])
                if 'date_of_birth' in data:
                    dates_of_birth.append(data['date_of_birth'])
        
        # Check for inconsistencies
        if len(set(names)) > 1:
            errors.append(f"Inconsistent names found: {names}")
        
        if len(set(passport_numbers)) > 1:
            errors.append(f"Inconsistent passport numbers found: {passport_numbers}")
        
        if len(set(dates_of_birth)) > 1:
            errors.append(f"Inconsistent dates of birth found: {dates_of_birth}")
        
        return errors
    
    def get_data_handling_rules(self, country_code: str) -> Dict[str, Any]:
        """Get data handling and privacy rules for a country"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return {}
        
        return {
            "gdpr_compliant": requirements.get("gdpr_compliant", False),
            "data_retention_days": requirements.get("data_retention_days", 90),
            "requires_encryption": True,
            "requires_consent": True,
            "allowed_data_transfer": requirements.get("gdpr_compliant", False)
        }
    
    def get_photo_specifications(self, country_code: str) -> Dict[str, str]:
        """Get photograph specifications for a country"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return {}
        
        return requirements.get("photo_specifications", {})
    
    def get_processing_time(self, country_code: str) -> int:
        """Get estimated processing time in days"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return 0
        
        return requirements.get("processing_time_days", 0)
    
    def is_biometric_required(self, country_code: str) -> bool:
        """Check if biometric data is required"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return False
        
        return requirements.get("requires_biometric", False)
    
    def is_interview_required(self, country_code: str) -> bool:
        """Check if interview is required"""
        requirements = self.get_requirements(country_code)
        if not requirements:
            return False
        
        return requirements.get("requires_interview", False)
