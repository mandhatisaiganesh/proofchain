"""Synthetic demo documents for ProofChain.

These documents contain intentional contradictions and realistic relationships
to demonstrate ProofChain's commitment intelligence capabilities.
"""

DEMO_DOCUMENTS = {
    "RFP.md": """# Federal IT Infrastructure Modernization Services
## Request for Proposal (RFP) #FED-2024-0847

### 1. Overview
The Department of Federal Services (DFS) seeks a qualified vendor to provide comprehensive IT infrastructure modernization services including cloud migration, managed services, and ongoing technical support.

### 2. Scope of Work

#### 2.1 Technical Support Requirements
The vendor **must provide 24/7 technical support** with a guaranteed response time of 15 minutes for critical incidents (Priority 1) and 1 hour for high-priority incidents (Priority 2). Support must be available via phone, email, and a dedicated support portal.

#### 2.2 Security Requirements
- The vendor must hold current **ISO 27001 certification**
- The vendor must maintain **SOC 2 Type II** compliance
- The vendor must have **FedRAMP authorization** at the Moderate impact level
- All data must be encrypted at rest (AES-256) and in transit (TLS 1.3)
- The vendor must conduct quarterly penetration testing

#### 2.3 Deployment Timeline
The vendor must complete initial deployment **within 30 calendar days** of contract award. Full operational capability must be achieved within 60 calendar days.

#### 2.4 Staffing Requirements
- The vendor must provide a dedicated Program Manager
- Minimum 5 certified cloud engineers (AWS/Azure/GCP certified)
- Minimum 3 security engineers with CISSP or equivalent
- All personnel must hold active security clearances

#### 2.5 Service Level Agreements
- System availability: 99.95% uptime
- Mean Time to Recovery (MTTR): < 4 hours for critical systems
- Monthly SLA reporting to the government

#### 2.6 Compliance Requirements
- NIST 800-53 compliance
- FISMA compliance
- Section 508 accessibility compliance
- Regular compliance audits (quarterly)

### 3. Evaluation Criteria
- Technical approach (40%)
- Past performance (25%)
- Staffing and management (20%)
- Price (15%)

### 4. Contract Terms
- Base period: 12 months
- Option periods: 4 option years
- Contract start date: December 1, 2024
""",

    "Company_Profile.md": """# TechForward Solutions — Company Profile

## About Us
TechForward Solutions is a leading IT services provider with **12 years of experience** delivering enterprise technology solutions to government and commercial clients. Headquartered in Arlington, Virginia, we have **150 full-time employees** and maintain offices in Washington DC, Austin TX, and San Diego CA.

## Core Capabilities
- Cloud infrastructure design and migration (AWS, Azure)
- Managed IT services and support
- Cybersecurity consulting and operations
- Application modernization
- Data center operations

## Key Differentiators
- 12 years of federal IT experience
- Deep expertise in DoD and civilian agency environments
- Strong partnerships with AWS, Microsoft, and major technology vendors
- Proven track record of on-time, on-budget delivery

## Current Clients
- Department of Commerce (active)
- US Army Corps of Engineers (active)
- General Services Administration (active)
- 3 Fortune 500 commercial clients

## Financial Strength
- Annual revenue: $45M (FY2023)
- Year-over-year growth: 18%
- Dun & Bradstreet rated
- No outstanding legal actions

## Employee Statistics
- 150 full-time employees
- 85% technical staff
- Average employee tenure: 4.2 years
- Active security clearances: 78 employees
""",

    "Support_Policy.md": """# TechForward Solutions — Technical Support Policy
## Document Version 3.2 | Effective Date: January 2024

### 1. Support Hours
**Technical support is available during standard business hours: Monday through Friday, 8:00 AM to 6:00 PM Eastern Time.** Excluding federal holidays.

### 2. After-Hours Support
For critical production issues outside business hours, an on-call engineer can be reached via the emergency support line. **After-hours support is provided on a best-effort basis** and is not covered under standard SLAs. Response times for after-hours requests may be extended.

### 3. Support Tiers

#### Tier 1 — Help Desk
- First point of contact
- Basic troubleshooting
- Ticket creation and routing
- **Staffed during business hours only**

#### Tier 2 — Technical Support
- Advanced troubleshooting
- System administration
- Configuration changes
- **Available during business hours with limited after-hours coverage**

#### Tier 3 — Engineering
- Root cause analysis
- Architecture changes
- Vendor escalation
- **Business hours only, scheduled engagements**

### 4. Response Time SLAs
| Priority | Business Hours Response | After-Hours Response |
|----------|----------------------|---------------------|
| P1 - Critical | 30 minutes | Best effort (2-4 hours) |
| P2 - High | 2 hours | Next business day |
| P3 - Medium | 4 hours | Next business day |
| P4 - Low | 8 hours | Next business day |

### 5. Support Channels
- Email: support@techforward.example.com
- Phone: (703) 555-0142 (business hours)
- Portal: support.techforward.example.com
- Emergency Line: (703) 555-0199 (after hours, P1 only)

### 6. Current Support Staff
- 8 Tier 1 help desk analysts
- 5 Tier 2 support engineers
- 3 Tier 3 senior engineers
- Total support organization: **16 personnel**
""",

    "Certifications.md": """# TechForward Solutions — Certifications & Compliance

## Active Certifications

### ISO 27001:2022
- **Status: CERTIFIED**
- Certification Body: BSI Group
- Certificate Number: IS 750231
- Scope: IT Service Management and Cloud Operations
- Last Audit: March 2024
- Expiration: March 2027
- No non-conformities identified

### SOC 2 Type II
- **Status: CERTIFIED**
- Audit Period: January 2023 — December 2023
- Auditor: Deloitte & Touche LLP
- Trust Service Criteria: Security, Availability, Confidentiality
- Report Available: Upon NDA execution
- No exceptions noted

### CMMI Level 3
- **Status: CERTIFIED**
- Appraised: June 2023
- Valid Through: June 2026
- Scope: Development and Services

## In-Progress Certifications

### FedRAMP Authorization
- **Status: IN PROGRESS**
- Current Phase: 3PAO Assessment
- Sponsoring Agency: Department of Commerce
- **Expected Authorization: Q1 2025**
- Note: Initial documentation submitted. Assessment ongoing. Authorization not yet granted.

### StateRAMP
- **Status: PLANNED**
- Target Start: Q2 2025

## Compliance Frameworks
- NIST 800-53 Rev. 5 — Self-assessed, controls documented
- FISMA — Compliant through agency sponsorship
- Section 508 — Compliant, VPAT available
- HIPAA — Not currently applicable
""",

    "Staffing_Plan.md": """# TechForward Solutions — Staffing Plan for DFS Contract
## CONFIDENTIAL — Draft v2.1

### 1. Current Staffing Assessment
TechForward currently has 150 full-time employees. For the DFS contract, we plan to leverage existing staff and hire additional personnel to meet requirements.

### 2. Proposed Team Structure

#### Program Management
- Program Manager: Sarah Chen (existing employee, PMP certified)
- Deputy PM: To be hired
- Contract Administrator: James Wilson (existing)

#### Cloud Engineering Team
- Lead Cloud Architect: Michael Torres (AWS Solutions Architect Professional, existing)
- Cloud Engineers: 4 existing + **2 additional hires planned**
- Total: 7 cloud engineers (5 currently available, 2 to be hired)
- Target hire date for new engineers: **November 2024**

#### Security Team
- CISO: Dr. Priya Patel (CISSP, existing)
- Security Engineers: 2 existing (both CISSP) + **1 additional hire planned**
- Total: 3 security engineers when fully staffed
- Target hire date: **October 2024**

#### Support Team
- Support Manager: David Kim (existing)
- Current support staff: 16 personnel (business hours coverage)
- **Additional support engineers: 3 hires planned for 24/7 coverage**
- Target hire date: **November 15, 2024**
- Planned shift structure: 3 shifts x 8 hours to achieve 24/7 coverage
- NOTE: **24/7 support capability is contingent on completing these hires**

### 3. Security Clearance Status
- Currently cleared personnel: 78
- Clearance applications in progress: 5
- Additional clearances needed for DFS: Approximately 8-12
- **Timeline for clearance processing: 3-6 months**

### 4. Training Plan
- AWS re-certification: October 2024
- FedRAMP awareness training: September 2024
- DFS-specific onboarding: Post-contract award

### 5. Risk Factors
- Competitive hiring market for cleared engineers
- Clearance processing delays possible
- **24/7 support staffing is not yet in place and depends on successful hiring**
- Key personnel availability must be confirmed before contract start
""",

    "Security_Capabilities.md": """# TechForward Solutions — Security Capabilities Statement

## 1. Security Operations
TechForward maintains a dedicated Security Operations Center (SOC) that monitors our managed environments.

### SOC Operations
- **Operating hours: Monday-Friday, 7:00 AM - 7:00 PM Eastern**
- Automated monitoring and alerting: 24/7
- Manual incident response: Business hours with on-call rotation
- SIEM: Splunk Enterprise
- EDR: CrowdStrike Falcon

### Incident Response
- IR Plan: Updated annually, last update February 2024
- IR Team: 3 dedicated incident responders
- Mean Time to Detect: < 15 minutes (automated)
- Mean Time to Respond: < 30 minutes (business hours), < 2 hours (after hours)

## 2. Encryption Standards
- Data at rest: AES-256 encryption
- Data in transit: TLS 1.2 and TLS 1.3
- Key management: AWS KMS
- Certificate management: Automated via ACM

## 3. Access Control
- Multi-factor authentication required for all administrative access
- Role-based access control (RBAC) implemented
- Privileged access management: CyberArk
- Regular access reviews: Quarterly

## 4. Vulnerability Management
- Vulnerability scanning: Weekly automated scans (Tenable Nessus)
- Penetration testing: **Annual third-party testing** (last completed: June 2024)
- Patch management: Critical patches within 72 hours
- Remediation tracking: Jira-based workflow

## 5. Cloud Security
- AWS experience: 6 years
- Azure experience: 3 years
- **GCP experience: Limited (evaluation phase)**
- Cloud security posture management: Prisma Cloud
- Container security: Aqua Security

## 6. Compliance Monitoring
- Continuous compliance monitoring via Prisma Cloud
- NIST 800-53 control mapping documented
- Quarterly internal audits
- Annual third-party assessments

## 7. Known Gaps
- **SOC does not operate 24/7 — automated monitoring covers off-hours**
- Penetration testing is annual; quarterly testing would require additional vendor engagement
- GCP capabilities are limited and not production-ready
""",

    "Implementation_Plan.md": """# TechForward Solutions — Implementation Plan for DFS Contract
## Draft v1.3

### 1. Project Overview
This implementation plan outlines the phased approach for delivering IT infrastructure modernization services to the Department of Federal Services (DFS).

### 2. Implementation Timeline

#### Phase 1: Mobilization (Days 1-15)
- Contract kickoff meeting
- Staff onboarding and badging
- Environment access provisioning
- Initial security documentation
- Project management plan delivery

#### Phase 2: Assessment & Design (Days 16-30)
- Current state infrastructure assessment
- Target architecture design
- Security architecture review
- Migration planning
- Stakeholder workshops

#### Phase 3: Initial Deployment (Days 31-45)
- Core infrastructure provisioning
- Network configuration
- Security control implementation
- Initial workload migration (Tier 1 applications)
- **Monitoring and alerting setup**

#### Phase 4: Full Deployment (Days 46-60)
- Remaining workload migration
- Performance tuning
- Security validation
- User acceptance testing
- Operational readiness review

#### Phase 5: Steady State Operations (Day 61+)
- Transition to managed services
- SLA monitoring begins
- Monthly reporting cadence
- Continuous improvement process

### 3. Key Milestones

| Milestone | Target Day | Status |
|-----------|-----------|--------|
| Contract Award | Day 0 | Pending |
| Kickoff Meeting | Day 3 | Planned |
| Staff Onboarded | Day 15 | Planned |
| Assessment Complete | Day 30 | Planned |
| **Initial Deployment Complete** | **Day 45** | **Planned** |
| Full Operational Capability | Day 60 | Planned |
| First Monthly Report | Day 90 | Planned |

### 4. Risks and Mitigation
- **Risk: Initial deployment timeline (45 days) exceeds RFP requirement (30 days)**
  - Mitigation: Negotiate timeline or accelerate Phase 2 by running parallel workstreams
  - Impact: HIGH — could affect proposal scoring
- Risk: Security clearance delays for new staff
  - Mitigation: Use existing cleared personnel during transition
- Risk: Legacy system compatibility issues
  - Mitigation: Thorough assessment phase with fallback options

### 5. Resource Requirements
- 12 FTE during mobilization/deployment
- 8 FTE during steady state
- Cloud infrastructure costs: Estimated $85,000/month
- Tooling and licensing: $12,000/month

### 6. Dependencies
- Government-furnished facility access
- Network connectivity to DFS data centers
- Security clearance adjudications for new hires
- **Completion of 24/7 support staff hiring** (see Staffing Plan)
- **FedRAMP authorization completion** (see Certifications document)
""",
}


def get_demo_document_names() -> list[str]:
    """Return list of demo document filenames."""
    return list(DEMO_DOCUMENTS.keys())


def get_demo_document_content(filename: str) -> str:
    """Get content of a specific demo document."""
    return DEMO_DOCUMENTS.get(filename, "")


def get_all_demo_documents() -> dict[str, str]:
    """Get all demo documents."""
    return DEMO_DOCUMENTS.copy()
