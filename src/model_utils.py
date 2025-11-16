import google.generativeai as genai
import os
import pandas as pd


genai.configure(api_key=os.getenv("GEMINI_KEY"))

advisor_model = genai.GenerativeModel(
    model_name = 'gemini-2.5-flash'
)

ADVISOR_SYSTEM_PROMPT = """
You are a College Affordability Advisor.
You give grounded, empathetic, data-backed advice to students exploring college options.

You specialize in:
- Affordability (net price, affordability gap, weekly hours to close the gap)
- Public vs private institutions
- Regional and in-state guidance
- MSI institutions (HSI, HBCU, AANAPII, Tribal)
- Parent and independent students
- International students
- First-generation challenges

Rules:
1. NEVER hallucinate colleges or numbers.
2. ONLY use the information explicitly provided in the context.
3. If any information is missing, say “data not provided.”
4. Do NOT generalize or infer details not present in the context.
5. Be encouraging, clear, and helpful.
6. Think step-by-step internally, but ONLY output the final polished answer.
7. Do NOT output your reasoning chain.

You will be given a STUDENT PROFILE and COLLEGE DATA after this prompt.
Do NOT respond until you see that context.

=== OUTPUT FORMAT ===
Provide:
1. A 2–3 sentence overview of how the recommended colleges relate to the student’s situation.
2. Bullet points for each recommended college, each with:
   - “Why it fits” (specific reasons tied directly to the student’s needs)
   - Financial alignment
   - MSI or cultural alignment (if applicable)
   - Academic/major alignment (if applicable)
   - Support structures: parent support, adult learner support, international-friendly features (only if supported by the data)
3. End with a brief closing suggestion or encouragement.
"""

def build_rag_context(student: dict, recs):
    if isinstance(recs, pd.DataFrame):
        schools = recs.to_dict(orient="records")
    else:
        schools = recs

    student_lines = ["Student Profile:"]
    for k, v in student.items():
        if v is None or v == "":
            continue
        if isinstance(v, bool):
            v = "Yes" if v else "No"
        student_lines.append(f"- {k.replace('_',' ').title()}: {v}")
    student_text = "\n".join(student_lines)

    college_blocks = []
    for col in schools:
        name = col.get("Institution_Name_x") or col.get("Institution Name") or "Unnamed Institution"
        block_lines = [f"College: {name}"]
        for key, value in col.items():
            if key in ["Institution_Name_x", "Institution Name"]:
                continue
            if value is None:
                continue
            if isinstance(value, (float, int)) and abs(value) > 999:
                value_str = f"${value:,.0f}"
            else:
                value_str = value
            block_lines.append(f"- {key}: {value_str}")
        college_blocks.append("\n".join(block_lines))

    colleges_text = "\n\n".join(college_blocks)

    full_context = f"""
=== STUDENT PROFILE ===
{student_text}

=== COLLEGE DATA ===
{colleges_text}
"""
    return full_context

def advisor_chat(rag_context):
    response = advisor_model.generate_content(
        contents=[
            {"role": "user", "parts": [{"text": ADVISOR_SYSTEM_PROMPT}]},
            {"role": "user", "parts": [{"text": rag_context}]}
        ]
    )
    return response.text