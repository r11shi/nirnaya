"""Nirnaya — Curated Indian Scam & Legitimate Message Dataset.

This module provides a real, curated dataset of Indian financial scam messages
and legitimate financial messages for:
1. Training the TF-IDF + LogReg classifier
2. Seeding the semantic scam retrieval index
3. Evaluation benchmarks (precision, recall, F1, FPR)

Every message is real or closely modeled on real Indian scam patterns.
No fabricated metrics. The dataset is versioned and extensible.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class MessageCategory(str, Enum):
    """Scam and legitimate message categories."""
    # Scam categories
    KYC_PHISHING = "kyc_phishing"
    OTP_THEFT = "otp_theft"
    LOTTERY_PRIZE = "lottery_prize"
    LOAN_FRAUD = "loan_fraud"
    REFUND_SCAM = "refund_scam"
    REMOTE_ACCESS = "remote_access"
    INVESTMENT_SCAM = "investment_scam"
    JOB_SCAM = "job_scam"
    IMPERSONATION = "impersonation"
    UPI_FRAUD = "upi_fraud"
    CUSTOMS_SCAM = "customs_scam"
    ELECTRICITY_SCAM = "electricity_scam"

    # Legitimate categories
    LEGIT_BANK_ALERT = "legit_bank_alert"
    LEGIT_OTP = "legit_otp"
    LEGIT_DELIVERY = "legit_delivery"
    LEGIT_PAYMENT = "legit_payment"
    LEGIT_BILL = "legit_bill"
    LEGIT_GOVERNMENT = "legit_government"
    LEGIT_MEDICAL = "legit_medical"
    LEGIT_INVESTMENT = "legit_investment"


@dataclass
class LabeledMessage:
    text: str
    is_scam: bool
    category: MessageCategory
    tags: List[str]  # additional metadata


# ─── SCAM MESSAGES ──────────────────────────────────────────
# Each message is modeled on real Indian scam patterns documented by
# RBI, NPCI, cybercrime.gov.in, and news reports.

SCAM_MESSAGES: List[LabeledMessage] = [
    # === KYC Phishing ===
    LabeledMessage(
        text="Dear SBI customer, your account will be blocked within 24 hours due to incomplete KYC. Update immediately: http://sbi-kyc-update.tk",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url", "sbi"],
    ),
    LabeledMessage(
        text="URGENT: Your HDFC Bank account is temporarily suspended. Complete PAN card verification at hdfc-panverify.com to restore access.",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "pan", "fake_url", "hdfc"],
    ),
    LabeledMessage(
        text="RBI Alert: All bank customers must link Aadhaar before 30th. Failure will result in account freeze. Click: http://bit.ly/rbi-aadhaar",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["authority", "aadhaar", "shortened_url", "rbi"],
    ),
    LabeledMessage(
        text="Your ICICI account KYC is expired. Verify now to avoid deactivation: icici-verify.xyz. Call 9876543210 for help.",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["kyc", "fake_url", "icici", "phone"],
    ),
    LabeledMessage(
        text="Attention: Your Axis Bank a/c will be permanently closed due to non-compliance with KYC norms. Submit documents at axis-support.net immediately.",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url", "axis"],
    ),
    LabeledMessage(
        text="Important Notice from PNB: Your account has been flagged for KYC non-compliance. Complete verification within 12 hours or face account suspension. Visit pnb-kyc-update.in",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url", "pnb"],
    ),
    LabeledMessage(
        text="Dear Customer, your Kotak bank account KYC is pending. Last date today. Update at kotak-kyc.com or your net banking will stop.",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url", "kotak"],
    ),
    LabeledMessage(
        text="SBI se: Aapka account 48 ghante mein band ho jayega. KYC update karne ke liye click karein: http://sbi-update.co",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url", "sbi", "hinglish"],
    ),
    LabeledMessage(
        text="Your bank account will be blocked if you don't update your KYC. Click the link below to verify your identity and keep your account active. www.bank-kyc-verify.com",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url"],
    ),
    LabeledMessage(
        text="Last warning! Your UBI account will be deactivated tomorrow. Complete e-KYC at http://ubi-ekyc.in to continue banking services.",
        is_scam=True, category=MessageCategory.KYC_PHISHING,
        tags=["urgency", "kyc", "fake_url"],
    ),

    # === OTP Theft ===
    LabeledMessage(
        text="This is SBI customer care. We noticed suspicious activity on your account. Please share the OTP sent to your phone for verification.",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "authority", "sbi"],
    ),
    LabeledMessage(
        text="Dear customer, a refund of Rs.15000 is pending. To process, share the 6-digit OTP received on your mobile. - HDFC Bank",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "refund", "hdfc"],
    ),
    LabeledMessage(
        text="Your UPI PIN needs to be reset due to security update. Call 8899776655 and share your OTP for instant reset.",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "upi", "phone"],
    ),
    LabeledMessage(
        text="We are from RBI fraud department. Your account shows unauthorized transactions. Share your net banking password and OTP to block the account.",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "credential", "authority", "rbi"],
    ),
    LabeledMessage(
        text="Aapke account se Rs.49999 ka transaction hua hai. Agar yeh aapne nahi kiya toh turant OTP share karein verification ke liye.",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "hinglish", "urgency"],
    ),
    LabeledMessage(
        text="ALERT: Unauthorized login detected on your account. Share the OTP we just sent to verify your identity and secure your account immediately.",
        is_scam=True, category=MessageCategory.OTP_THEFT,
        tags=["otp", "urgency", "threat"],
    ),

    # === Lottery / Prize Scam ===
    LabeledMessage(
        text="Congratulations! You have won Rs.25,00,000 in the KBC Lottery. To claim your prize, pay Rs.5,000 registration fee. Contact: 9988776655",
        is_scam=True, category=MessageCategory.LOTTERY_PRIZE,
        tags=["reward", "payment", "phone"],
    ),
    LabeledMessage(
        text="Dear user, your mobile number has been selected for Rs.50 Lakh prize by Jio Lucky Draw 2026. Send Rs.2500 processing fee to claim.",
        is_scam=True, category=MessageCategory.LOTTERY_PRIZE,
        tags=["reward", "payment", "jio"],
    ),
    LabeledMessage(
        text="You won iPhone 16 Pro in Amazon Lucky Draw! Pay Rs.999 shipping charge to receive your prize. Click: amzon-prize.com",
        is_scam=True, category=MessageCategory.LOTTERY_PRIZE,
        tags=["reward", "payment", "fake_url", "amazon"],
    ),
    LabeledMessage(
        text="WINNER! You are selected in Google Annual Award 2026. Prize: $1,000,000. Email google.prize.claim@gmail.com with your bank details.",
        is_scam=True, category=MessageCategory.LOTTERY_PRIZE,
        tags=["reward", "credential", "google"],
    ),
    LabeledMessage(
        text="Paytm Cashback Offer! You won Rs.10,000 cashback. Claim now by paying Rs.500 processing fee. UPI: cashback@ybl",
        is_scam=True, category=MessageCategory.LOTTERY_PRIZE,
        tags=["reward", "payment", "upi", "paytm"],
    ),

    # === Loan Fraud ===
    LabeledMessage(
        text="Pre-approved personal loan of Rs.5,00,000 at 0% interest! No documents needed. Pay Rs.3,000 processing fee. Apply: http://instant-loan.in",
        is_scam=True, category=MessageCategory.LOAN_FRAUD,
        tags=["payment", "fake_url", "loan"],
    ),
    LabeledMessage(
        text="Get instant loan Rs.10 lakh in 5 minutes. No CIBIL check. No guarantor. Just pay Rs.5000 insurance fee. WhatsApp: 7766554433",
        is_scam=True, category=MessageCategory.LOAN_FRAUD,
        tags=["payment", "phone", "loan"],
    ),
    LabeledMessage(
        text="BAJAJ FINANCE: Your pre-approved loan of Rs.3,00,000 is ready for disbursal. Pay one-time Rs.2,999 verification charge. Contact: 8855667744",
        is_scam=True, category=MessageCategory.LOAN_FRAUD,
        tags=["payment", "phone", "authority", "loan"],
    ),

    # === Refund Scam ===
    LabeledMessage(
        text="Your refund of Rs.3,500 from Flipkart is pending. Click here to claim: http://flipkart-refund.co and enter your bank details.",
        is_scam=True, category=MessageCategory.REFUND_SCAM,
        tags=["refund", "fake_url", "credential", "flipkart"],
    ),
    LabeledMessage(
        text="Income Tax Department: Excess TDS of Rs.15,600 detected. Claim your refund at http://bit.ly/itrefund. Provide bank account and PAN.",
        is_scam=True, category=MessageCategory.REFUND_SCAM,
        tags=["refund", "authority", "shortened_url", "credential"],
    ),
    LabeledMessage(
        text="IRCTC Refund: Your cancelled ticket refund of Rs.2,450 failed. Re-initiate by entering card details at irctc-refund.xyz",
        is_scam=True, category=MessageCategory.REFUND_SCAM,
        tags=["refund", "fake_url", "credential"],
    ),

    # === Remote Access ===
    LabeledMessage(
        text="Sir, this is SBI tech support. We need to fix your net banking issue. Please install AnyDesk app and share the 9-digit code.",
        is_scam=True, category=MessageCategory.REMOTE_ACCESS,
        tags=["remote_access", "authority", "sbi"],
    ),
    LabeledMessage(
        text="To resolve your UPI payment issue, download TeamViewer Quick Support and share access code with our executive on call.",
        is_scam=True, category=MessageCategory.REMOTE_ACCESS,
        tags=["remote_access", "upi"],
    ),
    LabeledMessage(
        text="Your mobile banking app has a security vulnerability. Install this app for protection: http://secure-fix.apk. Our team will guide you remotely.",
        is_scam=True, category=MessageCategory.REMOTE_ACCESS,
        tags=["remote_access", "fake_url", "threat"],
    ),

    # === Investment Scam ===
    LabeledMessage(
        text="Join our WhatsApp group for guaranteed 50% monthly returns on stock market. No loss guarantee. Contact: 9955884477. Limited seats.",
        is_scam=True, category=MessageCategory.INVESTMENT_SCAM,
        tags=["reward", "phone", "investment"],
    ),
    LabeledMessage(
        text="Earn Rs.5000 daily from home. Just invest Rs.1000 in our crypto trading platform. 100% profit guaranteed. Visit: earnbig.co",
        is_scam=True, category=MessageCategory.INVESTMENT_SCAM,
        tags=["reward", "payment", "fake_url", "investment"],
    ),
    LabeledMessage(
        text="SEBI registered advisor (Reg: INH000XXXXX). Buy RELIANCE at 2800 target 5000. Guaranteed profit. Join premium group Rs.10000/month.",
        is_scam=True, category=MessageCategory.INVESTMENT_SCAM,
        tags=["authority", "payment", "investment"],
    ),

    # === Job Scam ===
    LabeledMessage(
        text="Work from home. Earn Rs.15000-50000/month. Just do copy paste work. Registration fee Rs.500 only. WhatsApp 8877665544",
        is_scam=True, category=MessageCategory.JOB_SCAM,
        tags=["reward", "payment", "phone", "job"],
    ),
    LabeledMessage(
        text="Amazon/Flipkart hiring! Data entry job Rs.30000/month. No experience needed. Pay Rs.1200 registration. Apply: job-apply.in",
        is_scam=True, category=MessageCategory.JOB_SCAM,
        tags=["payment", "fake_url", "authority", "job"],
    ),
    LabeledMessage(
        text="Congratulations! You are selected for Google internship. Stipend Rs.80000/month. Pay Rs.5000 for offer letter processing.",
        is_scam=True, category=MessageCategory.JOB_SCAM,
        tags=["reward", "payment", "authority", "job"],
    ),

    # === UPI Fraud ===
    LabeledMessage(
        text="I accidentally sent Rs.5000 to your UPI. Please return it to my account upi@ybl. I am in urgent need.",
        is_scam=True, category=MessageCategory.UPI_FRAUD,
        tags=["upi", "urgency", "payment"],
    ),
    LabeledMessage(
        text="To receive Rs.500 cashback, accept the UPI collect request from verifiedcashback@okaxis. Offer valid for 10 minutes only.",
        is_scam=True, category=MessageCategory.UPI_FRAUD,
        tags=["upi", "reward", "urgency"],
    ),
    LabeledMessage(
        text="Your PhonePe account will be deactivated. Verify by sending Rs.1 to admin@ybl. The amount will be refunded immediately.",
        is_scam=True, category=MessageCategory.UPI_FRAUD,
        tags=["upi", "urgency", "threat", "payment"],
    ),

    # === Electricity / Utility Scam ===
    LabeledMessage(
        text="Your electricity connection will be disconnected today due to pending bill. Pay immediately: WhatsApp 9966554433. Bill amount Rs.3,450.",
        is_scam=True, category=MessageCategory.ELECTRICITY_SCAM,
        tags=["urgency", "threat", "phone", "payment"],
    ),
    LabeledMessage(
        text="URGENT: Your electricity bill is overdue. Your power supply will be cut off tonight at 8 PM. Pay now at http://bill-pay.co to avoid disconnection.",
        is_scam=True, category=MessageCategory.ELECTRICITY_SCAM,
        tags=["urgency", "threat", "fake_url", "payment"],
    ),

    # === Customs / Courier Scam ===
    LabeledMessage(
        text="Your parcel is held at customs. Pay Rs.3000 customs duty to release. FedEx tracking: FX8899. Contact: 7788994455",
        is_scam=True, category=MessageCategory.CUSTOMS_SCAM,
        tags=["payment", "phone", "authority"],
    ),
    LabeledMessage(
        text="India Post: Your international package requires customs clearance fee of Rs.2500. Pay at http://indiapost-customs.in or it will be returned.",
        is_scam=True, category=MessageCategory.CUSTOMS_SCAM,
        tags=["payment", "fake_url", "authority", "urgency"],
    ),

    # === Impersonation ===
    LabeledMessage(
        text="Hi, this is your son Rahul. I lost my phone and wallet. Please urgently send Rs.20000 to this UPI: emergency@ybl. Will explain later.",
        is_scam=True, category=MessageCategory.IMPERSONATION,
        tags=["urgency", "upi", "payment", "impersonation"],
    ),
    LabeledMessage(
        text="I am calling from CBI. There is a money laundering case against your Aadhaar number. To avoid arrest, transfer Rs.50000 to our secure account immediately.",
        is_scam=True, category=MessageCategory.IMPERSONATION,
        tags=["authority", "threat", "payment", "urgency"],
    ),
]


# ─── LEGITIMATE MESSAGES ────────────────────────────────────
# These MUST NOT trigger fraud alerts. They are the false-positive benchmark.

LEGITIMATE_MESSAGES: List[LabeledMessage] = [
    # === Bank Alerts ===
    LabeledMessage(
        text="Your SBI account XX1234 has been credited with Rs.50,000.00. Available balance: Rs.1,25,000.00. If not done by you, call 1800-111-111.",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "credit", "sbi"],
    ),
    LabeledMessage(
        text="Rs.2,500.00 debited from your HDFC Bank A/c XX5678 on 15-Aug-2026. UPI Ref: 123456789012. Not you? Call 1800-XXX-XXXX",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "debit", "hdfc"],
    ),
    LabeledMessage(
        text="ICICI Bank: Your FD of Rs.1,00,000 has been renewed for 1 year at 7.10% p.a. Maturity amount: Rs.1,07,100. Ref: FD20268899",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "fd", "icici"],
    ),
    LabeledMessage(
        text="Your Axis Bank credit card XX9876 payment of Rs.15,000 is due on 25-Aug-2026. Pay now to avoid late fee.",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "credit_card", "axis"],
    ),
    LabeledMessage(
        text="SBI: Your cheque no. 123456 for Rs.10,000 has been cleared. Available balance: Rs.45,000. -SBI",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "cheque", "sbi"],
    ),
    LabeledMessage(
        text="Alert: A new beneficiary RAVI KUMAR has been added to your HDFC net banking. If not you, call 1800-XXX-XXXX immediately.",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "beneficiary", "hdfc"],
    ),
    LabeledMessage(
        text="Your Kotak 811 savings account interest of Rs.1,250.00 has been credited for the quarter ending Jun 2026.",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "interest", "kotak"],
    ),
    LabeledMessage(
        text="EMI of Rs.12,500 for Home Loan A/c XXXX1234 has been debited from your SBI account. Next EMI due: 05-Sep-2026.",
        is_scam=False, category=MessageCategory.LEGIT_BANK_ALERT,
        tags=["bank", "emi", "sbi"],
    ),

    # === Legitimate OTPs ===
    LabeledMessage(
        text="Your OTP for SBI Internet Banking login is 456789. Valid for 5 minutes. Do NOT share with anyone. - SBI",
        is_scam=False, category=MessageCategory.LEGIT_OTP,
        tags=["otp", "sbi"],
    ),
    LabeledMessage(
        text="123456 is your OTP for transaction of Rs.2000 on Flipkart. OTP valid for 10 mins. Do not share. -HDFCBK",
        is_scam=False, category=MessageCategory.LEGIT_OTP,
        tags=["otp", "hdfc", "flipkart"],
    ),
    LabeledMessage(
        text="Your OTP for Aadhaar authentication is 987654. This OTP is valid for 10 minutes. Do not share this OTP with anyone. -UIDAI",
        is_scam=False, category=MessageCategory.LEGIT_OTP,
        tags=["otp", "aadhaar", "uidai"],
    ),
    LabeledMessage(
        text="Your one-time password for Google sign-in is 345678. Don't share it with anyone.",
        is_scam=False, category=MessageCategory.LEGIT_OTP,
        tags=["otp", "google"],
    ),
    LabeledMessage(
        text="OTP for your IRCTC booking is 654321. Valid for 5 minutes. Do not share. -IRCTC",
        is_scam=False, category=MessageCategory.LEGIT_OTP,
        tags=["otp", "irctc"],
    ),

    # === Delivery Notifications ===
    LabeledMessage(
        text="Your Amazon order #123-456-789 has been shipped. Expected delivery: 22-Aug-2026. Track: https://www.amazon.in/track",
        is_scam=False, category=MessageCategory.LEGIT_DELIVERY,
        tags=["delivery", "amazon"],
    ),
    LabeledMessage(
        text="Flipkart: Your order FLK123456 is out for delivery. Delivery partner: Wishmaster. Contact: 98XXXXXXXX",
        is_scam=False, category=MessageCategory.LEGIT_DELIVERY,
        tags=["delivery", "flipkart"],
    ),
    LabeledMessage(
        text="Swiggy: Your food order from Biryani House is being prepared. Estimated delivery in 35 mins.",
        is_scam=False, category=MessageCategory.LEGIT_DELIVERY,
        tags=["delivery", "swiggy"],
    ),
    LabeledMessage(
        text="India Post: Your Speed Post EE123456789IN is out for delivery today. -IndiaPost",
        is_scam=False, category=MessageCategory.LEGIT_DELIVERY,
        tags=["delivery", "indiapost"],
    ),

    # === Payment Confirmations ===
    LabeledMessage(
        text="Rs.500 paid to DMART via UPI. UPI Ref: 2608XXXXX. Debit A/c: XX1234. If not done by you, contact bank.",
        is_scam=False, category=MessageCategory.LEGIT_PAYMENT,
        tags=["payment", "upi"],
    ),
    LabeledMessage(
        text="Payment of Rs.1,200 received from RAMESH KUMAR via UPI. Credited to your Paytm Payments Bank account.",
        is_scam=False, category=MessageCategory.LEGIT_PAYMENT,
        tags=["payment", "upi", "paytm"],
    ),
    LabeledMessage(
        text="PhonePe: Rs.350.00 paid to Uber India. UPI Ref: 260812345678. Balance: Rs.4,650.",
        is_scam=False, category=MessageCategory.LEGIT_PAYMENT,
        tags=["payment", "upi", "phonepe"],
    ),
    LabeledMessage(
        text="Google Pay: You paid Rs.999 to Netflix. Transaction ID: GPay123456789.",
        is_scam=False, category=MessageCategory.LEGIT_PAYMENT,
        tags=["payment", "gpay", "netflix"],
    ),

    # === Bill / Utility Notifications ===
    LabeledMessage(
        text="Your Jio postpaid bill of Rs.599 is generated for Aug 2026. Due date: 25-Aug-2026. Pay on MyJio app or jio.com",
        is_scam=False, category=MessageCategory.LEGIT_BILL,
        tags=["bill", "jio"],
    ),
    LabeledMessage(
        text="BESCOM: Your electricity bill for Aug 2026 is Rs.1,850. Due date: 30-Aug-2026. Pay at bescom.karnataka.gov.in",
        is_scam=False, category=MessageCategory.LEGIT_BILL,
        tags=["bill", "electricity"],
    ),
    LabeledMessage(
        text="Your Airtel broadband bill of Rs.999 has been auto-debited from HDFC A/c XX5678. Next billing: 15-Sep-2026.",
        is_scam=False, category=MessageCategory.LEGIT_BILL,
        tags=["bill", "airtel", "auto_debit"],
    ),

    # === Government / Official ===
    LabeledMessage(
        text="Your Income Tax Return for AY 2026-27 has been successfully filed. Acknowledgement No: CPC/12345/2026. -Income Tax Dept",
        is_scam=False, category=MessageCategory.LEGIT_GOVERNMENT,
        tags=["government", "tax"],
    ),
    LabeledMessage(
        text="Your PAN card application is under process. Application No: NSDLPAN123456. Track at tin-nsdl.com",
        is_scam=False, category=MessageCategory.LEGIT_GOVERNMENT,
        tags=["government", "pan"],
    ),
    LabeledMessage(
        text="DigiLocker: Your driving licence has been successfully linked to your DigiLocker account.",
        is_scam=False, category=MessageCategory.LEGIT_GOVERNMENT,
        tags=["government", "digilocker"],
    ),

    # === Medical ===
    LabeledMessage(
        text="Reminder: Your appointment with Dr. Sharma at Apollo Hospital is scheduled for 22-Aug-2026 at 10:30 AM. -Apollo Hospitals",
        is_scam=False, category=MessageCategory.LEGIT_MEDICAL,
        tags=["medical", "appointment"],
    ),
    LabeledMessage(
        text="Your lab report from SRL Diagnostics is ready. Download at https://reports.srl.in/XXXXX. Report ID: SRL2026XXXX",
        is_scam=False, category=MessageCategory.LEGIT_MEDICAL,
        tags=["medical", "lab_report"],
    ),

    # === Investment ===
    LabeledMessage(
        text="Your SIP of Rs.5,000 in Axis Bluechip Fund has been successfully processed for Aug 2026. Folio: 12345/67. -Axis MF",
        is_scam=False, category=MessageCategory.LEGIT_INVESTMENT,
        tags=["investment", "sip", "mutual_fund"],
    ),
    LabeledMessage(
        text="Zerodha: Buy order executed. 10 shares of RELIANCE at Rs.2,850.50. Order ID: 260820XXXXX.",
        is_scam=False, category=MessageCategory.LEGIT_INVESTMENT,
        tags=["investment", "stock", "zerodha"],
    ),
    LabeledMessage(
        text="Your PPF account has been credited with Rs.1,50,000 for FY 2026-27. Current balance: Rs.8,50,000. -SBI",
        is_scam=False, category=MessageCategory.LEGIT_INVESTMENT,
        tags=["investment", "ppf", "sbi"],
    ),
    LabeledMessage(
        text="Groww: Your mutual fund redemption of Rs.25,000 from HDFC Mid Cap Fund has been processed. Amount will be credited in 2-3 business days.",
        is_scam=False, category=MessageCategory.LEGIT_INVESTMENT,
        tags=["investment", "redemption", "groww"],
    ),
]


def get_dataset() -> Tuple[List[str], List[int], List[str]]:
    """Get the full dataset as (texts, labels, categories).

    Returns:
        texts: list of message strings
        labels: list of 0 (legit) or 1 (scam)
        categories: list of category strings
    """
    all_messages = SCAM_MESSAGES + LEGITIMATE_MESSAGES
    texts = [m.text for m in all_messages]
    labels = [1 if m.is_scam else 0 for m in all_messages]
    categories = [m.category.value for m in all_messages]
    return texts, labels, categories


def get_scam_corpus() -> List[str]:
    """Get just the scam messages for embedding/retrieval index."""
    return [m.text for m in SCAM_MESSAGES]


def get_legitimate_corpus() -> List[str]:
    """Get just the legitimate messages for false-positive testing."""
    return [m.text for m in LEGITIMATE_MESSAGES]


def get_dataset_stats() -> Dict:
    """Get dataset statistics."""
    return {
        "total": len(SCAM_MESSAGES) + len(LEGITIMATE_MESSAGES),
        "scam": len(SCAM_MESSAGES),
        "legitimate": len(LEGITIMATE_MESSAGES),
        "scam_categories": len(set(m.category for m in SCAM_MESSAGES)),
        "legit_categories": len(set(m.category for m in LEGITIMATE_MESSAGES)),
        "scam_breakdown": {
            cat.value: sum(1 for m in SCAM_MESSAGES if m.category == cat)
            for cat in MessageCategory if any(m.category == cat for m in SCAM_MESSAGES)
        },
        "legit_breakdown": {
            cat.value: sum(1 for m in LEGITIMATE_MESSAGES if m.category == cat)
            for cat in MessageCategory if any(m.category == cat for m in LEGITIMATE_MESSAGES)
        },
    }
