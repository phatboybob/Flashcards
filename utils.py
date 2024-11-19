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

def check_word():
    """Check if the value entered was correct
    """
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
                   direction,
                   other_direction):
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
            'direction': direction,
            'other_direction': other_direction}

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
    del st.session_state.word_line
    del st.session_state.word
    del st.session_state.correct_answer