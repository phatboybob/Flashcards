"""
Utilities for the Streamlit German Flashcards app
Created by Lori Jackson January 2025
"""

from typing_extensions import Literal

import pandas
import streamlit as st
from streamlit_gsheets import GSheetsConnection

LORIS_FLASHCARDS_WORKSHEET = 'Lori_streamlit'
JONATHANS_FLASHCARDS_WORKSHEET = 'Jonathan_streamlit'
KERRYS_FLASHCARDS_WORKSHEET = 'Kerry_streamlit'
SAMPLE_CSV = 'sample.csv'
DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'
COLUMNS_AND_TYPES = {f'{DIRECTION_ENGLISH} Word': str,
                     f'{DIRECTION_ENGLISH} Correct Count': 'Int64',
                     f'{DIRECTION_ENGLISH} Call Count': 'Int64',
                     f'{DIRECTION_ENGLISH} Percent Correct': float,
                     f'{DIRECTION_GERMAN} Word': str,
                     f'{DIRECTION_GERMAN} Correct Count': 'Int64',
                     f'{DIRECTION_GERMAN} Call Count': 'Int64',
                     f'{DIRECTION_GERMAN} Percent Correct': float}

COLUM_CONFIG = {f'{DIRECTION_ENGLISH} Word': st.column_config.TextColumn(required=True),
                f'{DIRECTION_ENGLISH} Correct Count': st.column_config.NumberColumn(default=0),
                f'{DIRECTION_ENGLISH} Call Count': st.column_config.NumberColumn(default=0),
                f'{DIRECTION_ENGLISH} Percent Correct': st.column_config.NumberColumn(
                    format='%.2f %%',
                    default=0.0),
                f'{DIRECTION_GERMAN} Word': st.column_config.TextColumn(required=True),
                f'{DIRECTION_GERMAN} Correct Count': st.column_config.NumberColumn(default=0),
                f'{DIRECTION_GERMAN} Call Count': st.column_config.NumberColumn(default=0),
                f'{DIRECTION_GERMAN} Percent Correct': st.column_config.NumberColumn(
                    format='%.2f %%',
                    default=0.0)
               }

def get_flashcard_worksheet_by_user(user='Guest'):
    """Read in the default csv. Unless it's not there.

    Returns:
        dataframe: the pandas dataframe of the csv. otherwise None
    """
    match user:
        case 'Lori Jackson':
            flashcard_path = LORIS_FLASHCARDS_WORKSHEET
        case 'Jonathan ODell':
            flashcard_path = JONATHANS_FLASHCARDS_WORKSHEET
        case 'Kerry Rohner':
            flashcard_path = KERRYS_FLASHCARDS_WORKSHEET
        case 'Guest':
            flashcard_path = 'sample.csv'
        case 'Local_Dev':
            flashcard_path = 'sample.csv'
        case _:
            flashcard_path = 'sample.csv'
    return flashcard_path


def get_flashcard_dataframe(user='Guest'):
    """Uploads a csv and returns it as a dataframe

    Args:
        flashcard_path (path, optional): path to a csv. Defaults to LORIS_FLASHCARDS_CSV.

    Returns:
        dataframe: dataframe conversion of the csv
    """

    if st.session_state.current_user != 'Guest':
        # Create a connection object.
        gcp_connection = st.connection("gsheets",
                                    type=GSheetsConnection)

        flashcard_worksheet = get_flashcard_worksheet_by_user(user=user)
        flashcards_df = gcp_connection.read(worksheet=flashcard_worksheet).dropna(subset=[f'{DIRECTION_ENGLISH} Word',
                                                                                     f'{DIRECTION_GERMAN} Word']).fillna(0)
    else:
        flashcards_df = pandas.read_csv(SAMPLE_CSV).dropna(subset=[f'{DIRECTION_ENGLISH} Word',
                                                                        f'{DIRECTION_GERMAN} Word']).fillna(0)
    return flashcards_df


def view_flashcard_data_editor(flashcards_df,
                               english_min_correct=0,
                               english_max_correct=100,
                               german_min_correct=0,
                               german_max_correct=100,
                               english_min_call=0,
                               english_max_call=100,
                               german_min_call=0,
                               german_max_call=100,
                               english_min_percent=0.0,
                               english_max_percent=100.0,
                               german_min_percent=0.0,
                               german_max_percent=100.0,
                               ):
    """displays everything in the review panel
    """




    filtered_english_count = flashcards_df[
       (flashcards_df[f'{DIRECTION_ENGLISH} Correct Count'] <= english_max_correct)
       & (english_min_correct <= flashcards_df[f'{DIRECTION_ENGLISH} Correct Count'])
       & (flashcards_df[f'{DIRECTION_GERMAN} Correct Count'] <= german_max_correct)
       & (german_min_correct <= flashcards_df[f'{DIRECTION_GERMAN} Correct Count'])
       & (flashcards_df[f'{DIRECTION_ENGLISH} Call Count'] <= english_max_call)
       & (english_min_call <= flashcards_df[f'{DIRECTION_ENGLISH} Call Count'])
       & (flashcards_df[f'{DIRECTION_GERMAN} Call Count'] <= german_max_call)
       & (german_min_call <= flashcards_df[f'{DIRECTION_GERMAN} Call Count'])
       & (flashcards_df[f'{DIRECTION_ENGLISH} Percent Correct'] <= english_max_percent)
       & (english_min_percent <= flashcards_df[f'{DIRECTION_ENGLISH} Percent Correct'])
       & (flashcards_df[f'{DIRECTION_GERMAN} Percent Correct'] <= german_max_percent)
       & (german_min_percent <= flashcards_df[f'{DIRECTION_GERMAN} Percent Correct'])
    ]
    if not filtered_english_count.empty:
        st.data_editor(
            data=filtered_english_count,
            width='content',
            num_rows='dynamic',
            column_config=COLUM_CONFIG,
        )
    else:
        st.write("Please Upload Data")


def view_flashcard_table(flashcards_df):
    """prints out the summary table after getting all words correct
    """

    flashcards_df['Run Again'] = 'False'
    if not flashcards_df.empty:
        st.session_state.results_df = st.data_editor(
            flashcards_df,
            width='content',
            column_config={
                "Run Again": st.column_config.CheckboxColumn(
                    "Check Box to Run Again",
                    help="Select all the words you want to run again",
                    default=False,
                ),
            },
            hide_index=True,
        )

    # words_to_run_again = results_df[results_df['Run Again']]
    # if not words_to_run_again.empty:
    #     print(f"words to run again: {words_to_run_again}")
    else:
        st.write("please upload data")


def get_vocab_sample(params: dict,
                     direction: Literal["DIRECTION_GERMAN", "DIRECTION_ENGLISH"]
                     ):
    """get a sample from the huge list of words
    Args:
        number_to_ask (int): how man words to ask (maximum)
        percent_corret (float): only show words that you've gotten right less than this
        correct_count (int): only show words that have been correct less than this
    """
    # entire dataframe
    all_words = st.session_state.flashcards_df

    # all words that fit the ask count and percent cuttoff
    fewer_words = all_words[(all_words[f'{direction} Correct Count'] <= int(params['correct_count']))
                            & (all_words[f'{direction} Percent Correct'] <= float(params['percent_correct']))]

    # subset of qualifying words
    # subset may be less than the number to ask, leading to out of bounds error
    if len(fewer_words) <= int(params['number_to_ask']):
        return fewer_words
    else:
        return fewer_words.sample(n=int(params['number_to_ask']))


def check_word(direction):
    """Check if the value entered was correct
    Args:
        direction: asking a German word to English, or the inverse.
    """
    if direction == 'German':
        if st.session_state.my_answer.lower().strip() == st.session_state.correct_answer.lower():
            return True
        else:
            return False


def set_other_direction(direction):
    """Sets the inverse direction (English to German or German to English)

    Args:
        direction (String): Asking a German -> English or Enlgish -> German

    Returns:
        string: Returns the opposite of direction
    """
    if direction is DIRECTION_ENGLISH:
        return DIRECTION_GERMAN
    else:
        return DIRECTION_ENGLISH


def set_params(number_to_ask,
               correct_count,
               percent_correct,
               current_user,
              ):
    """Sets the parameters for what words to ask

    Args:
        number_to_ask (int): number of words to ask
        correct_count (int): number of time correct threashold
        percent_correct (float): percent correct threashold
    """
    clear_values()
    return {'number_to_ask': number_to_ask,
            'correct_count': correct_count,
            'percent_correct': percent_correct,
            'current_user': current_user,
    }


def set_word_line_values(direction, other_direction):
    """Once a subset of words are selected based on the parameters,
    This selects a word from the sample/subset and assigns the entire
    row of data from the dataframe Example:
    he must	11	37	69.69	er muss	4	6	66.66
    Args:
        direction (string): English -> German or German -> English
        other_direction (string): opposite of above
    """
    # take a sample of the samle date (get a random row)
    st.session_state.word_line = st.session_state.sample.sample()

    # set the word to be asked
    st.session_state.word = st.session_state.word_line[f'{direction} Word'].values[0]

    # set the correct answer
    st.session_state.correct_answer = st.session_state.word_line[
        f'{other_direction} Word'].values[0]

def update_correct_word(direction, from_word, df):
    """updates when a word is correct
    Args:
        direction (string): Same as all the others of this
        from_word (string): word that user tried to translate
        df (Datframe): Dataframe containing the sample flashcard data.
            ie, what needs to be updated.
    """

    # get the current number of times user has answered correctly
    correct_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count']

    # get the current number of times the user has been asked this word
    call_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count']

    correct_count += 1
    call_count += 1
    correct_percent = correct_count/call_count * 100

    # update sample dataframe with new counts and percent correct
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count'] = call_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count'] = correct_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Percent Correct'] = correct_percent


def update_incorrect_word(direction, from_word, df):
    """updates when a word is incorrect
    Args:
        direction (string): Same as all the others of this
        from_word (string): word that user tried to translate
        df (Datframe): Dataframe containing the sample flashcard data.
            ie, what needs to be updated.
    """

    # get the current number of times user has answered correctly
    correct_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count']

    # get the current number of times the user has been asked this word
    call_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count']

    call_count += 1
    correct_percent = correct_count/call_count * 100

    # update sample dataframe with new counts and percent correct
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count'] = call_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Percent Correct'] = correct_percent


def merge_dataframes(old_df, new_df):
    """Merges the new and old dataframe, overwriting the old with the new

    Args:
        new_df (Dataframe): The sample dataframe that was temporarily holding the
                            updated values of correct/incorrect
        old_df (Dateframe): The main dataframe of vocab words
                            that new_df will be merged into
    """
    # merge the sample dataframe into the main dataframe
    old_df.update(new_df)


def write_df_to_google_drive(dataframe,
                             user='Guest'):
    """writes a dataframe to Google Drive
    """
    sheet_name = get_flashcard_worksheet_by_user(user)
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(
        worksheet=sheet_name,
        data=dataframe
    )

def write_df_to_csv(dataframe,
                    filepath=SAMPLE_CSV,
                    ):
    """writes a dataframe to csv

    Args:
        dataframe (dataframe): dataframe you want to write to csv
        filename (output filename, optional): output filename csv to write dataframe to.
        Defaults to LORIS_FLASHCARDS_CSV.
    """
    dataframe.to_csv(filepath, index=False, header=True)


def remove_word(direction):
    """remove words from the sample. Once all the words are gone,
    user is done with the session

    Args:
        direction (string): uhg. Again? I need to make this a session state
    """
    st.session_state.sample = st.session_state.sample.drop(
        st.session_state.sample[
            st.session_state.sample[f'{direction} Word'] == st.session_state.word].index)

def clear_values(exception_list=None):
    """clear the values so starting fresh doesn't
    have session states messing up if statements
    """
    values = ['word_line', 'word', 'correct_answer', 'sample', 'show_form']

    # create a filtered list that doesn't delete certain values
    if exception_list:
        filtered_list = [item for item in values if item not in exception_list]
    else:
        filtered_list = values

    for val in filtered_list:
        if val in st.session_state:
            del st.session_state[val]


def enable_yes_no():
    """Enable any buttons with the session state of 'disabled' (yes and no)
    """
    if 'disabled' in st.session_state and st.session_state.disabled is False:
        st.session_state.disabled = True

def disable_yes_no():
    """disable any buttons with the session state of 'disabled' (yes and no)
    """
    if 'disabled' in st.session_state and st.session_state.disabled is True:
        st.session_state.disabled = False


def enable_buttons():
    """Enable any buttons with the session state of 'disabled' (yes and no)
    """
    st.session_state.yes_no_disabled = False

def disable_buttons():
    """Disable any buttons with the session state of 'disabled' (yes and no)
    enables submit button. I don't like this but it works and buttons are HARD
    """
    st.session_state.yes_no_disabled = True
    st.session_state.submit_button_disabled = False


def switch_buttons():
    """switches the yes/no and the submit buttons state from
    enabled (clickable) to disablee (not clickable.)
    """
    st.session_state.yes_no_disabled = not st.session_state.yes_no_disabled
    st.session_state.submit_button_disabled = not st.session_state.yes_no_disabled

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)
    st.button("Continue as Guest", on_click=set_current_user, args=("Guest",))

# def set_login_state():
#     print("loggin in")
#     print(f"=========={st.user.name}")
#     # st.session_state.current_user = st.user.name
#     # print(f"set current user to {st.session_state.current_user}")
#     # st.logout()

def set_current_user(user='Guest'):
    st.session_state.current_user = user


def set_page_config():
    st.set_page_config(page_title='Flashcards',
                       layout='wide',
                    )

    if 'flashcards_df' not in st.session_state:
        st.session_state.flashcards_df = get_flashcard_dataframe(user=st.session_state.current_user)

    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'Guest'

    review_tab, view_tab = st.tabs(['Review', 'Modify/View'])
    with review_tab:
        with st.form('vocab_list_form'):
            parameters_container = st.container()
            # current_user = parameters_container.selectbox(label='Current User',
            #                                               options=('Lori', 'Jonathan', 'Kerry', 'Guest'),
            #                                             )
            number_to_ask = parameters_container.text_input(label='Number of words to ask',
                                                            value=10,
                                                            help=('This is the number of words '
                                                                'that will be asked in this session'))
            correct_count = parameters_container.text_input(label='Only show if correct less than:',
                                                            value=10,
                                                            help=('I\'ll only show words that have been called '
                                                                'less than this number of times AND are right less than '
                                                                'the below percentage'
                                                                '  \nExample: 10, 70% --> all words that have only been asked'
                                                                '10 or fewer times and were correct 70% of the time'))
            percent_correct = parameters_container.text_input(label='% right less than',
                                                            value=100,
                                                            help=('I\'ll only show words that have been called '
                                                                    'less than above number of times AND are right less than '
                                                                    'this percentage'
                                                                    '  \nExample: 10, 70% --> all words that have only been asked'
                                                                    '10 or fewer times and were correct 70% of the time'))

            update_parameters = st.form_submit_button('Set Parameters')

        if 'parameters' not in st.session_state:
            st.session_state.parameters = set_params(
                number_to_ask=number_to_ask,
                correct_count=correct_count,
                percent_correct=percent_correct,
                current_user=st.session_state.current_user
                )
        if update_parameters:
            st.session_state.flashcards_df = get_flashcard_dataframe(user=st.session_state.current_user)
            st.session_state.parameters = set_params(
                number_to_ask=number_to_ask,
                correct_count=correct_count,
                percent_correct=percent_correct,
                current_user=st.session_state.current_user
                )

        german_to_english_tab, english_to_german_tab = st.tabs(['Translate German to English',
                                                                'Translate English to German'])
        with german_to_english_tab:
            with st.form('German to English', clear_on_submit=True):
                st.session_state.my_answer = st.text_input(label='Type Answer Here:')
                submit = st.form_submit_button('Run German to English')
                if submit:
                    if 'show_form' in st.session_state:
                        st.session_state.show_form = False
                    # get a subset of words based on the parameters
                    if 'sample' not in st.session_state:
                        try:
                            rerun_list = st.session_state.results_df[st.session_state.results_df['Run Again']=='True']
                        except AttributeError:
                            rerun_list = []
                        if ('run_results_again' in st.session_state
                            and st.session_state.run_results_again
                            and not rerun_list.empty):
                            st.session_state.sample = rerun_list
                            del st.session_state['run_results_again']
                        else:
                            st.session_state.sample = get_vocab_sample(st.session_state.parameters,
                                                                       direction=DIRECTION_GERMAN
                                                                        )
                        # code removes word from sample as user gets it right.
                        # code updates sample_copy with correct counts, then merges
                        # that into the original dataframe
                        st.session_state.sample_copy = st.session_state.sample

                    # set word to ask and display
                    if 'word' not in st.session_state:
                        if len(st.session_state.sample)>0:
                            # get the row from the sample
                            # set the 'word' and the 'answer'
                            set_word_line_values(direction=DIRECTION_GERMAN,
                                                other_direction=set_other_direction(DIRECTION_GERMAN))
                            st.markdown(f'# {st.session_state.word}')
                        else:
                            st.markdown('Parameters are too strict, no words in sample size')

                    # if 'word' is in session state, then check if the answer is correct
                    else:
                        if check_word(DIRECTION_GERMAN) is True:
                            update_correct_word(direction=DIRECTION_GERMAN,
                                                from_word=st.session_state.word,
                                                df=st.session_state.sample_copy)
                            remove_word(direction=DIRECTION_GERMAN)

                            # if user hasn't gotten them all correct, set a new word
                            # from the sample
                            if len(st.session_state.sample) > 0:
                                set_word_line_values(direction=DIRECTION_GERMAN,
                                                    other_direction=set_other_direction(DIRECTION_GERMAN))
                                st.markdown(f'# {st.session_state.word}')
                            else:
                                st.markdown('# You got them all correct. '
                                            'Hit "Show Selection" to get a new selection of words')

                                # merge the updated correct counts with
                                # original data
                                merge_dataframes(old_df=st.session_state.flashcards_df,
                                                 new_df=st.session_state.sample_copy)

                                if st.session_state.local_dev:
                                    write_df_to_csv(dataframe=st.session_state.flashcards_df)
                                elif st.session_state.current_user == 'Guest':
                                    st.markdown('# Guest user, no data saved')
                                else:
                                    write_df_to_google_drive(dataframe=st.session_state.flashcards_df,
                                                             user=st.session_state.current_user)
                                st.session_state.show_form = True

                                clear_values(['show_form'])
                        else:
                            st.markdown('# Incorrect. The correct '
                                        f' answer for :blue[{st.session_state.word}] is '
                                        f':green[{st.session_state.correct_answer}] '
                                        f'your answer: :red[{st.session_state.my_answer}]')
                            update_incorrect_word(direction=DIRECTION_GERMAN,
                                                from_word=st.session_state.word,
                                                df=st.session_state.sample_copy)
                            del st.session_state['word']
                            st.session_state.show_form = False
            if 'show_form' in st.session_state and st.session_state.show_form:
                with st.form('random form', clear_on_submit=True):
                    if 'sample_copy' in st.session_state:
                        st.markdown('# Summary:')
                        view_flashcard_table(
                                        st.session_state.sample_copy)
                    run_again_button = st.form_submit_button('Click here to Run Selected words Again')
                    if run_again_button:
                        st.session_state.run_results_again = True
                        st.session_state.show_form = False
                        clear_values()

        with english_to_german_tab:
            with st.form('English to German'):
                if 'submit_button_disabled' not in st.session_state:
                    st.session_state.submit_button_disabled = False
                submit_english_to_german = st.form_submit_button(label='Run English to German/Show Answer',
                                                                disabled=st.session_state.submit_button_disabled)

                # make sure yes/no buttons disabled until ready
                if 'yes_no_disabled' not in st.session_state:
                    st.session_state.yes_no_disabled = True

                yes_col, no_col = st.columns([.05, .95])
                with yes_col:
                    st.session_state.yes_button = st.form_submit_button(label='Yes',
                                                                        disabled=st.session_state.yes_no_disabled)
                with no_col:
                    # I think there's a bug in streamlit (14 jan 2025), can only have
                    # one 'on click' and it has to be the second button.
                    st.session_state.no_button = st.form_submit_button(label='No',
                                                                    disabled=st.session_state.yes_no_disabled,
                                                                    on_click=disable_buttons())
                if submit_english_to_german:
                    if 'show_form' in st.session_state:
                        st.session_state.show_form = False
                    # get a subset of words based on the parameters
                    if 'sample' not in st.session_state:
                        try:
                            rerun_list = st.session_state.results_df[st.session_state.results_df['Run Again']=='True']
                        except AttributeError:
                            rerun_list = []
                        if ('run_results_again' in st.session_state
                            and st.session_state.run_results_again
                            and not rerun_list.empty):
                            st.session_state.sample = rerun_list
                            del st.session_state['run_results_again']
                        else:
                            st.session_state.sample = get_vocab_sample(st.session_state.parameters,
                                                                    direction = DIRECTION_ENGLISH
                                                                    )

                        # code removes word from sample as user gets it right.
                        # code updates sample_copy with correct counts, then merges
                        # that into the original dataframe
                        st.session_state.sample_copy = st.session_state.sample

                        # this happens on next page refresh (like pressing a button)
                        # enable yes/no buttons and disable run.
                        switch_buttons()

                    # set word to ask and display
                    if 'word' in st.session_state:
                        st.markdown(f'# :blue[{st.session_state.word}] is '
                                    f':green[{st.session_state.correct_answer}] in Geramn'
                                    '\n Did you get it right?')
                    else:
                        if len(st.session_state.sample)>0:
                            # get the row from the sample
                            # set the 'word' and the 'answer'
                            set_word_line_values(direction=DIRECTION_ENGLISH,
                                                other_direction=set_other_direction(DIRECTION_ENGLISH))
                            st.markdown(f'# {st.session_state.word}')
                        else:
                            st.markdown('Parameters are too strict, no words in sample size')

                if st.session_state.yes_button:
                    # This executes for the next button pressed,
                    # which should only ever be 'Run English to German/Show Answer'
                    switch_buttons()
                    update_correct_word(direction=DIRECTION_ENGLISH,
                                        from_word=st.session_state.word,
                                        df=st.session_state.sample_copy)
                    remove_word(direction=DIRECTION_ENGLISH)
                    if len(st.session_state.sample) > 0:
                        set_word_line_values(direction=DIRECTION_ENGLISH,
                                            other_direction=set_other_direction(DIRECTION_ENGLISH))
                        st.markdown(f'# {st.session_state.word}')
                        st.session_state.show_form = False
                    else:
                        st.markdown('# You got them all correct. '
                                    'Hit "Show Selection" to get a new selection of words')

                        # merge the updated correct counts with
                        # original data
                        merge_dataframes(old_df=st.session_state.flashcards_df,
                                        new_df=st.session_state.sample_copy)
                        if st.session_state.local_dev:
                            write_df_to_csv(dataframe=st.session_state.flashcards_df)
                        elif st.session_state.current_user == 'Guest':
                            st.markdown('# Guest user, no data saved')
                        else:
                            write_df_to_google_drive(dataframe=st.session_state.flashcards_df,
                                                     user=st.session_state.current_user)


                        st.session_state.show_form = True

                        clear_values(['show_form'])
                        del st.session_state.submit_button_disabled
                        del st.session_state.yes_no_disabled

                if st.session_state.no_button:
                    # This executes for the next button pressed,
                    # which should only ever be 'Run English to German/Show Answer'
                    switch_buttons()
                    update_incorrect_word(direction=DIRECTION_ENGLISH,
                                        from_word=st.session_state.word,
                                        df=st.session_state.sample_copy)
                    set_word_line_values(direction=DIRECTION_ENGLISH,
                                        other_direction=set_other_direction(DIRECTION_ENGLISH))
                    st.markdown(f'# {st.session_state.word}')
                    st.session_state.show_form = False
            if 'show_form' in st.session_state and st.session_state.show_form:
                with st.form('random form e2g', clear_on_submit=True):
                    if 'sample_copy' in st.session_state:
                        st.markdown('# Summary:')
                        view_flashcard_table(
                                        st.session_state.sample_copy)
                    run_again_button = st.form_submit_button('Click here to Run Selected words Again')
                    if run_again_button:
                        st.session_state.run_results_again = True
                        st.session_state.show_form = False
                        clear_values()


    with view_tab:
        with st.form(key='Pull in Data from Google Sheets'):
            st.markdown(f'# Currently Viewing :red[{st.session_state.current_user}\'s] Data')
            clear_cache_and_sync = st.form_submit_button(label='Sync with Google Sheets')

            if clear_cache_and_sync:
                st.cache_data.clear()
                st.session_state.flashcards_df = get_flashcard_dataframe(st.session_state.current_user)
        with st.expander('Filter Data'):
            min_value = 0
            max_value = 100

            english_min_correct, english_max_correct = st.slider(
            'English Min and Max Correct Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

            english_min_call, english_max_call = st.slider(
            'English Min and Max Call Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

            english_min_percent, english_max_percent = st.slider(
            'English Min and Max Percent Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

            german_min_correct, german_max_correct = st.slider(
            'German Min and Max Correct Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

            german_min_call, german_max_call = st.slider(
            'German Min and Max Call Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

            german_min_percent, german_max_percent = st.slider(
            'German Min and Max Percent Count to Display',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])


        view_flashcard_data_editor(flashcards_df=st.session_state.flashcards_df,
                                english_min_correct=english_min_correct,
                                english_max_correct=english_max_correct,
                                german_min_correct=german_min_correct,
                                german_max_correct=german_max_correct,
                                english_min_call=english_min_call,
                                english_max_call=english_max_call,
                                german_min_call=german_min_call,
                                german_max_call=german_max_call,
                                english_min_percent=english_min_percent,
                                english_max_percent=english_max_percent,
                                german_min_percent=german_min_percent,
                                german_max_percent=german_max_percent,
                                )

