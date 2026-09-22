# import streamlit as st
# import pandas as pd
# import time
# import joblib
# from database import save_prediction
# from streamlit_extras.stylable_container import stylable_container

# model = joblib.load('model/TB_model_v1.pkl')



# def yes_no(question):
#     answer = st.selectbox(
#         question, 
#         options=['No','Yes'],
#             format_func=lambda x: x.title(),
#         index=None,
#         placeholder="select an option",
#     )
#     return 1 if answer == 'Yes' else 0

# def show_tb_page():

#     st.markdown(
#     '<div class="section-title">TB Prediction</div>',
#     unsafe_allow_html=True
#     )
#     st.title(':blue[Tuberculosis Prediction]' , text_alignment="center")
#     st.write("Fill in the questionnaire below.")


#     with stylable_container(
#     key="tb_card",
#     css_styles="""
#     {
#         background: rgba(8,12,28,0.92);

#         border-radius: 24px;

#         padding: 32px;

#         border: 1px solid rgba(120,119,198,0.18);

#         transition:
#             box-shadow 0.3s ease,
#             border-color 0.3s ease;
#     }

#     &:hover {

#         border-color: rgba(180,120,255,0.35);

#         box-shadow:
#             0 0 18px rgba(0,140,255,0.18),
#             0 0 40px rgba(162,0,255,0.22);
#     }
#     """
#     ):
       
#         col1, col2, col3 = st.columns(
#         [1,1,1],
#         gap="large"
#          )

#         with col1: 
#             fever = yes_no(
#                 'Have you had fever for more than 2 weeks '
#             )

#             cough_blood = yes_no(''
#             'Are you coughing blood'
#             )

#             night_sweat = yes_no(
#                 'Do you experience night sweats'
#             )

#             chest_pain = yes_no(
#             'Do you have a chest pain'
#             )
#         st.markdown("<br>", unsafe_allow_html=True)
#         with col2:
#             back_pain = yes_no(
#             'Do you have a back pain'
#             )

#             sputum = yes_no(
#             'Is your sputum or mucus mixed with blood'
#             )
        
#             breath_shortness = yes_no(
#             'Do you experience shortness of breath'
#             )

#             weight_loss = yes_no(
#             'Have you experience unexplained weight loss recently'
#             )
#         st.markdown("<br>", unsafe_allow_html=True)
#         with col3:
#             body_feel_tired = yes_no(
#             'Do you often feel unusually tired or weak'
#             )

#             lumps = yes_no(
#             'Have you noticed any lumps or swellimg on your body'
#             )

#             continuous_cough = yes_no(
#             'Have you had a continuous cough with phlegm'
#             )

#             swollen_lymph_nodes = yes_no(
#             'Do you have swollen lymph nodes'
#             )

#             loss_of_appetite = yes_no(
#                 'Have you experienced loss of appetite recently'
#             )

#     if st.button('Run Prediction'):

#         input_data = pd.DataFrame([{
#             'two_weeks_fever':fever,
#             'coughing_blood': cough_blood,
#             'sputum_mixed_with_blood': sputum,
#             'night_sweats': night_sweat,
#             'chest_pain': chest_pain,
#             'back_pain': chest_pain,
#             'breath_shortness': breath_shortness,
#             'weight_loss': weight_loss,
#             'body_feels_tired': body_feel_tired,
#             'lumps': lumps,
#             'continuous_cough_and_phlegm':continuous_cough,
#             'swollen_lymph_nodes': swollen_lymph_nodes,
#             'loss_of_appetite': loss_of_appetite
#         }])

#         with st.spinner('Analyxing patient data...'):
#             time.sleep(1.5)

#             pred = model.predict(input_data)[0]
#             prob = model.predict_proba(input_data)[0][1]

#             st.write("### Result")

#             if pred == 1:
#                 st.error(F'High Risk of TB ({round(prob*100,2)}%)')

#                 st.warning("""
#             Recommendation:
#             Please visit a healthcare center for proper
#             testing and medical consultation.
#             """)
#             else: 
#                 st.success(f'Low Risk of TB({round(prob*100, 2)}%)')
#                 st.info("""
#             Maintain healthy habits and regular medical
#             checkups.
#             """)
                
#         save_prediction(
#             user_email=st.session_state['user'].email,
#             disease='Tuberculosis',
#             input_data=input_data.to_dict(orient='records')[0],
#             prediction=int(pred),
#             probability=float(prob)
#         )




# import streamlit as st
# import pandas as pd
# import time
# import joblib
# from database import save_prediction
# from streamlit_extras.stylable_container import stylable_container

# model = joblib.load('model/TB_model_v1.pkl')


# def yes_no(question):
#     answer = st.selectbox(
#         question, 
#         options=['No', 'Yes'],
#         format_func=lambda x: x.title(),
#         index=None,
#         placeholder="select an option",
#     )
#     # CRITICAL FIX: Keep it as None if unanswered, otherwise convert to 1 or 0
#     if answer is None:
#         return None
#     return 1 if answer == 'Yes' else 0


# def show_tb_page():

#     st.markdown(
#         '<div class="section-title">TB Prediction</div>',
#         unsafe_allow_html=True
#     )
#     st.title(':blue[Tuberculosis Prediction]', text_alignment="center")
#     st.write("Fill in the questionnaire below.")

#     # We will store answers in a dictionary to easily validate them
#     answers = {}

#     with stylable_container(
#         key="tb_card",
#         css_styles="""
#         {
#             background: rgba(8,12,28,0.92);
#             border-radius: 24px;
#             padding: 32px;
#             border: 1px solid rgba(120,119,198,0.18);
#             transition:
#                 box-shadow 0.3s ease,
#                 border-color 0.3s ease;
#         }
#         &:hover {
#             border-color: rgba(180,120,255,0.35);
#             box-shadow:
#                 0 0 18px rgba(0,140,255,0.18),
#                 0 0 40px rgba(162,0,255,0.22);
#         }
#         """
#     ):
        
#         col1, col2, col3 = st.columns([1, 1, 1], gap="large")

#         with col1: 
#             answers['fever'] = yes_no('Have you had fever for more than 2 weeks ')
#             answers['cough_blood'] = yes_no('Are you coughing blood')
#             answers['night_sweat'] = yes_no('Do you experience night sweats')
#             answers['chest_pain'] = yes_no('Do you have a chest pain')
            
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         with col2:
#             # Note: Fixed a tiny typo from your original code where you mapped back_pain to chest_pain below
#             answers['back_pain'] = yes_no('Do you have a back pain')
#             answers['sputum'] = yes_no('Is your sputum or mucus mixed with blood')
#             answers['breath_shortness'] = yes_no('Do you experience shortness of breath')
#             answers['weight_loss'] = yes_no('Have you experience unexplained weight loss recently')
            
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         with col3:
#             answers['body_feel_tired'] = yes_no('Do you often feel unusually tired or weak')
#             answers['lumps'] = yes_no('Have you noticed any lumps or swellimg on your body')
#             answers['continuous_cough'] = yes_no('Have you had a continuous cough with phlegm')
#             answers['swollen_lymph_nodes'] = yes_no('Do you have swollen lymph nodes')
#             answers['loss_of_appetite'] = yes_no('Have you experienced loss of appetite recently')

#     # When they click the prediction button, check everything first!
#     if st.button('Run Prediction'):
        
#         # 1. Count how many fields are still None
#         unanswered_count = sum(1 for val in answers.values() if val is None)
        
#         if unanswered_count > 0:
#             st.error(f"⚠️ You have {unanswered_count} unanswered question(s). Please complete all fields before running the prediction.")
#         else:
#             # 2. If everything is filled, build the DataFrame using the dictionary values
#             input_data = pd.DataFrame([{
#                 'two_weeks_fever': answers['fever'],
#                 'coughing_blood': answers['cough_blood'],
#                 'sputum_mixed_with_blood': answers['sputum'],
#                 'night_sweats': answers['night_sweat'],
#                 'chest_pain': answers['chest_pain'],
#                 'back_pain': answers['back_pain'], 
#                 'breath_shortness': answers['breath_shortness'],
#                 'weight_loss': answers['weight_loss'],
#                 'body_feels_tired': answers['body_feel_tired'],
#                 'lumps': answers['lumps'],
#                 'continuous_cough_and_phlegm': answers['continuous_cough'],
#                 'swollen_lymph_nodes': answers['swollen_lymph_nodes'],
#                 'loss_of_appetite': answers['loss_of_appetite']
#             }])

#             with st.spinner('Analyzing patient data...'):
#                 time.sleep(1.5)

#                 pred = model.predict(input_data)[0]
#                 prob = model.predict_proba(input_data)[0][1]

#                 # Create side-by-side columns to bring the alert banner to the front
#                 res_col1, res_col2 = st.columns([1, 5])

#                 with res_col1:
#                     st.write("### Result:")

#                 with res_col2:
#                     if pred == 1:
#                         st.error(f'High Risk of TB ({round(prob*100,2)}%)')
#                     else: 
#                         st.success(f'Low Risk of TB ({round(prob*100, 2)}%)')

#                 # Recommendations sit cleanly below the header row
#                 if pred == 1:
#                     st.warning("""
#                     Recommendation:
#                     Please visit a healthcare center for proper
#                     testing and medical consultation.
#                     """)
#                 else:
#                     st.info("""
#                     Recommendation:
#                     Maintain healthy habits and regular medical
#                     checkups.
#                     """)
                    
                
        

#             # From your Gmail/Database setup
#             save_prediction(
#                 user_email=st.session_state['user'].email,
#                 disease='Tuberculosis',
#                 input_data=input_data.to_dict(orient='records')[0],
#                 prediction=int(pred),
#                 probability=float(prob)
#             )






import streamlit as st
import pandas as pd
import time
import joblib
from database import save_prediction
from streamlit_extras.stylable_container import stylable_container

model = joblib.load('model/TB_model_v1.pkl')


def yes_no(question):
    answer = st.selectbox(
        question, 
        options=['No', 'Yes'],
        format_func=lambda x: x.title(),
        index=None,
        placeholder="select an option",
    )
    # CRITICAL FIX: Keep it as None if unanswered, otherwise convert to 1 or 0
    if answer is None:
        return None
    return 1 if answer == 'Yes' else 0


def show_tb_page():

    # st.markdown(
    #     '<div class="section-title">TB Prediction</div>',
    #     unsafe_allow_html=True
    # )
    # st.title(':blue[Tuberculosis Prediction]', text_alignment="center")
    st.title(":color[Tuberculosis Prediction]{foreground='white'}", text_alignment="center")
    st.write("Fill in the questionnaire below.")

    # We will store answers in a dictionary to easily validate them
    answers = {}

    
    with stylable_container(
        key="tb_card",
        css_styles="""
        {
            background: rgba(8,12,28,0.92);
            border-radius: 24px;
            padding: 32px;
            border: 1px solid rgba(120,119,198,0.18);
            transition:
                box-shadow 0.3s ease,
                border-color 0.3s ease;
        }
        &:hover {
            border-color: rgba(180,120,255,0.35);
            box-shadow:
                0 0 18px rgba(0,140,255,0.18),
                0 0 40px rgba(162,0,255,0.22);
        }
        """
    ):

        # =========================
        # GENERAL SYMPTOMS
        # =========================
        st.subheader(":blue[General Symptoms]")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            answers['fever'] = yes_no('Have you had fever for more than 2 weeks?')
            answers['night_sweat'] = yes_no('Do you experience night sweats?')
            answers['weight_loss'] = yes_no('Have you experienced unexplained weight loss recently?')

        with col2:
            answers['body_feel_tired'] = yes_no('Do you often feel unusually tired or weak?')
            answers['loss_of_appetite'] = yes_no('Have you experienced loss of appetite recently?')

        st.divider()

        # =========================
        # RESPIRATORY SYMPTOMS
        # =========================
        st.subheader(":blue[Respiratory Symptoms]")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            answers['continuous_cough'] = yes_no('Have you had a continuous cough with phlegm?')
            answers['cough_blood'] = yes_no('Are you coughing blood?')
            answers['sputum'] = yes_no('Is your sputum or mucus mixed with blood?')

        with col2:
            answers['breath_shortness'] = yes_no('Do you experience shortness of breath?')
            answers['chest_pain'] = yes_no('Do you have chest pain?')

        st.divider()

        # =========================
        # OTHER PHYSICAL SYMPTOMS
        # =========================
        st.subheader(":blue[Other Physical Symptoms]")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            answers['back_pain'] = yes_no('Do you have back pain?')
            answers['lumps'] = yes_no('Have you noticed any lumps or swelling on your body?')

        with col2:
            answers['swollen_lymph_nodes'] = yes_no('Do you have swollen lymph nodes?')


   


    # When they click the prediction button, check everything first!
    if st.button('Run Prediction'):
        
        # 1. Count how many fields are still None
        unanswered_count = sum(1 for val in answers.values() if val is None)
        
        if unanswered_count > 0:
            st.error(f"⚠️ You have {unanswered_count} unanswered question(s). Please complete all fields before running the prediction.")
        else:
            # 2. If everything is filled, build the DataFrame using the dictionary values
            input_data = pd.DataFrame([{
                'two_weeks_fever': answers['fever'],
                'coughing_blood': answers['cough_blood'],
                'sputum_mixed_with_blood': answers['sputum'],
                'night_sweats': answers['night_sweat'],
                'chest_pain': answers['chest_pain'],
                'back_pain': answers['back_pain'], 
                'breath_shortness': answers['breath_shortness'],
                'weight_loss': answers['weight_loss'],
                'body_feels_tired': answers['body_feel_tired'],
                'lumps': answers['lumps'],
                'continuous_cough_and_phlegm': answers['continuous_cough'],
                'swollen_lymph_nodes': answers['swollen_lymph_nodes'],
                'loss_of_appetite': answers['loss_of_appetite']
            }])

            with st.spinner('Analyzing patient data...'):
                time.sleep(1.5)

                pred = model.predict(input_data)[0]
                prob = model.predict_proba(input_data)[0][1]

                # Create side-by-side columns to bring the alert banner to the front
                res_col1, res_col2 = st.columns([1, 5])

                with res_col1:
                    st.write("### Result:")

                with res_col2:
                    if pred == 1:
                        st.error(f'High Risk of TB ({round(prob*100,2)}%)')
                    else: 
                        st.success(f'Low Risk of TB ({round(prob*100, 2)}%)')

                # Recommendations sit cleanly below the header row
                if pred == 1:
                    st.warning("""
                    Recommendation:
                    Please visit a healthcare center for proper
                    testing and medical consultation.
                    """)
                else:
                    st.info("""
                    Recommendation:
                    Maintain healthy habits and regular medical
                    checkups.
                    """)
                    
            # From your Database setup
            save_prediction(
                user_email=st.session_state['user'].email,
                disease='Tuberculosis',
                input_data=input_data.to_dict(orient='records')[0],
                prediction=int(pred),
                probability=float(prob)
            )


    
    