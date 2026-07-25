# core/validator.py

def validate_interval(value_str, default=100.0, min_val=0.1, max_val=3600000.0):
    """اعتبارسنجی تاخیر زمان کلیک (بین 0.1 میلی‌ثانیه تا 1 ساعت)"""
    try:
        val = float(value_str)
        if val < min_val:
            return min_val
        if val > max_val:
            return max_val
        return val
    except (ValueError, TypeError):
        return default

def validate_duration(value_str, default=10.0, min_val=1.0, max_val=86400.0):
    """اعتبارسنجی مدت زمان توقف خودکار (بین 1 ثانیه تا 24 ساعت)"""
    try:
        val = float(value_str)
        if val < min_val:
            return min_val
        if val > max_val:
            return max_val
        return val
    except (ValueError, TypeError):
        return default

def validate_coordinate(value_str, default=0):
    """اعتبارسنجی مختصات X و Y موس"""
    try:
        val = int(value_str)
        return max(0, val)
    except (ValueError, TypeError):
        return default