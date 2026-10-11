import os
import pymupdf

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "documents", "sample")
os.makedirs(SAMPLES_DIR, exist_ok=True)

DOCS = [
    {
        "filename": "Vendor_Agreement.pdf",
        "title": "Vendor Master Services Agreement",
        "pages": [
            "VENDOR MASTER SERVICES AGREEMENT\n\nParties: Alpha Global Enterprises ('Client') and ABC Technologies Inc ('Vendor').\n\n1. SCOPE OF SERVICES\nVendor shall provide enterprise cloud infrastructure management, data pipeline orchestration, and technical support as detailed in Exhibit A.\n\n2. TERM AND RENEWAL\nThis Agreement commences on October 1, 2026 and shall remain in effect for an initial period of twelve (12) months. It will automatically renew for successive 12-month periods unless either party provides timely notice.",
            "3. TERMINATION CLAUSE\nThe agreement requires 30 days written notice for standard termination without cause. Either party may terminate immediately upon material breach if uncured within fifteen (15) days of notice.\n\n4. FEES AND PAYMENT\nInvoices will be submitted monthly. Payment terms are Net 30 days from date of invoice receipt.\n\n5. GOVERNING LAW\nThis Agreement shall be governed by the laws of the State of Delaware."
        ]
    },
    {
        "filename": "Employee_Policy.pdf",
        "title": "Global Employee Workplace Policy",
        "pages": [
            "GLOBAL EMPLOYEE WORKPLACE POLICY\n\n1. WORKING HOURS & ATTENDANCE\nThe standard workweek is 40 hours, Monday through Friday. Core operating hours are 9:00 AM to 5:00 PM local time.\n\n2. REMOTE WORK GUIDELINES\nEligible employees may work remotely up to two (2) days per week with direct manager approval. High-speed secure broadband and compliance with data protection rules are mandatory.",
            "3. PAID TIME OFF (PTO)\nFull-time personnel accrue twenty (20) days of paid annual leave per calendar year. Unused leave up to five (5) days may carry over to the subsequent year.\n\n4. CODE OF ETHICS\nAll staff must maintain respect, fairness, and zero tolerance for discrimination, harassment, or retaliation in all interactions."
        ]
    },
    {
        "filename": "Finance_Invoice.pdf",
        "title": "Q3 Enterprise Infrastructure Invoice",
        "pages": [
            "ENTERPRISE BILLING STATEMENT & INVOICE\n\nInvoice Number: INV-2026-8921\nDate: September 15, 2026\nBilled To: Enterprise Document Automation Division\nVendor: CloudScale Infrastructure Corp\n\nLINE ITEMS:\n1. Dedicated GPU Inference Cluster (3 Months) - $85,000.00\n2. Enterprise High-Throughput NVMe Storage (500TB) - $42,500.00\n3. 24/7 Managed SRE Monitoring Support - $21,000.00\n\nTOTAL AMOUNT DUE: $148,500.00 USD",
            "PAYMENT TERMS & WIRE INSTRUCTIONS:\nPayment Terms: Net 45 Days.\nBank: First International Commerce Bank\nAccount: 4892-0091-7721\nRouting: 021000021\nSWIFT: FICBUS33\nTax ID (EIN): 84-2910391\nLate payment penalty: 1.5% per month on overdue balances."
        ]
    },
    {
        "filename": "Security_Policy.pdf",
        "title": "Corporate Information Security Policy",
        "pages": [
            "CORPORATE INFORMATION SECURITY & ACCESS POLICY\n\n1. PURPOSE\nTo protect organizational data assets, customer records, and network infrastructure from unauthorized access, breach, and digital threats.\n\n2. PASSWORD REQUIREMENTS\nAll system passwords must contain a minimum of 14 characters, combining uppercase, lowercase, numbers, and special symbols. Passwords must be rotated every 90 days.",
            "3. MULTI-FACTOR AUTHENTICATION (MFA)\nHardware-backed or authenticator-app MFA is mandatory across all workstations, VPN connections, and cloud dashboards. SMS-based MFA is prohibited.\n\n4. INCIDENT REPORTING\nAny suspected security incident or lost device must be reported to sec-ops@example.com within two (2) hours of discovery."
        ]
    },
    {
        "filename": "Executive_Contract.pdf",
        "title": "Executive Employment Agreement - Confidential",
        "pages": [
            "CONFIDENTIAL EXECUTIVE EMPLOYMENT AGREEMENT\n\nClassification: RESTRICTED / HIGHLY CONFIDENTIAL\nDepartment: LEGAL / EXECUTIVE\n\nParties: Enterprise Corporation and Chief Executive Officer.\n\n1. COMPENSATION & INCENTIVES\nBase compensation shall be $650,000 annually. Target annual performance incentive is 100% of base salary subject to board milestones.\n\n2. EQUITY INCENTIVES\nGrant of 250,000 stock options vesting over four years with a 1-year cliff.",
            "3. TERMINATION CONDITIONS & SEVERANCE\nThe executive agreement provides 90 days written notice for termination without cause and full golden parachute provisions. Upon termination without cause or change of control, the executive shall receive eighteen (18) months of base salary continuation, full acceleration of all unvested equity awards, and 24 months of executive healthcare continuation.\n\n4. NON-COMPETE COVENANTS\nThe executive agrees not to engage in competing business activities for a period of twenty-four (24) months following separation."
        ]
    }
]

def main():
    for doc_info in DOCS:
        filepath = os.path.join(SAMPLES_DIR, doc_info["filename"])
        pdf_doc = pymupdf.open()
        for page_text in doc_info["pages"]:
            page = pdf_doc.new_page(width=595, height=842)  # A4 size
            # Insert title and text
            rect = pymupdf.Rect(50, 50, 545, 792)
            page.insert_textbox(rect, page_text, fontsize=12, fontname="helv")
        pdf_doc.save(filepath)
        pdf_doc.close()
        print(f"Generated: {filepath} ({len(doc_info['pages'])} pages)")

if __name__ == "__main__":
    main()
