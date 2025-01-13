import os

import pandas
import streamlit as st

# LORIS_FLASHCARDS_CSV = 'Flashcards_lori.csv'
LORIS_FLASHCARDS_CSV = 'sample.csv'
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

def view_flashcard_data_editor(flashcards_df):
    """_summary_
    """
    if not flashcards_df.empty:
        st.data_editor(
            flashcards_df,
            use_container_width=False,
            num_rows='dynamic',
        )
    else:
        st.write("please upload data")


def view_flashcard_table(flashcards_df):
    """_summary_
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
        number_to_ask (int): _description_
        percent_corret (float): _description_
        correct_count (int): _description_
    """
    # entire dataframe
    all_words = st.session_state.flashcards_df

    # all words that fit the ask count and percent cuttoff
    fewer_words = all_words[(all_words[f'{direction} Correct Count'] <= int(correct_count)) & (all_words[f'{direction} Percent Correct'] <= float(percent_correct))]

    # subset of qualifying words
    if len(fewer_words) <= int(number_to_ask):
        return fewer_words
    else:
        return fewer_words.sample(n=int(number_to_ask))

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
    clear_values()
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

def update_correct_word(direction, from_word, df):
    """updates when a word is correct"""
    correct_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count']
    call_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count']

    correct_count += 1
    call_count += 1
    correct_percent = correct_count/call_count

    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count'] = call_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count'] = correct_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Percent Correct'] = correct_percent


def update_incorrect_word(direction, from_word, df):
    """updates when a word is incorrect"""
    correct_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count']
    call_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count']
    print(f'{from_word}: Before correct count: {correct_count.to_string(index=False)}, call count: {call_count.to_string(index=False)}')

    call_count += 1
    correct_percent = correct_count/call_count

    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count'] = call_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Percent Correct'] = correct_percent
    print(f'{from_word} After: correct count: {correct_count.to_string(index=False)}, call count: {call_count.to_string(index=False)}, correct_percent: {correct_percent.to_string(index=False)}')


def merge_and_print_dataframes(old_df, new_df):
    """Merges the new and old dataframe, overwriting the old with the new

    Args:
        new_df (_type_): _description_
        old_df (_type_): _description_
    """
    old_df.update(new_df)
    old_df.to_csv(LORIS_FLASHCARDS_CSV, index=False, header=False)

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
            st.markdown(f'# {st.session_state.word}')
            st.markdown(f'the sample data is: {st.session_state.sample}')

        else:
            st.markdown('# You got them all correct. Hit '
                        '"Show Selection" to get a new selection of words'
                        f'the sample data is: {st.session_state.sample}')
            print(f'the selection is {st.session_state.sample}')

            clear_values()
    else:
        st.markdown('# The correct '
                    f' answer for :blue[{st.session_state.word}] is '
                    f':green[{st.session_state.correct_answer}] '
                    'Did you get it right?')

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


def enable_buttons():
    """Enables the yes_no buttons"""
    print('method call set it to enabled')
    st.session_state.yes_no_disabled = False

def disable_buttons():
    """Disabled the yes_no buttons"""
    st.session_state.yes_no_disabled = True

