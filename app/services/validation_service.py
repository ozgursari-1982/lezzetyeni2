import re
from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    """Giriş verilerini doğrulama servisi"""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Telefon numarası formatını doğrula"""
        if not phone:
            return False, "Telefon numarası gereklidir"
        
        # Türk telefon numarası formatı: 05xx xxx xx xx
        phone_pattern = r'^(\+90|0)?[5][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2}$'
        
        # Boşlukları ve özel karakterleri temizle
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        if re.match(phone_pattern, clean_phone):
            return True, None
        else:
            return False, "Geçerli bir telefon numarası girin (05xx xxx xx xx)"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Email formatını doğrula"""
        if not email:
            return True, None  # Email opsiyonel
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, email):
            return True, None
        else:
            return False, "Geçerli bir email adresi girin"
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> Tuple[bool, Optional[str]]:
        """Ad formatını doğrula"""
        if not name or not name.strip():
            return False, "Ad gereklidir"
        
        name = name.strip()
        
        if len(name) < min_length:
            return False, f"Ad en az {min_length} karakter olmalıdır"
        
        if len(name) > max_length:
            return False, f"Ad en fazla {max_length} karakter olabilir"
        
        # Sadece harf, boşluk ve Türkçe karakterler
        if not re.match(r'^[a-zA-Z\u00c0-\u017F\s]+$', name):
            return False, "Ad sadece harf ve boşluk karakterleri içerebilir"
        
        return True, None
    
    @staticmethod
    def validate_party_size(party_size: int, max_size: int = 12) -> Tuple[bool, Optional[str]]:
        """Grup boyutunu doğrula"""
        if not isinstance(party_size, int):
            return False, "Kişi sayısı sayı olmalıdır"
        
        if party_size < 1:
            return False, "Kişi sayısı en az 1 olmalıdır"
        
        if party_size > max_size:
            return False, f"Kişi sayısı en fazla {max_size} olabilir"
        
        return True, None
    
    @staticmethod
    def validate_date(reservation_date: date, advance_days: int = 30) -> Tuple[bool, Optional[str]]:
        """Rezervasyon tarihini doğrula"""
        if not isinstance(reservation_date, date):
            return False, "Geçerli bir tarih girin"
        
        today = date.today()
        
        if reservation_date < today:
            return False, "Geçmiş tarih seçilemez"
        
        max_date = date.today().replace(day=today.day + advance_days)
        if reservation_date > max_date:
            return False, f"En fazla {advance_days} gün öncesinden rezervasyon yapılabilir"
        
        return True, None
    
    @staticmethod
    def validate_time(reservation_time: time, 
                     opening_time: time = time(11, 0),
                     closing_time: time = time(23, 30)) -> Tuple[bool, Optional[str]]:
        """Rezervasyon saatini doğrula"""
        if not isinstance(reservation_time, time):
            return False, "Geçerli bir saat girin"
        
        if reservation_time < opening_time or reservation_time > closing_time:
            return False, f"Rezervasyon saati {opening_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')} arasında olmalıdır"
        
        return True, None
    
    @staticmethod
    def validate_special_requests(requests: Optional[str], max_length: int = 500) -> Tuple[bool, Optional[str]]:
        """Özel istekleri doğrula"""
        if not requests:
            return True, None
        
        if len(requests) > max_length:
            return False, f"Özel istekler en fazla {max_length} karakter olabilir"
        
        # Zararlı karakterleri kontrol et
        dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        requests_lower = requests.lower()
        
        for pattern in dangerous_patterns:
            if pattern in requests_lower:
                return False, "Geçersiz karakterler tespit edildi"
        
        return True, None
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Giriş verisini temizle"""
        if not input_str:
            return ""
        
        # HTML tag'lerini temizle
        clean_str = re.sub(r'<[^>]+>', '', input_str)
        
        # SQL injection karakterlerini temizle
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            clean_str = clean_str.replace(char, '')
        
        return clean_str.strip()
    
    @classmethod
    def validate_reservation_data(cls, data: Dict) -> Tuple[bool, List[str]]:
        """Tüm rezervasyon verilerini doğrula"""
        errors = []
        
        # Ad doğrulama
        name_valid, name_error = cls.validate_name(data.get('customer_name', ''))
        if not name_valid:
            errors.append(name_error)
        
        # Telefon doğrulama
        phone_valid, phone_error = cls.validate_phone(data.get('phone', ''))
        if not phone_valid:
            errors.append(phone_error)
        
        # Email doğrulama
        email_valid, email_error = cls.validate_email(data.get('email', ''))
        if not email_valid:
            errors.append(email_error)
        
        # Kişi sayısı doğrulama
        try:
            party_size = int(data.get('party_size', 0))
            size_valid, size_error = cls.validate_party_size(party_size)
            if not size_valid:
                errors.append(size_error)
        except (ValueError, TypeError):
            errors.append("Kişi sayısı geçerli bir sayı olmalıdır")
        
        # Tarih doğrulama
        try:
            if isinstance(data.get('reservation_date'), str):
                reservation_date = datetime.strptime(data['reservation_date'], '%Y-%m-%d').date()
            else:
                reservation_date = data.get('reservation_date')
            
            date_valid, date_error = cls.validate_date(reservation_date)
            if not date_valid:
                errors.append(date_error)
        except (ValueError, TypeError):
            errors.append("Geçerli bir tarih girin")
        
        # Saat doğrulama
        try:
            if isinstance(data.get('start_time'), str):
                start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            else:
                start_time = data.get('start_time')
            
            time_valid, time_error = cls.validate_time(start_time)
            if not time_valid:
                errors.append(time_error)
        except (ValueError, TypeError):
            errors.append("Geçerli bir saat girin")
        
        # Özel istekler doğrulama
        requests_valid, requests_error = cls.validate_special_requests(data.get('special_requests'))
        if not requests_valid:
            errors.append(requests_error)
        
        return len(errors) == 0, errors

# Global instance
validation_service = ValidationService()