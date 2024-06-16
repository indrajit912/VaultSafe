# /utils/general_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 16, 2024
#
import string
import secrets
from datetime import datetime, timedelta, timezone

import pytz
from tzlocal import get_localzone_name

def generate_strong_password(length=15):
    """
    Generate a strong password of specified length.
    
    Args:
        length (int): Length of the password to be generated.
        
    Returns:
        str: The generated strong password.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4 characters.")
    
    characters = string.ascii_letters + string.digits + "@#$-%&"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def get_system_timezone():
    """
    Get the system's current timezone.

    Returns:
        str: The system's timezone, or None if it cannot be determined.
    """
    try:
        # Get the local timezone name using tzlocal
        local_tz_name = get_localzone_name()
        return local_tz_name
    except Exception as e:
        # Log the exception if needed
        return None

def utcnow():
    """
    Get the current UTC datetime.

    Returns:
        datetime: A datetime object representing the current UTC time.
    """
    return datetime.now(timezone.utc)

def get_timezone_offset(timezone_str):
    """
    Get the UTC offset for a given timezone string.

    Args:
        timezone_str (str): The timezone string.

    Returns:
        timedelta: The offset of the given timezone from UTC.
    """
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        offset = now.utcoffset()
        return offset
    except Exception as e:
        # Log the exception if needed
        return timedelta(0)  # Default to UTC offset

def convert_utc_to_local_str(dt, show_time: bool = True, weekday: bool = True):
    """
    Convert a datetime object with timezone information UTC to a string representation in local time format.

    Args:
        dt (datetime.datetime): A datetime object with timezone information UTC.
        show_time (bool, optional): Whether to include the time in the output string. Defaults to True.
        weekday (bool, optional): Whether to include the weekday in the output string. Defaults to True.

    Returns:
        str: A string representation of the datetime object in local time format.
    """
    timezone_str = get_system_timezone()

    # Get the offset for the given timezone
    offset = get_timezone_offset(timezone_str)

    # Check whether the offset found or not
    timezone_str = 'UTC' if offset == timedelta(0) else timezone_str
    
    # Convert UTC to local time
    dt_local = dt + offset

    # Format the datetime object
    local_format = ""
    if weekday:
        local_format += dt_local.strftime("%a, ")
    local_format += dt_local.strftime("%d %b %Y")
    if show_time:
        local_format += dt_local.strftime(f" %I:%M %p ({timezone_str})")

    return local_format