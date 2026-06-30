# Data Breach Response Procedure

**Status**: Active
**Last Updated**: 2026-05-28
**POPIA Reference**: Section 22 - Security Safeguards; Section 23 - Notification of Security Compromises

## Purpose

This document outlines EduBoost SA's procedures for detecting, assessing, and responding to data breaches in accordance with the Protection of Personal Information Act (POPIA) requirements.

## Definitions

### Data Breach

A data breach is a security incident that results in the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to personal information transmitted, stored, or otherwise processed.

### Affected Data Subject

An individual whose personal information has been involved in a data breach.

### Information Regulator

The South African Information Regulator established under POPIA.

## Breach Response Team

### Core Team

- **Incident Response Lead**: [REQUIRED BEFORE LAUNCH]
- **Information Officer**: [REQUIRED BEFORE LAUNCH]
- **Technical Lead**: [REQUIRED BEFORE LAUNCH]
- **Legal Counsel**: [REQUIRED BEFORE LAUNCH]
- **Communications Lead**: [REQUIRED BEFORE LAUNCH]

### Responsibilities

- **Incident Response Lead**: Coordinate response, manage timeline, ensure procedure compliance
- **Information Officer**: Assess POPIA implications, decide on regulator notification
- **Technical Lead**: Investigate technical cause, implement containment measures
- **Legal Counsel**: Assess legal obligations, advise on notification requirements
- **Communications Lead**: Prepare communications to affected parties and public

## Detection and Reporting

### Detection Channels

Data breaches may be detected through:

- **Automated Monitoring**: Security alerts, anomaly detection, intrusion detection systems
- **Internal Reports**: Staff reports, security team findings
- **External Reports**: Third-party reports, user reports, media reports
- **Audits**: Regular security audits, penetration testing

### Initial Reporting

Any suspected data breach must be reported immediately to the Incident Response Lead via:

- **Email**: [REQUIRED BEFORE LAUNCH]
- **Phone**: [REQUIRED BEFORE LAUNCH]
- **Emergency Channel**: [REQUIRED BEFORE LAUNCH]

### Initial Report Contents

The initial report should include:

- Date and time of detection
- Nature of the suspected breach
- Systems or data potentially affected
- Initial assessment of severity
- Reporter's contact information

## Severity Classification

### Severity Levels

**Low (Severity 1)**

- Limited scope (fewer than 10 data subjects)
- No evidence of data exfiltration
- No evidence of malicious intent
- Minimal risk of harm to data subjects

**Medium (Severity 2)**

- Moderate scope (10-100 data subjects)
- Possible data exfiltration
- Possible malicious intent
- Moderate risk of harm to data subjects

**High (Severity 3)**

- Large scope (100-1,000 data subjects)
- Likely data exfiltration
- Likely malicious intent
- High risk of harm to data subjects

**Critical (Severity 4)**

- Very large scope (more than 1,000 data subjects)
- Confirmed data exfiltration
- Confirmed malicious intent
- Very high risk of harm to data subjects
- Sensitive data involved (e.g., full names, contact details)

### Classification Timeline

Severity must be classified within 24 hours of initial report.

## Response Timeline

### Immediate Actions (0-4 hours)

1. **Containment**: Isolate affected systems to prevent further unauthorized access
2. **Preservation**: Preserve evidence (logs, systems, data) for investigation
3. **Assessment**: Begin initial assessment of scope and impact
4. **Notification**: Notify core breach response team

### Investigation (4-48 hours)

1. **Root Cause Analysis**: Determine how the breach occurred
2. **Scope Assessment**: Identify all affected systems and data subjects
3. **Data Assessment**: Determine what personal information was compromised
4. **Impact Assessment**: Assess potential harm to affected data subjects
5. **Classification**: Finalize severity classification

### Decision Making (48-72 hours)

1. **Regulator Notification**: Decide whether to notify the Information Regulator
2. **Data Subject Notification**: Decide whether to notify affected data subjects
3. **Public Communication**: Decide whether to issue a public statement
4. **Remediation Plan**: Develop plan to address root cause and prevent recurrence

### Notification (72 hours - 7 days)

1. **Regulator Notification**: Notify Information Regulator if required
2. **Data Subject Notification**: Notify affected data subjects if required
3. **Public Communication**: Issue public statement if required
4. **Stakeholder Communication**: Notify relevant stakeholders

### Post-Incident (7-30 days)

1. **Remediation**: Implement remediation plan
2. **Documentation**: Complete incident report and documentation
3. **Review**: Conduct post-incident review
4. **Process Improvement**: Update procedures based on lessons learned

## Regulator Notification

### Notification Triggers

The Information Regulator must be notified when:

- The breach involves the personal information of more than 10 data subjects
- The breach poses a real risk of harm to data subjects
- The breach involves sensitive personal information
- The breach involves the unauthorized disclosure of personal information

### Notification Timeline

Regulator notification must be made as soon as reasonably possible, and no later than 72 hours after becoming aware of the breach.

### Notification Contents

The notification to the Information Regulator must include:

- Description of the nature of the breach
- Approximate number of affected data subjects
- Categories of personal information involved
- Likely consequences of the breach
- Measures taken or proposed to address the breach
- Measures taken or proposed to mitigate any adverse effects

### Notification Method

Regulator notification should be made via:

- **Email**: inforeg@justice.gov.za
- **Phone**: +27 12 315 5000
- **Online**: https://www.justice.gov.za/inforeg

## Data Subject Notification

### Notification Triggers

Affected data subjects must be notified when:

- The breach poses a real risk of harm to the data subject
- The breach involves sensitive personal information
- The breach involves the unauthorized disclosure of personal information

### Notification Timeline

Data subject notification must be made without undue delay after becoming aware of the breach.

### Notification Contents

The notification to affected data subjects must include:

- Description of the breach in clear and plain language
- Categories of personal information involved
- Likely consequences of the breach
- Measures taken or proposed to address the breach
- Measures the data subject can take to mitigate adverse effects
- Contact information for further inquiries

### Notification Method

Data subject notification should be made via:

- **Email**: Primary method for email addresses on file
- **SMS**: Secondary method for mobile numbers on file
- **Physical Mail**: For sensitive breaches or when electronic contact is unavailable
- **Website**: Public posting for large-scale breaches

## Evidence Preservation

### What to Preserve

- System logs (application, server, network)
- Database records (before and after breach)
- Access logs
- Authentication logs
- Configuration files
- Memory dumps (if applicable)
- Network traffic captures (if applicable)

### Preservation Methods

- **Read-Only Copies**: Create read-only copies of all relevant data
- **Hash Verification**: Generate cryptographic hashes for all preserved data
- **Secure Storage**: Store preserved data in secure, access-controlled storage
- **Chain of Custody**: Document chain of custody for all preserved evidence

### Retention Period

Preserved evidence must be retained for at least 7 years in accordance with POPIA requirements.

## Post-Incident Review

### Review Objectives

- Identify root cause of the breach
- Assess effectiveness of response
- Identify areas for improvement
- Update procedures and controls
- Provide training if needed

### Review Timeline

Post-incident review must be completed within 30 days of breach containment.

### Review Participants

- Incident Response Lead
- Information Officer
- Technical Lead
- Legal Counsel
- Relevant operational staff

### Review Outputs

- Incident report
- Root cause analysis
- Lessons learned
- Recommended improvements
- Updated procedures (if needed)

## Documentation

### Incident Report

A comprehensive incident report must be created for every data breach, including:

- Executive summary
- Timeline of events
- Root cause analysis
- Impact assessment
- Response actions taken
- Notification decisions and actions
- Post-incident review findings
- Recommendations

### Report Retention

Incident reports must be retained for at least 7 years in accordance with POPIA requirements.

## Training and Awareness

### Training Requirements

All staff must receive training on:

- Data breach detection and reporting
- This breach response procedure
- Their specific roles and responsibilities
- POPIA notification requirements

### Training Frequency

- **New Hires**: During onboarding
- **All Staff**: Annually
- **Breach Response Team**: Semi-annually

## Testing and Drills

### Drill Frequency

Breach response drills must be conducted:

- **Tabletop Exercises**: Annually
- **Simulated Breaches**: Bi-annually

### Drill Objectives

- Test effectiveness of procedures
- Identify gaps in response capabilities
- Train breach response team
- Validate communication channels

## References

- POPIA Section 22: Security Safeguards
- POPIA Section 23: Notification of Security Compromises
- POPIA Section 24: Codes of Conduct
- Information Regulator Guidelines: https://www.justice.gov.za/inforeg
