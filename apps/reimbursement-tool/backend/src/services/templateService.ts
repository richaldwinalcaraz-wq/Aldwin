import { EmailTemplateType } from '../types';

export const TEMPLATE_LABELS: Record<EmailTemplateType, string> = {
  standard: 'Standard',
  informational: 'Informational (No Access)',
  follow_up: 'Follow-Up (Past Due)',
  resubmission: 'Resubmission',
  priority: 'Priority (Urgent)',
};

export function selectTemplate(notes: string): EmailTemplateType {
  const n = notes.trim().toLowerCase();
  if (n === 'no access') return 'informational';
  if (n === 'past due') return 'follow_up';
  if (n === 'resubmission') return 'resubmission';
  if (n === 'urgent') return 'priority';
  return 'standard';
}

export function buildEmailSubject(
  template: EmailTemplateType,
  companyName: string,
  period: string
): string {
  switch (template) {
    case 'informational':
      return `[No Access Notice] Reimbursement Report – ${companyName} ${period}`;
    case 'follow_up':
      return `[Past Due] Reimbursement Report Follow-Up – ${companyName} ${period}`;
    case 'resubmission':
      return `[Resubmission Required] Reimbursement Report – ${companyName} ${period}`;
    case 'priority':
      return `[URGENT] Reimbursement Report – ${companyName} ${period}`;
    default:
      return `Reimbursement Report – ${companyName} ${period}`;
  }
}

function getCurrentPeriod(): string {
  const now = new Date();
  return now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

export function buildEmailHtml(params: {
  template: EmailTemplateType;
  companyName: string;
  total: string;
  currency: string;
  totalToCharge: string;
  pastDue: string;
  notes: string;
  sentBy: string;
  period?: string;
}): string {
  const {
    template,
    companyName,
    total,
    currency,
    totalToCharge,
    pastDue,
    sentBy,
    period = getCurrentPeriod(),
  } = params;

  const baseStyle = `
    font-family: Arial, Helvetica, sans-serif;
    font-size: 14px;
    color: #1a1a1a;
    line-height: 1.6;
    max-width: 680px;
  `;

  const headerColors: Record<EmailTemplateType, string> = {
    standard: '#1a1a2e',
    informational: '#2c3e50',
    follow_up: '#c0392b',
    resubmission: '#e67e22',
    priority: '#8e0000',
  };

  const headerColor = headerColors[template];

  const headerSection = `
    <div style="background:${headerColor};padding:24px 32px;border-radius:4px 4px 0 0;">
      <h2 style="color:#ffffff;margin:0;font-size:18px;font-weight:600;">
        Reimbursement Report – ${period}
      </h2>
      <p style="color:rgba(255,255,255,0.75);margin:4px 0 0;font-size:13px;">${companyName}</p>
    </div>
  `;

  const footerSection = `
    <div style="border-top:1px solid #e5e7eb;padding:16px 32px;background:#f9fafb;border-radius:0 0 4px 4px;">
      <p style="margin:0;font-size:12px;color:#6b7280;">
        Sent by: <strong>${sentBy}</strong> &nbsp;|&nbsp; ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
      </p>
      <p style="margin:6px 0 0;font-size:11px;color:#9ca3af;">
        This is an automated reimbursement notification. Please do not reply to this email directly.
      </p>
    </div>
  `;

  let bodyContent = '';

  switch (template) {
    case 'standard':
      bodyContent = `
        <p>Dear Client,</p>
        <p>Please find attached your reimbursement report for <strong>${period}</strong>.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#f3f4f6;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Company</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${companyName}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Billing Period</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${period}</td>
          </tr>
          <tr style="background:#f3f4f6;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Total Billed</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${currency} ${total}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Amount to Charge</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${totalToCharge || 'See attached report'}</td>
          </tr>
        </table>
        <p>Please review the attached PDF for detailed billing information. If you have any questions or concerns, please reach out to our team.</p>
      `;
      break;

    case 'informational':
      bodyContent = `
        <p>Dear Client,</p>
        <p>We are writing to inform you that <strong>no system access</strong> was recorded for <strong>${companyName}</strong> during <strong>${period}</strong>.</p>
        <p>As a result, there are no billable reimbursement charges for this period. No invoice or PDF report is attached.</p>
        <p>If you believe this is an error or if you did access the system, please contact our team immediately so we can review your account records.</p>
        <p>We will continue to monitor and will send a report once activity is detected.</p>
      `;
      break;

    case 'follow_up':
      bodyContent = `
        <p>Dear Client,</p>
        <p>This is a <strong>follow-up notice</strong> regarding an outstanding balance on your account for <strong>${period}</strong>.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#fef2f2;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #fecaca;color:#c0392b;">Past Due Balance</td>
            <td style="padding:10px 14px;border:1px solid #fecaca;font-weight:700;color:#c0392b;">${pastDue || 'See attached report'}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Total Billed</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${currency} ${total}</td>
          </tr>
          <tr style="background:#f3f4f6;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Amount to Charge</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${totalToCharge || 'See attached report'}</td>
          </tr>
        </table>
        <p>Please review the attached reimbursement report and arrange payment at your earliest convenience. If you have already settled this balance, please disregard this notice.</p>
        <p>For payment arrangements or disputes, please contact our billing team promptly.</p>
      `;
      break;

    case 'resubmission':
      bodyContent = `
        <p>Dear Client,</p>
        <p>We are reaching out regarding your reimbursement report for <strong>${period}</strong>. A <strong>resubmission is required</strong> for <strong>${companyName}</strong>.</p>
        <p>The attached report contains updated billing information that requires your review and acknowledgment.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#fff7ed;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #fed7aa;color:#c2410c;">Action Required</td>
            <td style="padding:10px 14px;border:1px solid #fed7aa;color:#c2410c;">Report Resubmission</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Total Billed</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${currency} ${total}</td>
          </tr>
        </table>
        <p>Please review the attached PDF and confirm receipt. Contact our team if you have any discrepancies to report.</p>
      `;
      break;

    case 'priority':
      bodyContent = `
        <p>Dear Client,</p>
        <p style="color:#8e0000;font-weight:600;">⚠ URGENT: Immediate action is required regarding your reimbursement account.</p>
        <p>This is a priority notification for <strong>${companyName}</strong> for the billing period <strong>${period}</strong>.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#fef2f2;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #fecaca;color:#8e0000;">Priority Status</td>
            <td style="padding:10px 14px;border:1px solid #fecaca;font-weight:700;color:#8e0000;">URGENT</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Total Billed</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${currency} ${total}</td>
          </tr>
          <tr style="background:#f3f4f6;">
            <td style="padding:10px 14px;font-weight:600;border:1px solid #e5e7eb;">Amount to Charge</td>
            <td style="padding:10px 14px;border:1px solid #e5e7eb;">${totalToCharge || 'See attached report'}</td>
          </tr>
        </table>
        <p>Please review the attached reimbursement report immediately and respond to our billing team within <strong>24 hours</strong>.</p>
      `;
      break;
  }

  return `
    <div style="${baseStyle}">
      ${headerSection}
      <div style="padding:24px 32px;background:#ffffff;border:1px solid #e5e7eb;border-top:none;border-bottom:none;">
        ${bodyContent}
      </div>
      ${footerSection}
    </div>
  `;
}
