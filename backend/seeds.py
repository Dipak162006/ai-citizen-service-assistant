from app import create_app
from models import db, Scheme

app = create_app()

def seed_schemes():
    schemes = [
        # --- Agriculture & Farmers ---
        {
            "scheme_name": "PM-KISAN Samman Nidhi",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"occupation": "Farmer", "land_holding_limit": 2},
            "benefits": "Financial benefit of Rs. 6000/- per year in three equal installments.",
            "documents": ["Aadhaar Card", "Land Ownership Record", "Bank Account Details"],
            "state": "All India",
            "official_link": "https://pmkisan.gov.in",
            "description": "Income support scheme for heavy landholding farmer families."
        },
        {
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"occupation": "Farmer", "crop_loan": "Optional"},
            "benefits": "Insurance coverage and financial support in event of failure of notified crops as a result of natural calamities, pests & diseases.",
            "documents": ["Land Possession Certificate", "Aadhaar Card", "Bank Passbook"],
            "state": "All India",
            "official_link": "https://pmfby.gov.in",
            "description": "Crop insurance scheme to protect farmers from yield losses."
        },
        {
            "scheme_name": "Kisan Credit Card (KCC)",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"occupation": "Farmer", "age": "18-75"},
            "benefits": "Credit at affordable interest rates (reduced from 9% to 7%).",
            "documents": ["Identity Proof", "Address Proof", "Land Documents"],
            "state": "All India",
            "official_link": "https://www.myscheme.gov.in/schemes/kcc",
            "description": "Provides adequate and timely credit support to farmers."
        },
        {
            "scheme_name": "Soil Health Card Scheme",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"occupation": "Farmer"},
            "benefits": "Soil health report and recommendations for fertilizer dosage.",
            "documents": ["Aadhaar Card", "Land Details"],
            "state": "All India",
            "official_link": "https://soilhealth.dac.gov.in",
            "description": "Promotes soil test based balanced use of fertilizers."
        },
        {
            "scheme_name": "PM Krishi Sinchayee Yojana (PMKSY)",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"land_ownership": "Required"},
            "benefits": "Subsidies for micro-irrigation systems (drip/sprinkler).",
            "documents": ["Land Records", "Aadhaar", "Bank Details"],
            "state": "All India",
            "official_link": "https://pmksy.gov.in",
            "description": "Focuses on improving water use efficiency ('Per Drop More Crop')."
        },
         {
            "scheme_name": "e-NAM (National Agriculture Market)",
            "category": "Agriculture",
            "target_group": "Farmers",
            "eligibility": {"occupation": "Farmer"},
            "benefits": "Online trading platform for agricultural commodities to discover better prices.",
            "documents": ["Bank Details", "Aadhaar", "Registration with APMC"],
            "state": "All India",
            "official_link": "https://enam.gov.in",
            "description": "Pan-India electronic trading portal for farm produce."
        },

        # --- Health & Insurance ---
        {
            "scheme_name": "Ayushman Bharat PM-JAY",
            "category": "Health",
            "target_group": "Low Income Families",
            "eligibility": {"income_status": "BPL", "deprivation_criteria": "SECC 2011"},
            "benefits": "Cashless health insurance cover of Rs. 5 Lakh per family per year for secondary and tertiary care hospitalization.",
            "documents": ["Aadhaar Card", "Ration Card", "Family ID"],
            "state": "All India",
            "official_link": "https://pmjay.gov.in",
            "description": "World's largest government-funded healthcare program."
        },
        {
            "scheme_name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "category": "Health",
            "target_group": "All Citizens",
            "eligibility": {"age": "18-70", "bank_account": "Required"},
            "benefits": "Accidental death and disability cover of Rs. 2 Lakh for a premium of Rs. 20/year.",
            "documents": ["Aadhaar Card", "Bank Account with Auto-Debit"],
            "state": "All India",
            "official_link": "https://jansuraksha.gov.in",
            "description": "Accident insurance scheme offering affordable coverage."
        },
        {
            "scheme_name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "category": "Health",
            "target_group": "All Citizens",
            "eligibility": {"age": "18-50", "bank_account": "Required"},
            "benefits": "Life insurance cover of Rs. 2 Lakh for any cause of death (Premium: Rs. 436/year).",
            "documents": ["Aadhaar Card", "Bank Account"],
            "state": "All India",
            "official_link": "https://jansuraksha.gov.in",
            "description": "Term life insurance scheme specifically for the poor and underprivileged."
        },
        {
            "scheme_name": "Janani Suraksha Yojana",
            "category": "Health",
            "target_group": "Pregnant Women",
            "eligibility": {"gender": "Female", "condition": "BPL/SC/ST"},
            "benefits": "Cash assistance for institutional delivery to reduce maternal and nenoatal mortality.",
            "documents": ["BPL Card", "Aadhaar", "MCH Card"],
            "state": "All India",
            "official_link": "https://nhm.gov.in",
            "description": "Safe motherhood intervention under the National Health Mission."
        },
        {
            "scheme_name": "Mission Indradhanush",
            "category": "Health",
            "target_group": "Children & Pregnant Women",
            "eligibility": {"age": "0-2 years", "condition": "Unimmunized"},
            "benefits": "Free vaccination against 12 vaccine-preventable diseases.",
            "documents": ["Birth Certificate", "Mother's ID"],
            "state": "All India",
            "official_link": "https://www.nhp.gov.in/mission-indradhanush",
            "description": "Health mission to ensure full immunization coverage."
        },

        # --- Housing & Urban Development ---
        {
            "scheme_name": "Pradhan Mantri Awas Yojana (Urban)",
            "category": "Housing & Urban Development",
            "target_group": "Urban Poor",
            "eligibility": {"income_group": "EWS/LIG/MIG", "location_type": "Urban"},
            "benefits": "Interest subsidy up to Rs. 2.67 lakh on home loans for first-time homebuyers.",
            "documents": ["Aadhaar", "Income Certificate", "Property Papers"],
            "state": "All India",
            "official_link": "https://pmaymis.gov.in",
            "description": "Housing for All in urban areas by 2024."
        },
        {
             "scheme_name": "Pradhan Mantri Awas Yojana (Gramin)",
            "category": "Housing & Urban Development",
            "target_group": "Rural Poor",
            "eligibility": {"income_status": "BPL", "location_type": "Rural", "housing_status": "Kutcha"},
            "benefits": "Financial assistance of Rs. 1.2 Lakh (plains) / Rs. 1.3 Lakh (hilly) for house construction.",
            "documents": ["Aadhaar", "Job Card", "Bank Account"],
            "state": "All India",
            "official_link": "https://pmayg.nic.in",
            "description": "Pucca houses with basic amenities for rural houseless."
        },
        {
            "scheme_name": "Smart Cities Mission",
            "category": "Housing & Urban Development",
            "target_group": "Urban Citizens",
            "eligibility": {"city": "Selected Smart City"},
            "benefits": "Improved infrastructure, digital services, and sustainable environment.",
            "documents": ["N/A"],
            "state": "Selected Cities",
            "official_link": "https://smartcities.gov.in",
            "description": "Urban renewal and retrofitting program to develop smart cities."
        },
        {
            "scheme_name": "Swachh Bharat Mission (Urban)",
            "category": "Housing & Urban Development",
            "target_group": "Urban Households",
            "eligibility": {"location_type": "Urban", "toilet_status": "None"},
            "benefits": "Financial incentive for construction of Individual Household Latrines (IHHL).",
            "documents": ["Aadhaar", "Bank Account", "Photo"],
            "state": "All India",
            "official_link": "https://swachhbharaturban.gov.in",
            "description": "Clean India mission focusing on sanitation and waste management."
        },
        {
            "scheme_name": "AMRUT (Atal Mission for Rejuvenation)",
            "category": "Housing & Urban Development",
            "target_group": "Urban Citizens",
            "eligibility": {"city_class": "Class I"},
            "benefits": "Improved water supply, sewerage, and urban transport infrastructure.",
            "documents": ["N/A"],
            "state": "Selected Cities",
            "official_link": "https://amrut.gov.in",
            "description": "Transformation of 500 cities/towns into efficient urban living spaces."
        },

        # --- Education & Students ---
        {
            "scheme_name": "Post Matric Scholarship for SC Students",
            "category": "Education",
            "target_group": "SC Students",
            "eligibility": {"category": "SC", "income_limit": "2.5 Lakh"},
            "benefits": "Financial assistance for education at post-matriculation level.",
            "documents": ["Caste Certificate", "Income Certificate", "Mark Sheet"],
            "state": "All India",
            "official_link": "https://socialjustice.gov.in",
            "description": "Scholarship to enable SC students to complete their education."
        },
        {
            "scheme_name": "National Means-cum-Merit Scholarship",
            "category": "Education",
            "target_group": "Meritorious Students",
            "eligibility": {"class": "Class 9", "income_limit": "3.5 Lakh", "min_marks": "55%"},
            "benefits": "Scholarship of Rs. 12,000 per annum.",
            "documents": ["Income Certificate", "Mark Sheet", "Aadhaar"],
            "state": "All India",
            "official_link": "https://scholarships.gov.in",
            "description": "Scholarship to arrest drop-out rate of meritorious students at class VIII."
        },
        {
            "scheme_name": "Central Sector Scheme of Scholarship",
            "category": "Education",
            "target_group": "College Students",
            "eligibility": {"percentile": "Top 20th", "income_limit": "4.5 Lakh"},
            "benefits": "Rs. 10,000/year (Graduation) to Rs. 20,000/year (Post-Graduation).",
            "documents": ["Class 12 Marksheet", "Income Certificate", "Aadhaar"],
            "state": "All India",
            "official_link": "https://scholarships.gov.in",
            "description": "Scholarship for university and college students."
        },
        {
            "scheme_name": "PM YUVA Yojana",
            "category": "Education",
            "target_group": "Young Authors",
            "eligibility": {"age_max": 30, "language": "Indian"},
            "benefits": "Mentorship and scholarship of Rs. 50,000 per month for 6 months.",
            "documents": ["Age Proof", "Manuscript Draft"],
            "state": "All India",
            "official_link": "https://www.nbtindia.gov.in",
            "description": "Mentoring scheme for young and budding authors."
        },
        {
            "scheme_name": "Vidyaalakshmi Portal",
            "category": "Education",
            "target_group": "Students seeking loans",
            "eligibility": {"admission": "Confirmed"},
            "benefits": "Single window for students to access education loans and scholarships.",
            "documents": ["Admission Letter", "KYC Documents"],
            "state": "All India",
            "official_link": "https://www.vidyalakshmi.co.in",
            "description": "Education Loan Portal."
        },

        # --- Women & Child Welfare ---
        {
            "scheme_name": "Sukanya Samriddhi Yojana",
            "category": "Women & Child",
            "target_group": "Girl Child",
            "eligibility": {"gender": "Female", "max_age_entry": 10},
            "benefits": "High interest rate savings scheme (approx 8%) with tax benefits under 80C.",
            "documents": ["Birth Certificate", "Parent ID", "Address Proof"],
            "state": "All India",
            "official_link": "https://www.nsiindia.gov.in",
            "description": "Small savings scheme to ensure a bright future for girl children."
        },
        {
            "scheme_name": "Beti Bachao Beti Padhao",
            "category": "Women & Child",
            "target_group": "Girl Child",
            "eligibility": {"gender": "Female"},
            "benefits": "Educational and welfare awareness to prevent gender-biased sex selection.",
            "documents": ["N/A"],
            "state": "All India",
            "official_link": "https://wcd.nic.in/bbbp",
            "description": "Campaign to generate awareness and improve the efficiency of welfare services for women."
        },
        {
            "scheme_name": "Pradhan Mantri Matru Vandana Yojana",
            "category": "Women & Child",
            "target_group": "Pregnant Women",
            "eligibility": {"age_min": 19, "child_order": 1},
            "benefits": "Cash incentive of Rs. 5000 in three installments directly to bank account.",
            "documents": ["Aadhaar", "MCP Card", "Bank Details"],
            "state": "All India",
            "official_link": "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana",
            "description": "Maternity benefit program."
        },
        {
            "scheme_name": "Mahila Samman Savings Certificate",
            "category": "Women & Child",
            "target_group": "Women",
            "eligibility": {"gender": "Female"},
            "benefits": "Fixed interest rate of 7.5% for two years.",
            "documents": ["Identity Proof", "Address Proof"],
            "state": "All India",
            "official_link": "https://www.indiapost.gov.in",
            "description": "One-time small savings scheme for women."
        },
        {
            "scheme_name": "Ujjwala Yojana",
            "category": "Women & Child",
            "target_group": "Women from BPL Households",
            "eligibility": {"gender": "Female", "poverty_status": "BPL", "age_min": 18},
            "benefits": "Free LPG connection with financial support of Rs. 1600.",
            "documents": ["BPL Ration Card", "Aadhaar", "Bank Account"],
            "state": "All India",
            "official_link": "https://www.pmuy.gov.in",
            "description": "Clean cooking fuel for rural women."
        },

        # --- Senior Citizens ---
        {
            "scheme_name": "Indira Gandhi Landless Old Age Pension",
            "category": "Senior Citizens",
            "target_group": "BPL Senior Citizens",
            "eligibility": {"min_age": 60, "poverty_status": "BPL"},
            "benefits": "Monthly pension (Rs. 200-500) provided by Central Govt + State contribution.",
            "documents": ["Age Proof", "BPL Card", "Bank Passbook"],
            "state": "All India",
            "official_link": "https://nsap.nic.in",
            "description": "Social assistance for the elderly poor."
        },
        {
            "scheme_name": "Pradhan Mantri Vaya Vandana Yojana",
            "category": "Senior Citizens",
            "target_group": "Senior Citizens",
            "eligibility": {"min_age": 60},
            "benefits": "Guaranteed pension for 10 years at an interest rate of ~7.4% p.a.",
            "documents": ["Aadhaar", "Pan Card", "Bank Details"],
            "state": "All India",
            "official_link": "https://licindia.in",
            "description": "Pension scheme for senior citizens managed by LIC."
        },
        {
            "scheme_name": "Rashtriya Vayoshri Yojana",
            "category": "Senior Citizens",
            "target_group": "BPL Senior Citizens",
            "eligibility": {"min_age": 60, "poverty_status": "BPL", "disability": "Age-related"},
            "benefits": "Free physical aids and assisted-living devices (Hearing aids, Wheelchairs, etc.).",
            "documents": ["Aadhaar", "BPL Certificate", "Medical Certificate"],
            "state": "All India",
            "official_link": "https://socialjustice.gov.in",
            "description": "Providing physical aids to senior citizens belonging to BPL category."
        },
        {
            "scheme_name": "Senior Citizens Savings Scheme (SCSS)",
            "category": "Senior Citizens",
            "target_group": "Senior Citizens",
            "eligibility": {"min_age": 60},
            "benefits": "High safety and regular income via interest payments (Currently ~8.2%).",
            "documents": ["Age Proof", "Address Proof", "PAN Card"],
            "state": "All India",
            "official_link": "https://www.indiapost.gov.in",
            "description": "Government-backed savings scheme for reliable retirement income."
        },

        # --- Employment & Skill Development ---
        {
            "scheme_name": "MGNREGA",
            "category": "Employment",
            "target_group": "Rural Households",
            "eligibility": {"location_type": "Rural", "age_min": 18},
            "benefits": "Guaranteed 100 days of wage employment in a financial year.",
            "documents": ["Job Card", "Aadhaar", "Bank Account"],
            "state": "All India",
            "official_link": "https://nrega.nic.in",
            "description": "Rural employment guarantee scheme."
        },
        {
            "scheme_name": "PM Kaushal Vikas Yojana (PMKVY)",
            "category": "Employment",
            "target_group": "Youth",
            "eligibility": {"age": "15-45", "education": "Dropout/Unemployed"},
            "benefits": "Free short-term skill training and industry-recognized certification.",
            "documents": ["Aadhaar", "Education Proof"],
            "state": "All India",
            "official_link": "https://www.pmkvyofficial.org",
            "description": "Skill certification scheme to encourage youth to take up industry-relevant skills."
        },
        {
            "scheme_name": "Start-up India",
            "category": "Employment",
            "target_group": "Entrepreneurs",
            "eligibility": {"entity_type": "Private Ltd/LLP", "age_max": "10 years coverage"},
            "benefits": "Tax exemptions, easy compliance, and funding support.",
            "documents": ["Incorporation Certificate", "PAN"],
            "state": "All India",
            "official_link": "https://www.startupindia.gov.in",
            "description": "Flagship initiative to build a strong ecosystem for nurturing innovation and startups."
        },
        {
            "scheme_name": "PM Employment Generation Programme (PMEGP)",
            "category": "Employment",
            "target_group": "Entrepreneurs",
            "eligibility": {"age_min": 18, "education": "8th Pass (for >10L projects)"},
            "benefits": "Credit-linked subsidy program for generating employment in micro-enterprises.",
            "documents": ["Project Report", "Aadhaar", "Caste Certificate"],
            "state": "All India",
            "official_link": "https://www.kviconline.gov.in",
            "description": "Loan scheme with subsidy for setting up new micro-enterprises."
        }
    ]

    with app.app_context():
        # Handle Schema Change: Drop and Recreate Schemes Table Only
        try:
            Scheme.__table__.drop(db.engine)
            print("Dropped existing schemes table.")
        except Exception as e:
            print(f"Table might not exist: {e}")

        # Create table with new schema
        Scheme.__table__.create(db.engine)
        print("Created new schemes table.")

        for s_data in schemes:
            scheme = Scheme(**s_data)
            db.session.add(scheme)
        
        db.session.commit()
        print(f"Successfully seeded {len(schemes)} schemes.")

if __name__ == '__main__':
    seed_schemes()
