import streamlit as st
import pandas

from utils import (
                    load_flashcard_data,
                    view_flashcard_data_editor,
                    view_flashcard_table,
                    get_vocab_sample,
                    set_other_direction,
                    set_params,
                    set_word_line_values,
                    check_word,
                    remove_word,
                    clear_values,
                    run_english_to_german,
                    update_correct_word,
                    update_incorrect_word,
                    merge_and_print_dataframes,
                  )

DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'
OTHER_DIRECTION = ''

if "disabled" not in st.session_state:
    st.session_state.disabled = True

st.set_page_config(page_title="Flashcards",
                   layout="wide",
                   )



st.session_state.flashcards_df = load_flashcard_data()

if "flashcards_df" not in st.session_state:
    flashcards_data = st.file_uploader("Choose your flashcards csv")
    if flashcards_data is not None:
        load_flashcard_data(flashcards_data)

review_tab, view_tab = st.tabs(['Review', 'Modify/View'])
with review_tab:
    with st.form('vocab_list_form'):
        parameters_container = st.container()
        number_to_ask = parameters_container.text_input(label="Number of words to ask",
                                                        value=5,
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
        # direction = parameters_container.selectbox('Translate Diretion',
        #                                             [DIRECTION_GERMAN,
        #                                             DIRECTION_ENGLISH])
        # other_direction = set_other_direction(direction=direction)

        show_selection = st.form_submit_button('Set Parameters')
    if show_selection:
        params = set_params(number_to_ask=number_to_ask,
                            correct_count=correct_count,
                            percent_correct=percent_correct,
                            )



    german_to_english_tab, english_to_german_tab = st.tabs(['Translate German to English',
                                                            'Translate English to German'])
    with english_to_german_tab:

        with st.form('English to German'):
            submit_english = st.form_submit_button('Run English to German')

            yes_col, no_col = st.columns(2)
            with yes_col:
                st.session_state.yes_button = st.form_submit_button(label='Yes', disabled=st.session_state.disabled)
            with no_col:
                st.session_state.no_button = st.form_submit_button(label='No', disabled=st.session_state.disabled)


            if submit_english:
                if 'sample' not in st.session_state:
                    st.session_state.sample = get_vocab_sample(number_to_ask=number_to_ask,
                    percent_correct=percent_correct,
                    correct_count=correct_count,
                    direction = DIRECTION_GERMAN
                    )
                run_english_to_german()
            if st.session_state.no_button:
                st.session_state_correct = False
                del st.session_state['word']
                run_english_to_german()
            if st.session_state.yes_button:
                if len(st.session_state.sample) > 0:
                    remove_word(direction=DIRECTION_ENGLISH)
                    del st.session_state['word']
                run_english_to_german()

    with german_to_english_tab:
        with st.form('German to English', clear_on_submit=True):
            st.session_state.my_answer = st.text_input(label="Type Answer Here:")
            submit = st.form_submit_button('Run German to English')
            if submit:
                if 'sample' not in st.session_state:
                    st.session_state.sample = get_vocab_sample(number_to_ask=number_to_ask,
                                                               percent_correct=percent_correct,
                                                               correct_count=correct_count,
                                                               direction = DIRECTION_GERMAN
                                                              )
                    st.session_state.sample_copy = st.session_state.sample
                if 'word' not in st.session_state:
                    if len(st.session_state.sample)>0:
                        # get the row from the sample
                        # set the "word" and the "answer"
                        set_word_line_values(direction=DIRECTION_GERMAN, other_direction=set_other_direction(DIRECTION_GERMAN))
                        st.markdown(f'# {st.session_state.word}')
                    else:
                        st.markdown('Parameters are too strict, no words in sample size')
                else:
                    if check_word(DIRECTION_GERMAN) is True:
                        update_correct_word(direction=DIRECTION_GERMAN, from_word=st.session_state.word, df=st.session_state.sample_copy)
                        remove_word(direction=DIRECTION_GERMAN)
                        if len(st.session_state.sample) > 0:
                            set_word_line_values(direction=DIRECTION_GERMAN, other_direction=set_other_direction(DIRECTION_GERMAN))
                            st.markdown(f'# {st.session_state.word}')
                        else:
                            st.markdown('# You got them all correct. Hit "Show Selection" to get a new selection of words')
                            merge_and_print_dataframes(st.session_state.flashcards_df, st.session_state.sample_copy)
                            st.markdown(f'# Summary: \n {view_flashcard_table(st.session_state.sample_copy)}')

                            clear_values()
                    else:
                        st.markdown('# Incorrect. The correct '
                                    f' answer for :blue[{st.session_state.word}] is '
                                    f':green[{st.session_state.correct_answer}] '
                                    f'your answer: :red[{st.session_state.my_answer}]')
                        update_incorrect_word(direction=DIRECTION_GERMAN,
                                              from_word=st.session_state.word,
                                              df=st.session_state.sample_copy)
                        del st.session_state['word']


with view_tab:
    view_flashcard_data_editor(st.session_state.flashcards_df)
