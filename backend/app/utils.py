import re


re_simple_email = re.compile(
    r'^[-_.a-zA-Z0-9]{3,}@([-a-zA-Z0-9]+\.)+[-a-zA-Z0-9]+$'
)
