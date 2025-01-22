"""
Utilities for the Streamlit German Flashcards app
Created by Lori Jackson January 2025
"""

import pandas
import streamlit as st

LORIS_FLASHCARDS_CSV = 'Flashcards_lori.csv'
JONATHAN_FLASHCARDS_CSV = 'jonathan_data.csv'
# LORIS_FLASHCARDS_CSV = 'sample.csv'
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

def get_flashcard_filepath_by_user(user='Lori'):
    """Read in the default csv. Unless it's not there.

    Returns:
        dataframe: the pandas dataframe of the csv. otherwise None
    """
    match user:
        case 'Lori':
            flashcard_path = LORIS_FLASHCARDS_CSV
        case 'Jonathan':
            flashcard_path = JONATHAN_FLASHCARDS_CSV
        case 'Sample':
            flashcard_path = 'sample.csv'
        case _:
            flashcard_path = 'sample.csv'
    return flashcard_path


def get_flashcard_dataframe(flashcard_path=LORIS_FLASHCARDS_CSV):
    """Uploads a csv and returns it as a dataframe

    Args:
        flashcard_path (path, optional): path to a csv. Defaults to LORIS_FLASHCARDS_CSV.

    Returns:
        dataframe: dataframe conversion of the csv
    """
    flashcards_df = pandas.read_csv(
        flashcard_path,
        names=COLUMNS_AND_TYPES.keys(),
        dtype=COLUMNS_AND_TYPES,
        header=None,
        skiprows=1
    ).fillna(0)
    return flashcards_df


def view_flashcard_data_editor(flashcards_df):
    """displays everything in the review panel
    """
    if not flashcards_df.empty:
        st.session_state.flashcards_df = st.data_editor(
                                                        data=flashcards_df,
                                                        use_container_width=False,
                                                        num_rows='dynamic',
                                                        column_config=COLUM_CONFIG,
                                                        )
    else:
        st.write("Please Upload Data")


def view_flashcard_table(flashcards_df):
    """prints out the summary table after getting all words correct
    """
    if not flashcards_df.empty:
        st.table(
            flashcards_df,
        )
    else:
        st.write("please upload data")


def get_vocab_sample(number_to_ask,
                     percent_correct,
                     correct_count,
                     direction,
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
    fewer_words = all_words[(all_words[f'{direction} Correct Count'] <= int(correct_count))
                            & (all_words[f'{direction} Percent Correct'] <= float(percent_correct))]

    # subset of qualifying words
    # subset may be less than the number to ask, leading to out of bounds error
    if len(fewer_words) <= int(number_to_ask):
        return fewer_words
    else:
        return fewer_words.sample(n=int(number_to_ask))


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


def write_df_to_csv(dataframe,
                    filepath=LORIS_FLASHCARDS_CSV,
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

def clear_values():
    """clear the values so starting fresh doesn't
    have session states messing up if statements
    """
    values = ['word_line', 'word', 'correct_answer', 'sample']

    for val in values:
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

