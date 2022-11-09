import re 
import bleach

def is_email(email):
    if '@' in email: return True
    else: return False


# Used for First and Last Name
name_length_regex = {
    'regex': """^(?=.{1,40}$)""", 
    'error': "Name does not match our requirements."
}
name_character_regex = {
    'regex': """^[a-zA-Z]+(?:[-' ][a-zA-Z]+)*$""", 
    'error': "Name does not match our requirements."
}
name_tests = [name_length_regex, name_character_regex]


# Used for First and Last Name
alphanumeric_name_length_regex = {
    'regex': """^(?=.{1,40}$)""", 
    'error': "Name does not match our requirements."
}
alphanumeric_name_character_regex = {
    'regex': """^[a-zA-Z0-9]+(?:[-' ][a-zA-Z0-9]+)*$""", 
    'error': "Name does not match our requirements."
}
alphanumeric_name_tests = [alphanumeric_name_length_regex, alphanumeric_name_character_regex]


# Used for User Name
username_length_regex = {
    'regex': """^(?=.{4,16}$)""", 
    'error': "Username does not meet our requirements."
}
username_character_regex = {
    'regex': """^(?!\.)(?!\_)(?!.*\.$)(?!.*\_$)(?!.*?\.\.)(?!.*?\_\_)(?!.*?\_\.)(?!.*?\.\_)[a-z0-9_.]+$""", 
    'error': "Username does not meet our requirements"
}
username_letter_regex = {
    'regex': """^([a-z].*?){4,}""", 
    'error': "Username does not meet our requirments"
}
username_tests = [username_length_regex, username_character_regex, username_letter_regex]


# Used for Email
email_length_regex = {
    'regex':"""^(?=.{3,320}$)""", 
    'error': "Email length does not match."
}
# Reconsider why we even need Email Regex
email_pattern_regex = {
    #'regex': """^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
    'regex': """^.+@.+\..+$""",
    #'regex': """^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
    'error': "Email must be a correct pattern."
}
email_tests = [email_length_regex, email_pattern_regex]

# Used for Password
password_length_regex = {
    'regex': """^(?=.{10,50}$)""", 
    'error': "Password length does not meet our requirements."
}
password_special_character_regex = { 
    'regex': """^(?=.*[*.!@#$%^&(){}[\]:;<>,.?\/~_+\-=|'"`])""", 
    'error': "Password must include at least one special character."
}
password_alpha_lower_character_regex = {
    'regex': """^(?=.*[a-z])""",
    'error': "Password must include at least one lower character."
}
password_alpha_upper_character_regex = {
    'regex': """^(?=.*[A-Z])""",
    'error': "Password must include at least one upper character."
}
password_numeric_character_regex = {
    'regex': """^(?=.*[0-9])""",
    'error': "Password must include at least one number."
}

password_tests = [
        password_length_regex, 
        password_numeric_character_regex, 
        password_alpha_lower_character_regex, 
        password_alpha_upper_character_regex, 
        password_special_character_regex
    ]

message_length_regex = {
    'regex': """^(?=.{0,64}$)""",
    'error': 'Message length does not meet our requirements.'
}
message_tests = [message_length_regex]


def validate_name(text, message=False):
    """
        Used to validate First and Last Names.
    """
    for test in name_tests:
        if not re.search(test['regex'], text): 
            if message: return False, test['message']
            else: return False
    return True


def validate_alphanumeric_name(text, message=False):
    """
        Used to validate alphanumeric names.
    """
    for test in alphanumeric_name_tests:
        if not re.search(test['regex'], text):
            if message: return False, test['error']
            else: return False
    return True


def validate_message(text, message=False):
    """
        Used to validate user messages.
    """
    for test in message_tests: 
        if not re.search(test['regex'], text):
            if message: return False, test['error']
            else: return False
    return True


def validate_email(text, message=False):  
    '''
        Used to validate Emails.
    '''
    # Quick check to see if there is any hidden javascript in an email.
    if bleach.clean(text) != text: return False

    for test in email_tests:
        if not re.search(test['regex'], text):
            if message: return False, test['error']
            else: return False
    return True


def validate_handle(text, message=False):
    """
        Used to validate usernames.
    """
    for test in username_tests:
        if not re.search(test['regex'], text):
            if message: return False, test['error']
            else: return False
    return True


def validate_password(text, message=False):
    """
        Used to validate Passwords.
    """
    for test in password_tests:
        if not re.search(test['regex'], text):
            if message: return False, test['error']
            else: return False
    return True