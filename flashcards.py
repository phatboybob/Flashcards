import streamlit as st

from utils import (
                    load_flashcard_data,
                    view_flashcard_data,
                    get_vocab_sample,
                    set_other_direction,
                    set_params,
                    set_word_line_values,
                    check_word,
                    remove_word,
                    clear_values,
                  )

DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'
OTHER_DIRECTION = ''

st.set_page_config(page_title="Flashcards")



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
                                                        value=20,
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
        direction = parameters_container.selectbox('Translate Diretion',
                                                    [DIRECTION_GERMAN,
                                                    DIRECTION_ENGLISH])
        other_direction = set_other_direction(direction=direction)

        show_selection = st.form_submit_button('Show selection')
    if show_selection:
        params = set_params(number_to_ask=number_to_ask,
                   correct_count=correct_count,
                   percent_correct=percent_correct,
                   direction=direction,
                   other_direction=other_direction)
        st.session_state.sample = sample = get_vocab_sample(number_to_ask=number_to_ask,
                            percent_correct=percent_correct,
                            correct_count=correct_count,
                            direction=direction)


    with st.form('question section', clear_on_submit=True):
        st.session_state.my_answer = st.text_input(label="Type Answer Here:")

        submit = st.form_submit_button('Run')

    if submit:
        if 'word' not in st.session_state:
            # get the row from the sample
            # set the "word" and the "answer"
            set_word_line_values(direction=direction, other_direction=other_direction)
            st.markdown(f'# {st.session_state.word}')
        else:
            if check_word() is True:
                remove_word(direction=direction)
                if len(st.session_state.sample) > 0:
                    set_word_line_values(direction=direction, other_direction=other_direction)
                    st.markdown(f'# {st.session_state.word}')
                else:
                    st.markdown('# You got them all correct. Hit "Show Selection" to get a new selection of words')
                    clear_values()
            else:
                st.markdown('# Incorrect. The correct '
                         f' answer for :blue[{st.session_state.word}] is '
                         f':green[{st.session_state.correct_answer}] '
                         f'your answer: :red[{st.session_state.my_answer}]')
                del st.session_state['word']

with view_tab:
    view_flashcard_data(st.session_state.flashcards_df)
