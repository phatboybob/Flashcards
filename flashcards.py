'''
Flashcards App Created (for now) to run English to German or German to English
translations.

Created by Lori Jackson January 2025
'''

from pathlib import Path

import streamlit as st

from utils import (
                    # get_flashcard_dataframe,
                    # view_flashcard_data_editor,
                    # view_flashcard_table,
                    # get_vocab_sample,
                    # set_other_direction,
                    # set_params,
                    # set_word_line_values,
                    # check_word,
                    # remove_word,
                    # clear_values,
                    # update_correct_word,
                    # update_incorrect_word,
                    # merge_dataframes,
                    # disable_buttons,
                    # switch_buttons,
                    # write_df_to_google_drive,
                    set_current_user,
                    login_screen,
                    set_page_config,
                  )

DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'
OTHER_DIRECTION = ''

SKIP_LOGIN = False

if 'local_dev' not in st.session_state:
    st.session_state.local_dev = False
secrets_toml_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
if Path.exists(secrets_toml_path):
    st.session_state.local_dev = True



if 'current_user' not in st.session_state:
    st.session_state.current_user = "Nobody"

if st.session_state.local_dev:
    if st.user.is_logged_in or st.session_state.current_user == "Guest":
        if st.user.is_logged_in:
            print("user email is: ", st.user.email)
            set_current_user(user=st.user.name)
        else:
            set_current_user(user="Guest")
        st.header(f"Welcome {st.session_state.current_user}!")
        set_page_config()

        if st.button("Log out"):
            st.logout()
    else:
        login_screen()
            # if st.user.email not in st.secrets["authorized_users"]:
            #     st.header(f"Access Denied {st.user.name}")
            #     st.subheader(f"{st.user.email} does not have permission to view this app.")


# This means there's no toml file.
# this happens in dev when:
#.    1. I removed it for testing locally
#.    2. An auth user is running it in the prod and need to log in
#     3. Someone else is running it in prod and needs to continue as a guest
else:
    # if st.user.is_logged_in---- change to a gcp means of login:
    #   st.header("Welcome!")
    #   set_page_config()
    #         if st.button("Log out"):
    #             st.logout()

    if st.session_state.current_user == "Nobody":
        login_screen()
    if st.session_state.current_user == "Guest":
        set_page_config()
        if st.button("Log out"):
                    st.logout()

