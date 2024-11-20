import os

import pandas
import streamlit as st

LORIS_FLASHCARDS_CSV = 'Flashcards_lori.csv'
COLUMNS_AND_TYPES = {'English Word': str,
                    'English Correct Count': 'Int64',
                    'English Call Count': 'Int64',
                    'English Percent Correct': float,
                    'German Word': str,
                    'German Correct Count': 'Int64',
                    'German Call Count': 'Int64',
                    'German Percent Correct': float}
DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'


def load_flashcard_data(flashcard_path=LORIS_FLASHCARDS_CSV):
    """Read in the default csv. Unless it's not there.

    Returns:
        dataframe: the pandas dataframe of the csv. otherwise None
    """
    if os.path.exists(flashcard_path):
        flashcards_df = pandas.read_csv(
            flashcard_path,
            names=COLUMNS_AND_TYPES.keys(),
            dtype=COLUMNS_AND_TYPES,
        ).fillna(0)
        return flashcards_df

def view_flashcard_data(flashcards_df):
    """_summary_
    """
    if not flashcards_df.empty:
        st.data_editor(
            flashcards_df,
            use_container_width=True,
            num_rows='dynamic'
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
        number_to_ask (int): _description_
        percent_corret (float): _description_
        correct_count (int): _description_
    """
    all_words = st.session_state.flashcards_df
    fewer_words = all_words[(all_words[f'{direction} Correct Count'] <= int(correct_count)) & (all_words[f'{direction} Percent Correct'] <= float(percent_correct))]
    sample = fewer_words.sample(n=int(number_to_ask))
    return sample

def check_word(direction):
    """Check if the value entered was correct
    """
    if direction == 'German':
        if st.session_state.my_answer.lower() == st.session_state.correct_answer.lower():
            return True
        else:
            return False


def set_other_direction(direction):
    if direction is DIRECTION_ENGLISH:
        return DIRECTION_GERMAN
    else:
        return DIRECTION_ENGLISH


def set_params(number_to_ask,
                   correct_count,
                   percent_correct,
                   ):
    """_summary_

    Args:
        number_to_ask (_type_): _description_
        correct_count (_type_): _description_
        percent_correct (_type_): _description_
        direction (_type_): _description_
        other_direction (_type_): _description_
    """
    return {'number_to_ask': number_to_ask,
            'correct_count': correct_count,
            'percent_correct': percent_correct,
    }


def set_word_line_values(direction, other_direction):
    """_summary_

    Args:
        direction (_type_): _description_
        other_direction (_type_): _description_
    """
    st.session_state.word_line = st.session_state.sample.sample()
    st.session_state.word = st.session_state.word_line[f'{direction} Word'].values[0]
    st.session_state.correct_answer = st.session_state.word_line[f'{other_direction} Word'].values[0]


def remove_word(direction):
    """remove words from the sample

    Args:
        direction (_type_): _description_
    """
    st.session_state.sample = st.session_state.sample.drop(st.session_state.sample[st.session_state.sample[f'{direction} Word'] == st.session_state.word].index)

def clear_values():
    """clear the values so starting fresh doesn't have session states messing up if statements
    """
    values = ['word_line', 'word', 'correct_answer', 'sample']

    for val in values:
        if val in st.session_state:
            del st.session_state[val]

def run_english_to_german():
    """_summary_
    """
    if 'word' not in st.session_state:
            # get the row from the sample
            # set the "word" and the "answer"
        if len(st.session_state.sample) > 0:
            set_word_line_values(direction='English', other_direction='German')
            disable_yes_no()
            st.markdown(f'# {st.session_state.word}')
        else:
            st.markdown('# You got them all correct. Hit '
                        '"Show Selection" to get a new selection of words')
            clear_values()
    else:
        st.markdown('# The correct '
                    f' answer for :blue[{st.session_state.word}] is '
                    f':green[{st.session_state.correct_answer}] '
                    'Did you get it right?')
        enable_yes_no()
        # del st.session_state['word']

def enable_yes_no():
    """enable the button. This is backwards and I don't know why
    """
    if "disabled" in st.session_state and st.session_state.disabled == False:
        st.session_state.disabled = True

def disable_yes_no():
    """Set the enable button to "False". This works backwards and I don't know why
    """
    if "disabled" in st.session_state and st.session_state.disabled == True:
        st.session_state.disabled = False

