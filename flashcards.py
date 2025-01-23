'''
Flashcards App Created (for now) to run English to German or German to English
translations.

Created by Lori Jackson January 2025
'''

import streamlit as st

from utils import (
                    get_flashcard_dataframe,
                    view_flashcard_data_editor,
                    view_flashcard_table,
                    get_vocab_sample,
                    set_other_direction,
                    set_params,
                    set_word_line_values,
                    check_word,
                    remove_word,
                    clear_values,
                    update_correct_word,
                    update_incorrect_word,
                    merge_dataframes,
                    disable_buttons,
                    switch_buttons,
                    write_df_to_csv,
                    get_flashcard_filepath_by_user,
                  )

DIRECTION_ENGLISH = 'English'
DIRECTION_GERMAN = 'German'
OTHER_DIRECTION = ''


st.set_page_config(page_title='Flashcards',
                   layout='wide',
                   )

if 'flashcards_df' not in st.session_state:
    st.session_state.flashcards_df = get_flashcard_dataframe()

if 'current_user' not in st.session_state:
    st.session_state.current_user = 'Lori'

# if 'flashcards_df' not in st.session_state:
#     flashcards_data = st.file_uploader('Choose your flashcards csv')
#     if flashcards_data is not None:
#         load_flashcard_data(flashcards_data)

review_tab, view_tab = st.tabs(['Review', 'Modify/View'])
with review_tab:
    with st.form('vocab_list_form'):
        parameters_container = st.container()
        current_user = parameters_container.selectbox(label='Current User',
                                                      options=('Lori', 'Jonathan', 'Sample'),
                                                      )
        number_to_ask = parameters_container.text_input(label='Number of words to ask',
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

        show_selection = st.form_submit_button('Set Parameters')

    if show_selection:
        if st.session_state.current_user is not current_user:
            file_path = get_flashcard_filepath_by_user(current_user)
            st.session_state.flashcards_df = get_flashcard_dataframe(flashcard_path=file_path)
            st.session_state.current_user = current_user
        params = set_params(number_to_ask=number_to_ask,
                            correct_count=correct_count,
                            percent_correct=percent_correct,
                            current_user=current_user
                            )

    german_to_english_tab, english_to_german_tab = st.tabs(['Translate German to English',
                                                            'Translate English to German'])
    with german_to_english_tab:
        with st.form('German to English', clear_on_submit=True):
            st.session_state.my_answer = st.text_input(label='Type Answer Here:')
            submit = st.form_submit_button('Run German to English')
            if submit:
                # get a subset of words based on the parameters
                if 'sample' not in st.session_state:
                    st.session_state.sample = get_vocab_sample(number_to_ask=number_to_ask,
                                                               percent_correct=percent_correct,
                                                               correct_count=correct_count,
                                                               direction = DIRECTION_GERMAN
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

                            # get filepath by user
                            filepath = get_flashcard_filepath_by_user(user=st.session_state.current_user)

                            # write that shit out
                            write_df_to_csv(filepath=filepath,
                                            dataframe=st.session_state.flashcards_df)
                            st.markdown('# Summary: \n '
                                        f'{view_flashcard_table(
                                            st.session_state.sample_copy)}')

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

                # get a subset of words based on the parameters
                if 'sample' not in st.session_state:
                    st.session_state.sample = get_vocab_sample(number_to_ask=number_to_ask,
                                                               percent_correct=percent_correct,
                                                               correct_count=correct_count,
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
                else:
                    st.markdown('# You got them all correct. '
                                'Hit "Show Selection" to get a new selection of words')

                    # merge the updated correct counts with
                    # original data
                    merge_dataframes(old_df=st.session_state.flashcards_df,
                                     new_df=st.session_state.sample_copy)

                    # get filepath by user
                    filepath = get_flashcard_filepath_by_user(user=st.session_state.current_user)

                    #write that shit out
                    write_df_to_csv(filepath=filepath,
                                    dataframe=st.session_state.flashcards_df)
                    st.markdown('# Summary: \n '
                                f'{view_flashcard_table(
                                    st.session_state.sample_copy)}')

                    clear_values()
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


with view_tab:
    with st.form(key='save to file'):
        st.markdown(f'# Currently Viewing :red[{st.session_state.current_user}\'s] Data')
        save_to_csv = st.form_submit_button(label='Save')
        uploaded_csv = st.file_uploader(label='Choose your flashcards file '
                                              'and the press the "Upload" button',
                                        type='csv')
        upload = st.form_submit_button(label='Upload')
        if save_to_csv:
            write_df_to_csv(dataframe=st.session_state.flashcards_df,
                            )
        if upload and uploaded_csv is not None:
            st.session_state.flashcards_df = get_flashcard_dataframe(uploaded_csv)

    view_flashcard_data_editor(flashcards_df=st.session_state.flashcards_df,
                               )
