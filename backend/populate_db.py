
import sys
import os
import json

# Add backend to path
sys.path.append(os.getcwd())

from flask import Flask
from app.models.models import db, Scheme, CommunityPost, Conversation
from app.core.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def populate_schemes():
    schemes_data = [
            {
                "id": "pm-kisan",
                "title": "PM-KISAN Samman Nidhi",
                "text": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Provides ₹6,000 per year income support to all landholding farmer families in three equal installments of ₹2,000 each. Launched on 1st December 2018. Eligibility: All landholding farmers. Documents: Aadhaar, bank account, land records. Apply at pmkisan.gov.in or nearest CSC. Helpline: 155261.",
                "keywords": ["kisan", "farmer", "money", "6000", "pm kisan", "agriculture", "farming", "crop", "land", "kisaan"],
                "link": "https://pmkisan.gov.in",
                "benefit": "₹6,000/year Income Support",
                "ministry": "Ministry of Agriculture",
                "category": "agriculture",
                "version": "1.1.0",
                "rules": {
                    "mandatory": [
                        { "field": "occupation", "operator": "in", "value": ["Farmer", "Kisan"], "label": "Landholding Farmer" },
                        { "field": "location_state", "operator": "ne", "value": "", "label": "Indian Citizen" }
                    ]
                }
            },
            {
                "id": "ayushman",
                "title": "Ayushman Bharat - PMJAY",
                "text": "Ayushman Bharat (PM Jan Arogya Yojana): Provides health insurance coverage of ₹5 Lakh per family per year for secondary and tertiary care hospitalization. Covers 1,393 procedures including surgery, medical care, and diagnostics. Eligibility: Based on SECC 2011 deprivation criteria. No premium required. Apply via pmjay.gov.in or Ayushman Mitra at empanelled hospitals.",
                "keywords": ["health", "insurance", "medical", "hospital", "ayushman", "treatment", "disease", "doctor", "medicine", "surgery", "bimari"],
                "link": "https://pmjay.gov.in",
                "benefit": "₹5 Lakh Free Health Cover",
                "ministry": "Ministry of Health",
                "category": "health",
                "version": "1.0.0",
                "rules": {
                    "mandatory": [
                        { "field": "income_bracket", "operator": "in", "value": ["EWS", "Lower Class", "Poor"], "label": "Financial Eligibility (SECC 2011)" }
                    ]
                }
            },
            {
                "id": "fasal-bima",
                "title": "PM Fasal Bima Yojana (PMFBY)",
                "text": "Pradhan Mantri Fasal Bima Yojana (PMFBY): Crop insurance scheme providing financial support to farmers suffering crop loss from unforeseen events like drought, flood, hailstorm, cyclone, pest attack. Premium: 2% for Kharif, 1.5% for Rabi, 5% for commercial/horticultural crops. Claim within 72 hours of crop damage. Apply via bank, CSC, or pmfby.gov.in.",
                "keywords": ["crop", "damage", "bima", "insurance", "loss", "cyclone", "flood", "drought", "fasal", "weather"],
                "link": "https://pmfby.gov.in",
                "benefit": "Crop Loss Insurance",
                "ministry": "Ministry of Agriculture",
                "category": "agriculture"
            },
            {
                "id": "awas",
                "title": "PM Awas Yojana (PMAY)",
                "text": "Pradhan Mantri Awas Yojana: Housing for All by providing affordable housing. Gramin (Rural): Up to ₹1.30 lakh in plains, ₹1.50 lakh in hilly areas for construction of pucca house. Urban: Interest subsidy of 6.5% on home loans for EWS/LIG. Eligibility: No pucca house anywhere in India. Apply via gram panchayat (rural) or ULB (urban).",
                "keywords": ["house", "awas", "ghar", "home", "housing", "construction", "build", "rent", "shelter", "makan"],
                "link": "https://pmaymis.gov.in/",
                "benefit": "₹1.30-2.67 Lakh Housing Aid",
                "ministry": "Ministry of Housing",
                "category": "housing"
            },
            {
                "id": "mudra",
                "title": "PM MUDRA Yojana",
                "text": "Pradhan Mantri MUDRA Yojana: Provides loans up to ₹10 lakh for non-corporate, non-farm small/micro enterprises. Three categories: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 lakh), Tarun (₹5 lakh to ₹10 lakh). No collateral required. Apply at any bank, NBFC, or MFI. No processing fee for Shishu loans.",
                "keywords": ["loan", "mudra", "business", "money", "enterprise", "shop", "startup", "self-employed", "vyapaar", "dukaan"],
                "link": "https://www.mudra.org.in/",
                "benefit": "Loans up to ₹10 Lakh",
                "ministry": "Ministry of Finance",
                "category": "financial"
            },
            {
                "id": "sukanya",
                "title": "Sukanya Samriddhi Yojana",
                "text": "Sukanya Samriddhi Yojana: Savings scheme for girl child. Interest rate 8.2% p.a. (highest among small savings). Minimum deposit ₹250/year, maximum ₹1.5 lakh/year. Account opens from birth to age 10. Matures at 21 years. 50% withdrawal allowed at age 18 for education. Tax-free under Section 80C.",
                "keywords": ["girl", "daughter", "beti", "education", "savings", "sukanya", "ladki", "bachchi", "school", "college"],
                "link": "https://www.nsiindia.gov.in/",
                "benefit": "8.2% Interest Girl Child Savings",
                "ministry": "Ministry of Finance",
                "category": "education"
            },
            {
                "id": "pm-vishwakarma",
                "title": "PM Vishwakarma Yojana",
                "text": "PM Vishwakarma: Support scheme for traditional artisans and craftspeople working with hands and tools. Covers 18 trades including carpenter, blacksmith, goldsmith, potter, tailor, washerman. Benefits: Recognition (PM Vishwakarma certificate), skill upgradation, toolkit incentive of ₹15,000, collateral-free credit up to ₹3 lakh at 5% interest.",
                "keywords": ["artisan", "craft", "carpenter", "blacksmith", "tailor", "potter", "vishwakarma", "karigar", "mistri", "darzi", "lohar"],
                "link": "https://pmvishwakarma.gov.in/",
                "benefit": "₹15K Toolkit + ₹3 Lakh Loan",
                "ministry": "Ministry of MSME",
                "category": "employment"
            },
            {
                "id": "matru-vandana",
                "title": "PM Matru Vandana Yojana",
                "text": "Pradhan Mantri Matru Vandana Yojana (PMMVY): Cash incentive of ₹11,000 for first child and ₹6,000 for second child (girl only) for pregnant women and lactating mothers. Compensation for wage loss during pregnancy. Eligibility: All pregnant women for first living child. Apply at nearest Anganwadi Centre or health facility.",
                "keywords": ["pregnant", "mother", "baby", "child", "maternity", "birth", "delivery", "garbhwati", "maa", "bachcha"],
                "link": "https://wcd.nic.in/",
                "benefit": "₹6,000-11,000 Maternity Benefit",
                "ministry": "Ministry of Women & Child",
                "category": "health"
            },
            {
                "id": "jandhan",
                "title": "PM Jan Dhan Yojana",
                "text": "Pradhan Mantri Jan Dhan Yojana: Financial inclusion scheme providing zero-balance bank accounts with RuPay debit card and ₹2 lakh accident insurance. Overdraft facility of ₹10,000 for eligible accounts. Life cover of ₹30,000 for accounts opened before Jan 2015. Apply at any bank branch with Aadhaar/voter ID.",
                "keywords": ["bank", "account", "jan dhan", "debit card", "insurance", "zero balance", "khata", "paisa"],
                "link": "https://pmjdy.gov.in/",
                "benefit": "Zero Balance Bank Account + Insurance",
                "ministry": "Ministry of Finance",
                "category": "financial"
            },
            {
                "id": "skill-india",
                "title": "Skill India Mission",
                "text": "Skill India Mission: Provides free skill training in 40+ sectors to Indian youth. Includes PMKVY, NAPS, and Jan Shikshan Sansthan. Linkage to employment and entrepreneurship.",
                "keywords": ["training", "skill", "job", "career", "employment", "learning"],
                "link": "https://skillindia.gov.in",
                "benefit": "Certified Skill Training",
                "ministry": "Ministry of Skill Development",
                "category": "employment"
            },
            {
                "id": "svanidhi",
                "title": "PM SVANidhi",
                "text": "Micro-credit facility for street vendors to restart their livelihoods. Loans up to ₹50,000 with interest subsidy and digital repayment incentives.",
                "keywords": ["vendor", "street", "loan", "thela", "hawker"],
                "link": "https://pmsvanidhi.mohua.gov.in",
                "benefit": "₹10,000-50,000 Working Capital Loan",
                "ministry": "Ministry of Housing",
                "category": "financial"
            }
    ]

    print("Checking specific schemes...")
    for s_data in schemes_data:
        existing = Scheme.query.get(s_data['id'])
        if not existing:
            scheme = Scheme(
                id=s_data['id'],
                title=s_data['title'],
                text=s_data['text'],
                benefit=s_data.get('benefit'),
                ministry=s_data.get('ministry'),
                link=s_data.get('link'),
                keywords=s_data.get('keywords'),
                category=s_data.get('category'),
                rules=s_data.get('rules'),
                version=s_data.get('version', '1.0.0')
            )
            db.session.add(scheme)
        else:
            # Update existing if needed
            existing.rules = s_data.get('rules')
            existing.version = s_data.get('version', '1.0.0')
    db.session.commit()
    print("Schemes populated.")

def populate_community_posts():
    print("Checking community posts...")
    if CommunityPost.query.count() == 0:
        posts = [
            CommunityPost(
                title="Village Panchayat Meeting",
                content="Discussion on new water irrigation project scheduled for tomorrow at 10 AM.",
                author="Sarpanch Office",
                author_role="Official",
                location="Varanasi",
                likes=45,
                comments_count=12
            ),
             CommunityPost(
                title="New Seed Distribution Center",
                content="Subsidized wheat seeds available at Block A center. Bring Aadhaar card.",
                author="Kisan Seva Kendra",
                author_role="Support",
                location="Varanasi",
                likes=89,
                comments_count=24
            ),
            CommunityPost(
                title="Scholarship Deadline Extended",
                content="Last date for Pre-Matric scholarship application extended to 31st March.",
                author="Edu Dept",
                author_role="Official",
                location="Lucknow",
                likes=120,
                comments_count=8
            )
        ]
        db.session.add_all(posts)
        db.session.commit()
        print("Community posts added.")
    else:
        print("Community posts already exist.")


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Tables created.")
            populate_schemes()
            populate_community_posts()
        except Exception as e:
            print(f"Error: {e}")
