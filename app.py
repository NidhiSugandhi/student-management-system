import streamlit as st
import mysql.connector
import pandas as pd

# 1. Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rni#16$tiw", # Replace with your MySQL password
        database="StudentManagement"   # Replace with your DB name
    )

# 2. Website UI & Styling
st.set_page_config(page_title="Student Management System", layout="wide")

st.markdown("""
    <style>
    /* Gradient Background for the whole app */
    .stApp {
        background: radial-gradient(circle at top left, #fdfcfb 0%, #e2d1c3 100%);
    }
    
    /* Creative Centered Title */
    .bomb-title {
        font-size: 60px;
        font-weight: 900;
        text-align: center;
        letter-spacing: -2px;
        background: linear-gradient(to right, #12c2e9, #c471ed, #f64f59);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-text {
        text-align: center;
        color: #555;
        font-weight: 300;
        margin-bottom: 40px;
    }
    
    /* Creative Card Styling */
    .stat-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.2);
    }
    </style>
    
    <h1 class="bomb-title">STUDENT HUB</h1>
    <p class="sub-text">Smart Analytics & Management System</p>
    """, unsafe_allow_html=True)

st.title("🎓 Student Management Dashboard")
st.divider() # Adds a clean line

menu = ["View Students", "Course Enrollment", "Attendance Report"]
choice = st.sidebar.selectbox("Menu", menu)

db = get_connection()
cursor = db.cursor()

if choice == "View Students":
    cursor.execute("SELECT * FROM student")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[i[0] for i in cursor.description])
    
    # Creative Layout: Metrics in "Floating" Divs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><h3>👥 Total</h3><h1 style="color:#12c2e9;">{len(df)}</h1><p>Active Scholars</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><h3>📅 Latest</h3><h1 style="color:#c471ed;">New</h1><p>Admission Entry</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><h3>✔️ Status</h3><h1 style="color:#f64f59;">Live</h1><p>DB Connected</p></div>', unsafe_allow_html=True)

    st.write("##")
    st.markdown("### 📋 Primary Student Registry")
    
    # Soft Styled Table
    st.dataframe(df.style.set_properties(**{
        'background-color': 'rgba(255, 255, 255, 0.5)',
        'color': '#333',
        'border-color': '#ddd'
    }).set_table_styles([{'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', '#333'), ('font-weight', 'bold')]}]))

elif choice == "Course Enrollment":
    st.markdown("### 🎓 Enrollment Intelligence")
    
    query = """
    SELECT s.first_name as Name, c.course_name as Course, e.grade as Grade 
    FROM student s 
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN courses c ON e.course_id = c.course_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['Name', 'Course', 'Grade'])

    def make_pretty(val):
        color = '#22C55E' if 'A' in str(val) else '#3B82F6' if 'B' in str(val) else '#F59E0B'
        return f'background-color: {color}; color: white; font-weight: bold; border-radius: 12px;'

    # --- THIS LINE FIXES THE ERROR ---
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.write("#### 📊 Academic Performance Table")
        # Ensure you use .map here
        st.dataframe(df.style.map(make_pretty, subset=['Grade']), width="stretch")

    with col_side:
        st.write("#### 🏆 Grade Mix")
        import plotly.express as px
        # Modern Donut Chart
        fig = px.pie(df, names='Grade', hole=0.6, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
        st.plotly_chart(fig, width="stretch")

elif choice == "Attendance Report":
    st.markdown("<h3 style='color: #1E293B;'>📅 Attendance Analytics</h3>", unsafe_allow_html=True)
    
    cursor.execute("SELECT student_id, attendance_date, status FROM Attendance")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['ID', 'Date', 'Status'])
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        import plotly.express as px
        counts = df['Status'].value_counts().reset_index()
        counts.columns = ['Status', 'Count']
        
        # Soft colors for light mode
        fig = px.pie(
            counts, values='Count', names='Status',
            color='Status',
            color_discrete_map={"Present": "#22C55E", "Absent": "#EF4444"},
            hole=0.4
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.write("#### Attendance Summary")
        c_pres = len(df[df['Status'] == 'Present'])
        c_abs = len(df[df['Status'] == 'Absent'])
        st.info(f"✅ Total Present: {c_pres}")
        st.error(f"❌ Total Absent: {c_abs}")

    st.markdown("---")
    st.write("#### 📋 Detailed Attendance Log")
    
    # Styled Table for Light Mode
    styled_attendance = df.style.set_properties(**{
        'background-color': 'white',
        'color': '#1E293B',
        'border-color': '#E2E8F0'
    }).map(lambda x: 'color: #16A34A; font-weight: bold' if x == 'Present' 
                    else 'color: #DC2626; font-weight: bold' if x == 'Absent' else '', subset=['Status'])
    
    st.dataframe(styled_attendance, width="stretch")

# Stylish Sidebar Footer
st.sidebar.markdown("---")
# 1. Add a Creative Header to the Sidebar
st.sidebar.markdown("""
    <div style="text-align: center; padding-bottom: 20px;">
        <div style="
            display: inline-block;
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #12c2e9, #c471ed, #f64f59);
            border-radius: 50%;
            color: white;
            line-height: 80px;
            font-size: 40px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        ">
            🎓
        </div>
        <h3 style="margin: 0; color: #333; font-weight: 700;">Admin Portal</h3>
        <p style="margin: 0; color: #888; font-size: 12px;">Active Session: 2026</p>
    </div>
    <hr style="margin-top: 5px; margin-bottom: 20px; border: 0; border-top: 1px solid #eee;">
    """, unsafe_allow_html=True)

# 2. Then your existing menu selection code
# choice = st.sidebar.selectbox("Menu", ["View Students", "Course Enrollment", "Attendance Report"])

st.sidebar.markdown(
    """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
        <p style="margin:0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Project Architect</p>
        <h3 style="margin:0; font-weight: 800;">Nidhi Sugandhi</h3>
        <p style="margin-top: 10px; font-size: 12px; opacity: 0.8;">© 2026 Innovation Lab</p>
    </div>
    """, 
    unsafe_allow_html=True
)
