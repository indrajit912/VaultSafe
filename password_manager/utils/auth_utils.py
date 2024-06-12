# /utils/auth_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#

import pwinput

def get_password(info_msg:str="Enter your password: ", success_msg:str="Password set successfully!"):
    bullet_unicode = '\u2022'
    while True:
        password1 = pwinput.pwinput(info_msg, mask=bullet_unicode)
        if password1 == '':
            return
        password2 = input("Confirm your password: ")
        if password1 == password2:
            print(success_msg)
            return password1
        else:
            print("Passwords do not match. Please try again.")
    