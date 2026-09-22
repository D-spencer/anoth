import streamlit as st
import pandas as pd
import joblib
import time
from database import save_prediction
from streamlit_extras.stylable_container import stylable_container

# LOAD MODEL
model = joblib.load('model/Hiv_model_v1.pkl')

def show_hiv_page():
    st.title(':blue[Hiv/Aids Prediction]', text_alignment="center")
    
    st.write("Fill in the questionnaire below.")

    # Dictionary to store all inputs for easy validation
    answers = {}

   
    with stylable_container(
        key="hiv_card",
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

        # ==========================================
        # PERSONAL INFORMATION
        # ==========================================
        st.subheader("Personal Information")

        col1, col2 = st.columns(2)

        with col1:
            answers['age'] = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=18
            )

        with col2:
            answers['marital_status'] = st.selectbox(
                "Marital Status",
                options=["unmarried", "married", "divorced", "widowed", "cohabiting"],
                format_func=lambda x: x.replace("_", " ").title(),
                index=None,
                placeholder="Select status"
            )

        st.divider()

        # ==========================================
        # EDUCATION & AWARENESS
        # ==========================================
        st.subheader("Education & Awareness")

        col1, col2 = st.columns(2)

        with col1:
            answers['educational_background'] = st.selectbox(
                "Educational Background",
                options=[
                    "college degree",
                    "senior high school",
                    "junior high school",
                    "illiteracy",
                    "primary school"
                ],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select education level"
            )

        with col2:
            answers['aids_education'] = st.selectbox(
                "Received AIDS Education",
                options=["no", "yes"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select an option"
            )

        st.divider()

        # ==========================================
        # SEXUAL HEALTH & BEHAVIOUR
        # ==========================================
        st.subheader("Sexual Health & Behaviour")

        col1, col2 = st.columns(2)

        with col1:
            answers['sexual_orientation'] = st.selectbox(
                "Sexual Orientation",
                options=["heterosexual", "bisexual", "homosexual"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select orientation"
            )

            answers['places_of_seeking_sex_partners'] = st.selectbox(
                "Places of Seeking Sex Partners",
                options=["bar", "park", "internet", "public bath", "others"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select primary place"
            )

        with col2:
            answers['drug_taking'] = st.selectbox(
                "Drug Taking",
                options=["no", "yes"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select an option"
            )

        st.divider()

        # ==========================================
        # HEALTH HISTORY
        # ==========================================
        st.subheader("Health History")

        col1, col2 = st.columns(2)

        with col1:
            answers['std'] = st.selectbox(
                "History of STD",
                options=["no", "yes"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select an option"
            )

        with col2:
            answers['hiv_test_in_past_year'] = st.selectbox(
                "HIV Test in Past Year",
                options=["no", "yes"],
                format_func=lambda x: x.title(),
                index=None,
                placeholder="Select an option"
            )



    # PREDICTION BUTTON
    if st.button("Run Prediction"):
        
        # Validation Logic: Check if any value in our dictionary is None
        unanswered_count = sum(1 for val in answers.values() if val is None)

        if unanswered_count > 0:
            st.error(f"⚠️ Please answer all fields. There are {unanswered_count} questions left empty.")
        else:
            # All fields are filled, proceed with prediction
            input_data = pd.DataFrame([{
                "age": answers['age'],
                "marital_status": answers['marital_status'],
                "std": answers['std'],
                "educational_background": answers['educational_background'],
                "hiv_test_in_past_year": answers['hiv_test_in_past_year'],
                "aids_education": answers['aids_education'],
                "places_of_seeking_sex_partners": answers['places_of_seeking_sex_partners'],
                "sexual_orientation": answers['sexual_orientation'],
                "drug_taking": answers['drug_taking']
            }])

            with st.spinner("Analyzing patient data..."):
                time.sleep(1.5)
                pred = model.predict(input_data)[0]
                prob = model.predict_proba(input_data)[0][1]

            # Create two side-by-side columns for the header and the status box
            res_col1, res_col2 = st.columns([1, 5])  # 1:4 ratio keeps them close together

            with res_col1:
                st.markdown("## Result:")

            with res_col2:
                if pred == 1:
                    st.error(f"High Risk of HIV/AIDS ({round(prob*100, 2)}%)")
                else:
                    st.success(f"Low Risk of HIV/AIDS ({round((1-prob)*100, 2)}%)")

            # Recommendations can sit nicely underneath the main row
            if pred == 1:
                st.warning("""
                **Recommendation:** Please visit a healthcare center for proper testing and medical consultation.
                """)
            else:
                st.info("""
                **Recommendation:** Maintain healthy habits and regular medical checkups.
                """)




            save_prediction(
                user_email=st.session_state['user'].email,
                disease='HIV/AIDS',
                input_data=input_data.to_dict(orient='records')[0],
                prediction=int(pred),
                probability=float(prob)
            )

            
   
