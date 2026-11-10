import streamlit as st
import pandas as pd
import joblib
import time
from database import save_prediction
from streamlit_extras.stylable_container import stylable_container

# LOAD MODEL
model = joblib.load('model/Hiv_model_v1.pkl')

def show_hiv_page():
    st.title("HIV/AIDS Prediction", text_alignment="center")
    
    st.write("Fill in the questionnaire below.")

    # Dictionary to store all inputs for easy validation
    answers = {}

   
    with stylable_container(
        key="hiv_card",
        css_styles="""
        {
            background: #ffffff;
            border-radius: 24px;
            padding: 32px;
            border: 1px solid #e5e7eb;
            transition:
                box-shadow 0.3s ease,
                border-color 0.3s ease;
        }
        &:hover {
            border-color: #e8b6b6;
            box-shadow:
                0 4px 14px rgba(25,35,45,0.06);
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



    # Preserve the latest prediction through Streamlit reruns.
    result_key = "hiv_prediction_result"
    answer_signature = tuple(answers.items())
    saved_result = st.session_state.get(result_key)
    if saved_result and saved_result.get("answers") != answer_signature:
        st.session_state.pop(result_key, None)

    if st.button("Run Prediction", key="hiv_run_prediction"):
        unanswered_count = sum(1 for val in answers.values() if val is None)

        if unanswered_count > 0:
            st.error(
                f"⚠️ Please answer all fields. There are "
                f"{unanswered_count} questions left empty."
            )
        else:
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
                # Class 1 represents the positive (disease-risk) class.
                # Always display its probability, and apply the requested
                # 50% threshold consistently to both the label and percentage.
                class_index = list(model.classes_).index(1)
                prob = float(model.predict_proba(input_data)[0][class_index])
                pred = int(prob >= 0.50)

            st.session_state[result_key] = {
                "answers": answer_signature,
                "prediction": pred,
                "probability": prob,
            }

            save_prediction(
                user_email=st.session_state['user'].email,
                disease='HIV/AIDS',
                input_data=input_data.to_dict(orient='records')[0],
                prediction=pred,
                probability=prob
            )

    # Always render the saved result, even after unrelated reruns.
    saved_result = st.session_state.get(result_key)
    if saved_result and saved_result.get("answers") == answer_signature:
        pred = saved_result["prediction"]
        prob = saved_result["probability"]

        res_col1, res_col2 = st.columns([1, 5])
        with res_col1:
            st.markdown("## Result:")
        with res_col2:
            if pred == 1:
                st.error(f"High Risk of HIV/AIDS ({round(prob * 100, 2)}%)")
            else:
                st.success(
                    f"Low Risk of HIV/AIDS ({round(prob * 100, 2)}%)"
                )

        if pred == 1:
            st.warning(
                "**Recommendation:** Please visit a healthcare center for "
                "proper testing and medical consultation."
            )
        else:
            st.info(
                "**Recommendation:** Maintain healthy habits and regular "
                "medical checkups."
            )
