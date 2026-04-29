import random
from datetime import datetime, timedelta
from database.db import get_connection


def _preview_text(full_text, length=120):
    s = (full_text or '').strip()
    if len(s) <= length:
        return s
    return s[:length] + '…'


def recompute_statistics():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) AS c, COALESCE(SUM(is_phishing),0) AS ph FROM analyses')
    row = cur.fetchone()
    total = row['c'] if row else 0
    ph = int(row['ph']) if row else 0
    leg = total - ph
    cur.execute(
        '''
        UPDATE statistics
        SET total_analyzed = ?, total_phishing = ?, total_legitimate = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = 1
        ''',
        (total, ph, leg),
    )
    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) AS c FROM analyses')
    if cur.fetchone()['c'] > 0:
        conn.close()
        recompute_statistics()
        return
    conn.close()

    now = datetime.now()
    conf_vals = [round(random.uniform(0.87, 0.99), 2) for _ in range(30)]

    phishing_bodies = [
        (
            'Dear client, the National Bank of Saudi Arabia has detected an outdated security profile. '
            'To avoid service interruption you must re-enter your full card number, expiry date, and CVN on the secure link below. '
            'This action is required within two hours. Failure to comply will result in permanent account lock and loss of all balances. '
            'Our fraud team is monitoring this message. Click verify now to continue without delay today.'
        ),
        (
            'PayPal service alert: unusual activity on your account from a new device. '
            'To prevent suspension we need you to confirm your identity. Open the form and type your current password, security questions, and national ID. '
            'This is a one-time verification. If you ignore this message your funds may be sent to a recovery queue and delayed for weeks. '
            'We apologize for the inconvenience. Take action now to stay protected always.'
        ),
        (
            'Congratulations! You are the lucky grand prize winner of our annual electronics lottery worth five thousand US dollars. '
            'To claim, pay a small processing fee and upload your personal ID. Our courier can deliver the prize within seven days after fee clearance. '
            'Do not share this with anyone. Limited time offer. Click claim reward before the timer expires. '
            'Support team is standing by 24/7 in case of questions. Good luck to you today.'
        ),
        (
            'Amazon billing department: we could not charge your last order because your default card expired. '
            'All pending shipments will be cancelled in the next 24 hours unless you update your payment and login credentials. '
            'We may also disable Prime benefits until this is fixed. Log in to the attached portal to secure your account. '
            'Thank you for being a valued member of our marketplace. Act fast to avoid any disruption only.'
        ),
        (
            'Apple security: your Apple ID has been locked because someone attempted to sign in from Russia. '
            'To unlock, verify your full name, address, and password on this one-time page. This message will not repeat. '
            'If the account is not restored, your photos and backups may be deleted permanently. Never share this with anyone. '
            'Sincerely, Apple support automation team. Follow the link in this message right now to finish.'
        ),
        (
            'Microsoft 365: urgent sign-in review. We blocked a sign-in to your work mailbox from a suspicious address. '
            'If you did not make this sign-in, open the security portal and enter your password, backup codes, and phone. '
            'Administrators are notified. Failure to respond can lock you out of Teams and email for 48 hours. '
            'Thank you for using Microsoft 365. Stay safe with strong passwords every day. Click below now please.'
        ),
        (
            'The IRS has a pending refund. Our records show you are eligible for a tax deposit of 3,200 dollars. '
            'To receive the direct deposit you must fill your bank routing, account, and SSN in the form for validation. '
            'The window closes in 5 days. This is a government-secured website. We never ask for a fee for refunds. '
            'Beware of fake messages. This one is the official process. Type your data carefully and submit the form for processing soon.'
        ),
        (
            'I am the finance director. We need a wire of 12,000 dollars to a vendor to close a time-sensitive deal. '
            'I am in a meeting; please handle before noon. I will provide account details in the next line after you confirm. '
            'This is confidential. Do not call me; the board is watching and only email is allowed. Approve the transfer immediately. '
            'I trust you. After payment send me the reference number so we can close the file without delay. Thank you from management.'
        ),
        (
            'Netflix: your account could not be renewed because the card was declined. '
            'Re-enter card details, billing address, and password in our new checkout page. Your profile may be lost if the issue persists. '
            'We may delete watch history in countries where payment laws apply. This message is for your security only. '
            'We hope you keep enjoying the service. If you have questions, use our official link in this message only.'
        ),
        (
            'DHL: your package is on hold. Customs requires 28 dollars to release. Pay using the form or we return the parcel. '
            'The tracking code is in your app but will vanish in 2 days. Use credit card, debit, or online wallet. '
            'This is a standard procedure for international border controls. We apologize for the delay. After payment, delivery resumes. '
            'Do not reply to DHL; use only the system link. Thank you and have a good day from shipping only.'
        ),
        (
            'IT help desk: we are moving mailboxes. Your mailbox is over quota. Install the new agent from the link to expand storage. '
            'The agent may ask to disable your antivirus for minutes; this is required for migration. We complete migration tonight. '
            'If you skip this step, your old mail may be purged. Save important messages before 9 PM. Thanks for your cooperation team-wide. '
            'Your department manager is CC’d on a separate list. This message is mandatory for all employees now.'
        ),
        (
            'Chase: validate your new device. We noticed a login from an unknown device in California. If this is you, ignore. '
            'If not, secure your account by typing your user ID, password, and PIN on our new validation screen. We may restrict wires otherwise. '
            'Banks are under heavy fraud pressure; your safety matters. This link expires in 20 minutes. Never share codes with anyone, except our officers. '
            'Thank you for choosing Chase. We protect what matters. Click confirm device now in this secure email message today.'
        ),
        (
            'Your Facebook page will be removed for policy violations. To appeal, open the case manager and re-enter your password, '
            'your phone, and a photo of your ID. Our automated review is strict. The deadline is 6 hours. After that, your audience is lost. '
            'We are sorry to send this, but the community must stay safe. Use the only official form below. Sincerely, Meta support bot only here.'
        ),
        (
            'LinkedIn security: someone in China viewed your private profile. Log in to see the full name and connect request. '
            'To review the visitor you may need to grant temporary app access. This helps our fraud models. It will auto-disable after 24h. '
            'We care about your career network. This message is personal to you. Do not forward. Click the blue button to start review now. '
            'Thank you for using LinkedIn. We build trust through transparency. Stay safe. Click link today please.'
        ),
        (
            'Urgent: your iCloud will delete photos. Your storage is full and a billing card failed. Update billing and password, '
            'or your memories may be lost forever. Apple cannot recover them without payment. The fee is 0.99 the first month. '
            'This is a final warning. Our servers rotate backups weekly. You have no time to waste. We love our customers, but rules apply. '
            'Fix now. Go to the web page. Sign in. Save your family photos before they disappear today quickly.'
        ),
    ]

    legit_bodies = [
        (
            'Thank you for your recent order. Your order number 78432 has been confirmed. Items will leave our warehouse in two business days. '
            'You can track the shipment in your account under Orders. A receipt is attached as PDF. If you need a change, contact us before the ship time. '
            'We appreciate your business. This is an automated message from our e-commerce system. If you have questions, reply to support. '
            'We hope you enjoy the products. Sincerely, customer care team, official store, no action required to keep your order active.'
        ),
        (
            'Meeting reminder: project sync is scheduled for tomorrow at 10:00 in conference room B. The agenda is in the team drive. '
            'Please add any blockers to the document before the start. We will cover milestones, risk items, and next sprint. '
            'This invite is for internal staff only. No password or payment is requested. If you need a new slot, use the team calendar. '
            'We look forward to a productive session. See you at ten. This message is from the program office only.'
        ),
        (
            'This is a reminder of your medical appointment on March 3 at 2:00 PM with Dr. Hani at the central clinic. '
            'If you need to cancel, call at least 24 hours in advance. Please bring your insurance card. Parking is in lot C. '
            'We look forward to seeing you. This is a standard reminder from the clinic system. No links or payment are required here. '
            'For questions, call the front desk. Have a good day. This message is confidential per privacy rules only.'
        ),
        (
            'Your monthly home internet plan for 45 dollars was charged to your card ending in 8821. A PDF invoice is in your customer portal. '
            'The next billing date is the first of next month. You can view usage charts any time. If any charge looks wrong, call billing. '
            'Thank you for being our subscriber. This is a routine billing notice. No action is needed for successful payments. '
            'Sincerely, billing department, official service provider. You may unsubscribe from marketing in profile settings for optional mail from us only.'
        ),
        (
            'Tech Weekly: this week we cover Python 3.12, Flask, and data privacy tips. You can read the full issue on our site. '
            'We never ask for your password in email. This newsletter is opt-in. To stop messages, use the link in the footer. '
            'We hope the articles are useful. Our editors pick topics that help teams build safer applications. No attachments are included. '
            'Enjoy reading, and follow us for updates. Sincerely, Tech Weekly staff. This is a low-frequency digest only in official brand voice.'
        ),
        (
            'Welcome to our learning community. Your registration is complete. You can start from the main dashboard. '
            'The first course is an orientation that takes about 20 minutes. If you have trouble logging in, reset your password on the public page. '
            'We never ask for a fee to activate a free plan. This message is automated. If you get a suspicious request, report it. '
            'We are happy you joined. Sincerely, learning platform. Support is available in help center on weekdays. Have a good start and learn well from home.'
        ),
        (
            'Thanks for opening support case 9021. We read your message about a login issue. A specialist will reply within one business day. '
            'Please do not send passwords in email. We will ask for safe ways to verify if needed. Our office hours are 9-5. '
            'We appreciate your patience. This is an auto-receipt from the ticket system. The case is assigned to the queue. '
            'If urgent, use the after-hours number on our site. Sincerely, support. No payment is required for standard triage. Have a good day from our support team officially.'
        ),
        (
            'Your package has shipped. The carrier is FedEx. Tracking number 1Z999AA10123456784. The estimated delivery is Friday. '
            'We will email again when the item is out for delivery. You can also track in your account. Thank you for shopping with us. '
            'If you have questions about the order, use the order form in your account. This message is informational only. '
            'Sincerely, merchant shipping team. No action except tracking in your account is needed. Have a good day officially.'
        ),
        (
            'Weekly team report: 14 tickets were closed, 3 are blocked on vendor, and 2 are new from customers. The burndown looks healthy. '
            'Milestones for next week are in the internal wiki. Please update your section by Thursday. This message is for staff only. '
            'We do not request credentials by email. If someone asks, report it. Thanks for the hard work, everyone, from the project office only. '
            'Sincerely, PMO. Use the same internal site you use daily; this email does not add new logins. Have a good week in full safety policy today.'
        ),
        (
            'Your hotel reservation at Seaside Inn is confirmed. Check-in April 10, check-out April 12. A confirmation number is in your online profile. '
            'The hotel is downtown near the main station. Breakfast is included. Late cancellation may carry a small fee. '
            'We look forward to your stay. If you have special needs, call the front desk. This is a real confirmation, no action needed. '
            'Sincerely, booking partner, official OTA, please review details in the app. Do not pay anyone outside the platform. Enjoy a restful stay with full comfort and trust in our service today for you and your group only, thank you for booking, end of line.'
        ),
        (
            'This email confirms you signed up for the workshop: IoT security basics, room 4, on May 5 at 1 PM. Bring your laptop. '
            'Coffee and badges will be at the door. The agenda is on the event site. This is a free community session. We do not need your bank data. '
            'If you cannot come, please cancel in the form so we can free the seat. See you at the event. Sincerely, organizers, happy to host you. '
            'No attachments or money transfers are part of this registration. The venue address is in the public calendar on our site only, official notice here today, thank you, period.'
        ),
        (
            'Profile update success: we saved your new display name and job title. Visibility depends on the settings you selected. '
            'You can change this any time. We never call you to ask for a password. If you get such a call, hang up. '
            'This is a routine system notice. No action is required. Sincerely, account services. This message only informs you and keeps your record right. '
            'Thank you for using our product. This email was sent to your verified address for account security, not for marketing, so we keep it direct from the system only today, officially, end, stop.'
        ),
        (
            'Backup report: the nightly backup to cloud storage completed without errors. Next run is in 24 hours. Contact IT if a restore is needed. '
            'The backup covers shared drives, not private downloads. This is a standard internal health email. We do not include web links in this type of mail. '
            'If a restore is urgent, use the help desk. Sincerely, IT. No credentials are requested. Have a good week from operations, policy applies per intranet, standard internal use only, end of system notice, period today officially only here final line, thank you, stop.'
        ),
        (
            'We received your return request for order 55601. A prepaid label is in your account. Please drop the package at any carrier point. '
            'The refund is processed five business days after the item is scanned. This is a normal process. We do not ask for wire or gift cards. '
            'Sincerely, returns, official merchant. This message is only about your RMA, nothing else, no other forms or logins, just use the label in your order page for this case today only, thank you, end, stop.'
        ),
        (
            'The quarterly all-hands is set for next Thursday at 3:00. The CEO will give updates, then we will have a short question and answer session. '
            'The meeting is on Teams; the link is in the calendar. No one will ask for your password in chat. This is a normal internal invite. '
            'Please join on time. Sincerely, internal comms, official corporate mail. We look forward to seeing you, no payments in the meeting, only work updates, security reminder only as usual, end, thank you, stop.'
        ),
    ]

    conn = get_connection()
    cur = conn.cursor()
    for i, body in enumerate(phishing_bodies):
        t = (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            '''
            INSERT INTO analyses (email_text, email_preview, result, is_phishing, confidence, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (body, _preview_text(body), 'تصيد احتيالي', 1, conf_vals[i] * 100, t),
        )
    for i, body in enumerate(legit_bodies):
        t = (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            '''
            INSERT INTO analyses (email_text, email_preview, result, is_phishing, confidence, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (body, _preview_text(body), 'بريد شرعي', 0, conf_vals[15 + i] * 100, t),
        )
    conn.commit()
    conn.close()
    recompute_statistics()
