"""
Synthetic Data Generator for Care Incident QA Project

Generates realistic but fully anonymised care plans, risk assessments, and incident records
for 100 service users in UK social care context.
"""

import csv
import random
from pathlib import Path
from datetime import datetime, timedelta


# Realistic UK social care data pools
FIRST_NAMES = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica",
    "Sarah", "Karen", "Margaret", "Dorothy", "Lisa", "Nancy", "Betty", "Helen",
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Donald", "Mark"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Clark"
]

LOCATIONS = [
    "Main Lounge", "Dining Room", "Bedroom", "Bathroom", "Corridor",
    "Garden", "Day Room", "Kitchen", "Conservatory", "Entrance Hall",
    "Wet Room", "Activity Room", "Quiet Lounge", "Outside Patio"
]

INCIDENT_CATEGORIES = [
    "Falls", "Medication", "Behaviour", "Skin Integrity", "Safeguarding",
    "Clinical", "Environment", "Nutrition", "Challenging Behaviour", "Absconding"
]

SEVERITIES = ["Low", "Medium", "High", "Critical"]

LIFE_HISTORY_SNIPPETS = [
    "Grew up along the Cornish coast and served as a Royal Navy cook; proud of culinary skills and maritime stories.",
    "Former textile designer from Manchester with lifelong love of patterned fabrics and meticulous sewing projects.",
    "Worked forty years as a Birmingham bus driver and values punctuality, uniforms, and orderly routines.",
    "Studied literature in London, later became a librarian who cherishes poetry recitals and quiet reading spaces.",
    "Ran a Yorkshire smallholding with spouse, happiest when discussing harvests, animals, and seasonal change.",
    "Migrated from Jamaica in the 1960s, active in church choir and values gospel music, vibrant colours, and faith discussions."
]

FAMILY_NETWORKS = [
    "Daughter (Sarah) is primary contact and attends monthly reviews; son (Liam) lives abroad and joins via video call.",
    "Sister (Joan) holds Lasting Power of Attorney for health decisions and expects weekly updates.",
    "Grandson (Elliot) visits after college on Wednesdays and advocates for technology use.",
    "Neighbour and long-term friend (Mrs Patel) acts as informal advocate alongside nephew (Marcus).",
    "Brother (David) coordinates with social worker; niece (Hannah) supplies faith resources and attends MDT meetings.",
    "Spouse deceased; lifelong friend (Agnes) plus church safeguarding lead act as support network."
]

COMMUNICATION_STYLES = [
    "Prefers calm, low tone with time to process information; avoid rapid questioning.",
    "Responds well to visual prompts, touch cues, and step-by-step explanations.",
    "Benefits from humour and reminiscence before discussing care tasks.",
    "Requires direct eye contact, clear lip movements due to mild hearing loss.",
    "Needs choices offered one at a time and confirmation of understanding.",
    "Uses short phrases; carers should validate feelings and repeat key points succinctly."
]

ROUTINE_COMPONENTS = {
    "Morning": [
        "Wake between 06:30-07:00; offer warm lemon water before personal care.",
        "Transfers using Sara Stedy with two staff; ensure orthostatic BP observed prior to standing.",
        "Accepts strip wash in bathroom if preferred staff present; otherwise, offer basin wash in-room.",
        "Breakfast best served in dining room window seat with porridge and stewed fruit.",
        "Medication window 07:30-08:00; crush tablets only if SALT guidance permits.",
        "Uses reminiscence playlist while carers complete dressing to reduce anxiety."
    ],
    "Daytime": [
        "Needs structured activity blocks (crafts, light physio, garden walk) to prevent disinhibition.",
        "Encourage hourly fluid round with thickened squash; record acceptance on fluid chart.",
        "Prefers chair exercises led by physio assistant; monitor for shortness of breath.",
        "Benefits from sensory box (fabric swatches, lavender oil) during quieter periods.",
        "May nap after lunch; ensure heels are offloaded and oxygen concentrator checked.",
        "Risk of distress if communal TV is loud; offer headphones or quiet lounge alternative."
    ],
    "Evening & Night": [
        "Sundowning begins circa 17:00; dim overhead lights and switch to warm lamps.",
        "Encourage family video call after tea to reduce exit-seeking thoughts.",
        "Night medication at 21:00 accompanied by malt drink; monitor for choking risk.",
        "Hourly safety checks overnight with gentle torch to avoid startling.",
        "If restless, offer folded laundry task or memory box to redirect energy.",
        "Sleep more settled with weighted blanket and familiar radio station at low volume."
    ]
}

ESCALATION_ROUTES = [
    "Escalate to Registered Nurse, complete SBARD handover, and contact GP out-of-hours if pain unmanaged within 2 hours.",
    "If behaviours escalate beyond verbal de-escalation, call senior on duty, consider PRN per protocol, and log on ABC chart.",
    "For oxygen saturation < 90% despite prescribed therapy, initiate NEWS scoring and call 111 for clinical advice.",
    "Safeguarding triggers (unexplained bruising, disclosures) must be reported to manager immediately and logged on safeguarding portal.",
    "If blood glucose <4 mmol/L or >18 mmol/L, follow diabetes emergency plan and inform GP/diabetes nurse.",
    "Unwitnessed falls with head impact require 24-hour neuro observations and GP review; call 999 if deterioration noted."
]

PROFESSIONAL_PARTNERS = [
    "Community Mental Health Team",
    "Falls and balance clinic",
    "Physiotherapist",
    "Speech and Language Therapist (SALT)",
    "Dietitian",
    "Tissue Viability Nurse",
    "Community Heart Failure Nurse",
    "Diabetes Specialist Nurse",
    "Respiratory Consultant",
    "Safeguarding Social Worker",
    "Occupational Therapist",
    "Admiral Nurse",
    "Palliative Care Team"
]

MONITORING_FOCUS = [
    "Fluid and nutritional intake (FORT 15 system)",
    "Daily weight and oedema check",
    "Blood glucose before breakfast and evening meal",
    "Hourly intentional rounding documentation",
    "Behaviour monitoring using ABC charts",
    "Pain assessment using PAINAD scale",
    "Oxygen saturation and respiratory rate logging",
    "Skin integrity audit every other day",
    "Medication concordance audit weekly",
    "Mental health wellness scoring (Dementia Care Mapping)"
]

CONDITION_PROFILES = [
    {
        "name": "Advanced mixed dementia with sundowning",
        "category": "cognitive",
        "summary": "Diagnosed 2017; fluctuating capacity, disorientation worsens late afternoon.",
        "presentation": "Requires 24-hour supervision, repetitive questioning, exit-seeking after 17:00.",
        "triggers": [
            "Sundowning after 17:00 leading to exit seeking",
            "Large groups or overlapping conversations",
            "Pain or discomfort not verbalised",
            "Unfamiliar carers approaching without introduction"
        ],
        "risks": [
            "High falls risk when mobilising impulsively",
            "Risk of missing medication due to confusion",
            "Potential for safeguarding disclosures needing validation"
        ],
        "interventions": {
            "proactive": [
                "Maintain orientation board with date, staff photos, and planned activities",
                "Offer memory box and narrated photo book before personal care",
                "Use lavender diffuser and soft lighting from 16:30"
            ],
            "reactive": [
                "Use validation therapy, acknowledge feelings, and redirect to safe space",
                "Reduce stimuli, offer weighted blanket, and provide one-to-one presence",
                "If disinhibited, offer folded laundry task to occupy hands"
            ],
            "clinical": [
                "GP reviews memantine and antidepressant regime quarterly",
                "Admiral nurse provides monthly coaching to staff",
                "Capacity assessments documented for high-risk decisions"
            ]
        },
        "monitoring": [
            "Hourly wellbeing checks between 17:00-22:00",
            "ABC chart for any escalation beyond 10 minutes",
            "Family update log maintained weekly"
        ],
        "professionals": ["Memory clinic consultant", "Admiral Nurse"]
    },
    {
        "name": "Parkinson's disease with dysphagia and orthostatic hypotension",
        "category": "neurological",
        "summary": "Diagnosed 2012; bradykinesia, tremor, and swallowing difficulties.",
        "presentation": "Transfers require two staff with Sara Stedy, experiences freezing episodes each morning.",
        "triggers": [
            "Delayed Parkinson's medication",
            "Fatigue following physiotherapy",
            "Rapid positional changes causing dizziness",
            "Thin fluids leading to coughing"
        ],
        "risks": [
            "Aspiration during meals",
            "Syncope due to blood pressure drops",
            "Muscle rigidity leading to pain"
        ],
        "interventions": {
            "proactive": [
                "Medication must be administered exactly on time using individual timers",
                "Provide soft diet with Stage 2 thickened fluids",
                "Allow extra time for verbal responses"
            ],
            "reactive": [
                "If freezing, encourage rhythmic counting and provide light touch guidance",
                "Sit or lie service user at first sign of dizziness, monitor BP",
                "If coughing persists, stop meal and alert nurse"
            ],
            "clinical": [
                "Neurology team reviews regimen every 6 months",
                "SALT monitors swallowing competence",
                "Physio leads quarterly moving and handling refreshers"
            ]
        },
        "monitoring": [
            "Record BP lying and standing twice weekly",
            "Meal charts noting cough/choke incidents",
            "Daily Parkinson's symptom log"
        ],
        "professionals": ["Neurology clinic", "SALT", "Physiotherapist"]
    },
    {
        "name": "Chronic heart failure with recurrent oedema",
        "category": "cardiovascular",
        "summary": "NYHA Class III; baseline shortness of breath on exertion.",
        "presentation": "Requires leg elevation in recliner, fluid restriction 1500ml/day.",
        "triggers": [
            "High-salt meals",
            "Missed diuretics",
            "Extended periods in wheelchair without elevation",
            "Emotional distress increasing heart rate"
        ],
        "risks": [
            "Flash pulmonary oedema",
            "Skin breakdown over ankles",
            "Dizziness when diuretics peak"
        ],
        "interventions": {
            "proactive": [
                "Daily weight monitoring before breakfast",
                "Encourage pacing techniques during transfers",
                "Strict fluid balance sheet"
            ],
            "reactive": [
                "If breathless at rest, sit upright, use fan therapy, start NEWS escalation",
                "Report weight gain >2kg in 3 days to heart failure nurse",
                "Apply emollient and support stockings as prescribed"
            ],
            "clinical": [
                "Community heart failure nurse reviews monthly",
                "GP adjusts diuretics based on weight trends",
                "Refer for urgent ECG if arrhythmia suspected"
            ]
        },
        "monitoring": [
            "Daily weights logged",
            "Fluid balance tallied each shift",
            "Ankle girth measured twice weekly"
        ],
        "professionals": ["Community Heart Failure Nurse", "GP"]
    },
    {
        "name": "Type 2 diabetes with peripheral neuropathy",
        "category": "metabolic",
        "summary": "Insulin dependent with fluctuating appetite; neuropathic pain in feet.",
        "presentation": "Requires foot inspections and carbohydrate counting support.",
        "triggers": [
            "Delayed meals",
            "High-sugar snacks left in communal areas",
            "Footwear rubbing or slipping",
            "Infections leading to hyperglycaemia"
        ],
        "risks": [
            "Hypoglycaemia during night",
            "Foot ulceration",
            "Mood changes linked to sugar fluctuations"
        ],
        "interventions": {
            "proactive": [
                "Offer low-GI snacks at 10:30 and 20:30",
                "Ensure podiatry-approved footwear only",
                "Teach staff to record carb portions"
            ],
            "reactive": [
                "For hypo signs, follow fast-acting glucose protocol",
                "Report redness on feet immediately and photograph",
                "If hyperglycaemic >18 mmol/L, alert nurse and repeat test"
            ],
            "clinical": [
                "Diabetes nurse reviews insulin regime quarterly",
                "Podiatry visit every 6 weeks",
                "Pain clinic oversees neuropathy medications"
            ]
        },
        "monitoring": [
            "Blood glucose before breakfast and evening",
            "Weekly foot integrity log",
            "Pain score recorded twice daily"
        ],
        "professionals": ["Diabetes Specialist Nurse", "Podiatry", "Pain Clinic"]
    },
    {
        "name": "Complex PTSD with recurrent depression",
        "category": "mental_health",
        "summary": "History of trauma; experiences intrusive memories, low mood, and withdrawal.",
        "presentation": "May decline care, experiences nightmares, hypervigilant to loud voices.",
        "triggers": [
            "Unexpected touch from behind",
            "Male voices shouting",
            "Smell of disinfectant similar to past events",
            "Nightmares leading to disorientation"
        ],
        "risks": [
            "Self-neglect (refusal to eat or wash)",
            "Heightened anxiety leading to aggression",
            "Suicidal ideation (historical)"
        ],
        "interventions": {
            "proactive": [
                "Offer choice of female carers for personal care",
                "Encourage grounding techniques (5-4-3-2-1)",
                "Provide safe space with comforting textiles"
            ],
            "reactive": [
                "Use trauma-informed language, acknowledge feelings, avoid restraint",
                "Offer PRN anxiolytic only after debrief",
                "If dissociating, provide warm drink and guide breathing"
            ],
            "clinical": [
                "CMHT reviews antidepressant therapy bi-monthly",
                "Psychologist offers remote sessions when tolerated",
                "Safeguarding plan in place for disclosures"
            ]
        },
        "monitoring": [
            "Daily mood tracker",
            "Weekly MDT reflection on triggers",
            "Safeguarding notes kept confidentially"
        ],
        "professionals": ["Community Mental Health Team", "Psychologist"]
    },
    {
        "name": "COPD with long-term oxygen therapy",
        "category": "respiratory",
        "summary": "Requires 2L oxygen via concentrator overnight and during exertion.",
        "presentation": "Baseline saturation 92%; productive cough in mornings.",
        "triggers": [
            "Chest infections",
            "Dusty environments",
            "Missing nebuliser treatment",
            "Anxiety causing rapid breathing"
        ],
        "risks": [
            "Acute exacerbation requiring hospital",
            "CO2 retention if oxygen exceeds prescription",
            "Weight loss due to breathlessness eating"
        ],
        "interventions": {
            "proactive": [
                "Encourage breathing exercises with physio",
                "Ensure nebuliser cleaned and ready twice daily",
                "Offer high-calorie small meals"
            ],
            "reactive": [
                "For sudden breathlessness, sit upright, pursed-lip breathing, start rescue pack if prescribed",
                "Escalate to 111/999 if saturation <88% after interventions",
                "Increase observation frequency during infection"
            ],
            "clinical": [
                "Respiratory nurse reviews every 3 months",
                "GP provides rescue steroid/antibiotic packs",
                "Dietitian monitors weight monthly"
            ]
        },
        "monitoring": [
            "SATS and respiratory rate twice daily",
            "Weight monthly",
            "Nebuliser maintenance log"
        ],
        "professionals": ["Respiratory Nurse", "Physiotherapist", "Dietitian"]
    },
    {
        "name": "Post-stroke hemiplegia with spasticity",
        "category": "neurological",
        "summary": "Left-sided weakness following 2021 CVA; expressive aphasia present.",
        "presentation": "Requires full hoist transfers, bespoke seating, and passive physiotherapy.",
        "triggers": [
            "Poor positioning leading to pain",
            "Fatigue after 30 minutes upright",
            "Constipation increasing tone",
            "Over-stimulation causing shutdown"
        ],
        "risks": [
            "Shoulder subluxation during transfers",
            "Pressure damage over sacrum",
            "Depression linked to communication barriers"
        ],
        "interventions": {
            "proactive": [
                "Use sling specified by physio only",
                "Implement 2-hourly repositioning schedule",
                "Provide communication board and allow time"
            ],
            "reactive": [
                "If tone increases, apply heat pack per protocol and consult physio",
                "For mood decline, use supported conversation techniques",
                "Report any new weakness immediately"
            ],
            "clinical": [
                "Physio reviews positioning plan monthly",
                "OT checks splints quarterly",
                "GP monitors antispasmodic medication"
            ]
        },
        "monitoring": [
            "Repositioning chart maintained",
            "Weekly skin inspections",
            "Mood log linked to therapy engagement"
        ],
        "professionals": ["Physiotherapist", "Occupational Therapist"]
    },
    {
        "name": "Alcohol-related brain damage with hepatic issues",
        "category": "cognitive",
        "summary": "Memory deficits, impulsivity, and compromised liver function.",
        "presentation": "Requires structured prompts, risk of confabulation, takes lactulose.",
        "triggers": [
            "Sensory overload in dining room",
            "Constipation increasing confusion",
            "Conversations about alcohol",
            "Missed lactulose doses"
        ],
        "risks": [
            "Exit seeking and community disorientation",
            "Hepatic encephalopathy",
            "Verbal aggression when challenged"
        ],
        "interventions": {
            "proactive": [
                "Provide structured day planner with traffic-light cues",
                "Encourage hydration and lactulose adherence",
                "Assign keyworker for reality orientation"
            ],
            "reactive": [
                "Use clear, factual statements and do not argue",
                "Offer quiet space and weighted blanket",
                "If hepatic signs emerge, escalate to GP"
            ],
            "clinical": [
                "Hepatology clinic reviews bloods quarterly",
                "Dietitian supports low-protein evening snack",
                "Psych liaison available if relapse risk rises"
            ]
        },
        "monitoring": [
            "Bowel chart for lactulose effectiveness",
            "Weekly LFT trend recording (if available)",
            "Exit-seeking log"
        ],
        "professionals": ["Hepatology clinic", "Dietitian", "Psych liaison"]
    },
    {
        "name": "Autism spectrum condition with learning disability",
        "category": "neurodivergent",
        "summary": "Requires structured routines, sensory regulation plan, and accessible information.",
        "presentation": "Communicates with short phrases, uses tablet for choice boards.",
        "triggers": [
            "Unexpected schedule changes",
            "Strong smells in dining room",
            "Staff speaking over each other",
            "Clothing labels causing itch"
        ],
        "risks": [
            "Meltdowns leading to self-injury",
            "Food refusal if textures disliked",
            "Isolation if peers misunderstand communication"
        ],
        "interventions": {
            "proactive": [
                "Provide visual timetable updated each shift",
                "Offer sensory diet (deep pressure, weighted lap pad)",
                "Use tablet-based social stories before appointments"
            ],
            "reactive": [
                "Implement low-arousal response, minimal speech",
                "Offer noise-cancelling headphones and dark room",
                "Allow recovery time without demands"
            ],
            "clinical": [
                "Learning disability nurse provides quarterly review",
                "Psychiatrist oversees medication annually",
                "Family advocate involved in best-interest meetings"
            ]
        },
        "monitoring": [
            "Sensory regulation log",
            "Food intake chart when new menu trialled",
            "Incident review template"
        ],
        "professionals": ["Learning Disability Nurse", "Psychiatrist"]
    }
]


def select_condition_profiles() -> list[dict]:
    """Ensure each care plan includes multiple complex conditions."""

    cognitive_pool = [c for c in CONDITION_PROFILES if c["category"] in {"cognitive", "mental_health"}]
    selection: list[dict] = [random.choice(cognitive_pool)]
    total_required = min(max(3, random.randint(3, 5)), len(CONDITION_PROFILES))
    remaining_pool = [c for c in CONDITION_PROFILES if c not in selection]
    needed = min(total_required - len(selection), len(remaining_pool))
    if needed > 0:
        selection.extend(random.sample(remaining_pool, k=needed))
    random.shuffle(selection)
    return selection


def build_daily_routine() -> dict[str, list[str]]:
    """Assemble varied daily routine notes for morning/day/evening."""

    routine: dict[str, list[str]] = {}
    for period, options in ROUTINE_COMPONENTS.items():
        pick = min(2, len(options))
        routine[period] = random.sample(options, k=pick)
    return routine


def aggregate_from_conditions(conditions: list[dict], key: str) -> list[str]:
    """Collect unique list items from all condition profiles."""

    collected: list[str] = []
    for condition in conditions:
        for item in condition.get(key, []):
            if item not in collected:
                collected.append(item)
    return collected


def aggregate_interventions(conditions: list[dict], intervention_key: str) -> list[str]:
    """Collect intervention statements of the requested type."""

    statements: list[str] = []
    for condition in conditions:
        for text in condition["interventions"].get(intervention_key, []):
            if text not in statements:
                statements.append(text)
    return statements


def build_risk_matrix_rows(conditions: list[dict]) -> list[tuple[str, str, str]]:
    """Create combined risk table entries covering triggers and responses."""

    rows: list[tuple[str, str, str]] = []
    for condition in conditions:
        risk_label = random.choice(condition["risks"])
        trigger = random.choice(condition["triggers"])
        response = random.choice(condition["interventions"].get("reactive", ["Provide reassurance and escalate to nurse."]))
        rows.append((f"{condition['name']} - {risk_label}", trigger, response))
    random.shuffle(rows)
    return rows[:5]


def choose_professionals(conditions: list[dict]) -> list[str]:
    """Blend professionals linked to conditions with general partners."""

    partners: list[str] = []
    for condition in conditions:
        for prof in condition.get("professionals", []):
            if prof not in partners:
                partners.append(prof)
    extra_pool = [p for p in PROFESSIONAL_PARTNERS if p not in partners]
    if extra_pool:
        extra_needed = max(0, 3 - len(partners))
        extra_needed = min(extra_needed, len(extra_pool))
        if extra_needed > 0:
            partners.extend(random.sample(extra_pool, k=extra_needed))
    return partners


def choose_monitoring_points(conditions: list[dict]) -> list[str]:
    """Combine monitoring prompts from profiles and general focus list."""

    monitoring_points = aggregate_from_conditions(conditions, "monitoring")
    extra_pool = [item for item in MONITORING_FOCUS if item not in monitoring_points]
    target = min(max(4, random.randint(4, 6)), len(monitoring_points) + len(extra_pool))
    while len(monitoring_points) < target and extra_pool:
        choice = random.choice(extra_pool)
        monitoring_points.append(choice)
        extra_pool.remove(choice)
    return monitoring_points[:target]


def generate_care_plan(service_user_id: str, name: str, age: int) -> str:
    """Create a multi-dimensional care plan with layered risks, triggers, and actions."""

    now = datetime.now()
    dob_year = now.year - age
    dob = datetime(dob_year, random.randint(1, 12), random.randint(1, 28))

    conditions = select_condition_profiles()
    daily_routine = build_daily_routine()
    triggers = aggregate_from_conditions(conditions, "triggers")
    risks = aggregate_from_conditions(conditions, "risks")
    proactive_support = aggregate_interventions(conditions, "proactive")
    reactive_support = aggregate_interventions(conditions, "reactive")
    clinical_actions = aggregate_interventions(conditions, "clinical")
    risk_rows = build_risk_matrix_rows(conditions)
    professionals = choose_professionals(conditions)
    monitoring_points = choose_monitoring_points(conditions)

    life_story = random.choice(LIFE_HISTORY_SNIPPETS)
    family_context = random.choice(FAMILY_NETWORKS)
    communication_style = random.choice(COMMUNICATION_STYLES)
    escalation_notes = random.sample(ESCALATION_ROUTES, k=2)

    def bulletise(items: list[str], limit: int | None = None) -> str:
        if not items:
            return "- No data"
        selection = items
        if limit is not None and len(items) > limit:
            selection = random.sample(items, k=limit)
        return "\n".join(f"- {text}" for text in selection)

    condition_rows = "\n".join(
        f"| {cond['name']} | {cond['presentation']} | {random.choice(cond['monitoring'])} / Linked team: {random.choice(cond.get('professionals', ['Core care team']))} |"
        for cond in conditions
    )

    risk_matrix = "\n".join(
        f"| {label} | {warning} | {response} |"
        for label, warning, response in risk_rows
    )

    daily_sections = []
    for period, activities in daily_routine.items():
        daily_sections.append(f"### {period}\n" + "\n".join(f"- {activity}" for activity in activities))
    daily_text = "\n\n".join(daily_sections)

    care_plan = f"""# Complex Care Plan: {name}

**Service User ID:** {service_user_id}  
**Date of Birth:** {dob.strftime('%Y-%m-%d')} (Age: {age})  
**Assessment Date:** {now.strftime('%Y-%m-%d')}  
**Planned Review Date:** {(now + timedelta(days=84)).strftime('%Y-%m-%d')}  
**Primary Diagnoses Referenced:** {', '.join(cond['name'] for cond in conditions[:4])}

---

## About the Person

- {life_story}
- {family_context}
- Communication preference: {communication_style}
- Cultural/spiritual needs: values respectful language, opportunity for reflection, and access to preferred music/faith resources.
- Advocacy/decision making: Best-interest decisions led with family/advocate present; capacity assessed per decision.

---

## Clinical Overview

| Condition | Presentation | Monitoring / Clinician Link |
|-----------|--------------|-----------------------------|
{condition_rows}

**Professional network actively involved:** {', '.join(professionals)}

---

## Presenting Needs, Triggers, and Risks

**Key triggers / early warning signs:**
{bulletise(triggers, limit=6)}

**Associated risks if unmet:**
{bulletise(risks, limit=5)}

**Observed strengths and protective factors:**
- Responds to storytelling about earlier career and music.
- Engages well with consistent staff pairing.
- Family provides collateral information when mental state fluctuates.

---

## Daily Rhythm and Support Offers

{daily_text}

---

## Proactive, Therapeutic, and Reactive Support

**Proactive approaches (embed every shift):**
{bulletise(proactive_support, limit=6)}

**Reactive / de-escalation responses:**
{bulletise(reactive_support, limit=5)}

**Clinical oversight / scheduled tasks:**
{bulletise(clinical_actions, limit=5)}

---

## Risk and Contingency Matrix

| Risk / Scenario | Warning Signs | Staff Response / Escalation |
|-----------------|---------------|-----------------------------|
{risk_matrix}

**Escalation reminders:**
{bulletise(escalation_notes)}

---

## Monitoring & Professional Oversight

**Required monitoring data sets:**
{bulletise(monitoring_points, limit=6)}

**Documentation expectations:**
- Care notes updated in real time with clear ABC entries for behavioural changes.
- Family communication log maintained weekly (or sooner following incidents).
- Capacity and best-interest records stored with safeguarding folder.

---

## Goals for the Next 12 Weeks

1. Maintain safety by reducing unplanned exits/falls to zero incidents through environmental cues and engagement.  
2. Achieve >85% adherence to personalised routine (measured via intentional rounding audits).  
3. Stabilise mood and sleep hygiene using co-produced bedtime plan and MDT oversight.  
4. Protect skin integrity and nutritional status through proactive monitoring and timely clinical escalation.  
5. Keep family/advocates involved with monthly MDT reviews and documented shared decisions.

---

**Compiled by:** Interdisciplinary Care Team  
**Signature:** _____________________  
**Date:** {now.strftime('%Y-%m-%d')}
"""
    return care_plan


def generate_falls_risk_assessment(service_user_id: str, name: str) -> str:
    """Generate a falls risk assessment."""
    
    risk_level = random.choice(["Low", "Medium", "High"])
    risk_score = {"Low": random.randint(0, 2), "Medium": random.randint(3, 5), "High": random.randint(6, 10)}[risk_level]
    
    assessment = f"""# Falls Risk Assessment

**Service User:** {name}  
**Service User ID:** {service_user_id}  
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Assessor:** Care Team Leader  

---

## Risk Score: {risk_score}/10 - **{risk_level} Risk**

---

## Assessment Criteria

| Factor | Yes/No | Notes |
|--------|--------|-------|
| History of falls | {random.choice(['Yes', 'No'])} | {random.choice(['2 falls in last 6 months', 'No falls recorded', '1 fall last month', 'Multiple falls documented'])} |
| Mobility issues | {random.choice(['Yes', 'No'])} | {random.choice(['Uses zimmer frame', 'Unsteady gait', 'Requires assistance', 'Independent mobility'])} |
| Cognitive impairment | {random.choice(['Yes', 'No'])} | {random.choice(['Dementia diagnosis', 'Confusion at times', 'Fully alert', 'Memory issues'])} |
| Medication affecting balance | {random.choice(['Yes', 'No'])} | {random.choice(['On diuretics', 'Sedating medications', 'No relevant medications', 'Antihypertensives'])} |
| Visual impairment | {random.choice(['Yes', 'No'])} | {random.choice(['Wears glasses', 'Cataracts', 'Good vision', 'Macular degeneration'])} |
| Continence issues | {random.choice(['Yes', 'No'])} | {random.choice(['Urgency leads to rushing', 'Fully continent', 'Uses pads', 'Catheterised'])} |
| Inappropriate footwear | {random.choice(['Yes', 'No'])} | {random.choice(['Sometimes wears slippers', 'Appropriate footwear', 'Requires supervision', 'New shoes provided'])} |
| Environmental hazards | {random.choice(['Yes', 'No'])} | {random.choice(['Clutter in room', 'Clear pathways', 'Poor lighting', 'All hazards removed'])} |

---

## Control Measures in Place

- {random.choice([
    'Bed rails in situ at night (with consent)',
    'Low-level bed to minimise injury risk',
    'Sensor mat in place to alert staff',
    'Regular observations during high-risk periods'
])}
- {random.choice([
    'Walking aid within easy reach',
    'Call bell accessible at all times',
    'Commode in room for night-time use',
    'Toilet located nearby'
])}
- {random.choice([
    'Anti-slip footwear to be worn',
    'Hip protectors recommended',
    'Appropriate footwear provided',
    'Physiotherapy referral made'
])}
- {random.choice([
    'Environment kept clear of obstacles',
    'Adequate lighting maintained',
    'Glasses cleaned daily and within reach',
    'Regular eyesight checks'
])}
- {random.choice([
    'Medication review completed',
    'Staff supervision during mobilisation',
    'Exercise programme to improve strength',
    'Family informed of falls risk'
])}

---

## Staff Actions

1. **Immediate:** {random.choice([
    'Ensure call bell always within reach',
    'Review environment for hazards daily',
    'Supervise all transfers',
    'Encourage use of walking aid'
])}

2. **Ongoing:** {random.choice([
    'Monitor and record all mobility activities',
    'Continue falls prevention programme',
    'Monthly medication review with GP',
    'Reassess following any incident'
])}

3. **Escalation:** Report any falls immediately to senior staff and complete incident form

---

## Review Date

This assessment will be reviewed on: **{(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}**  
Or sooner if circumstances change.

---

**Assessor Signature:** _____________________  
**Date:** {datetime.now().strftime('%Y-%m-%d')}
"""
    return assessment


def generate_behaviour_risk_assessment(service_user_id: str, name: str) -> str:
    """Generate a behaviour support risk assessment."""
    
    behaviours = [
        "verbal aggression when approached for personal care",
        "physical resistance during care activities",
        "wandering and attempting to leave the building",
        "agitation during evening hours (sundowning)",
        "calling out repeatedly",
        "intrusive behaviour towards other residents"
    ]
    
    triggers = [
        "unfamiliar staff members",
        "disruption to routine",
        "feeling unwell or in pain",
        "over-stimulation or noisy environment",
        "misunderstanding of situation",
        "feeling rushed or pressured"
    ]
    
    assessment = f"""# Behaviour Support Risk Assessment

**Service User:** {name}  
**Service User ID:** {service_user_id}  
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Assessor:** Senior Care Staff  

---

## Identified Behaviours

**Primary Behaviour of Concern:**  
{random.choice(behaviours).capitalize()}

**Frequency:** {random.choice(['Daily', 'Several times per week', 'Occasional', '2-3 times weekly'])}

**Triggers Identified:**
- {random.choice(triggers).capitalize()}
- {random.choice(triggers).capitalize()}
- {random.choice(triggers).capitalize()}

---

## Risk Level: {random.choice(['Medium', 'High', 'Low'])}

**Risk to Service User:** {random.choice([
    'May refuse essential care leading to deterioration',
    'Risk of injury if attempts to leave unescorted',
    'May become distressed and anxious',
    'Potential for self-harm if agitated'
])}

**Risk to Others:** {random.choice([
    'Minimal - behaviour not directed at others',
    'May distress other residents',
    'Potential for physical contact with staff',
    'Low risk with appropriate de-escalation'
])}

---

## Underlying Causes/Contributing Factors

- **Medical:** {random.choice([
    'Dementia diagnosis - capacity fluctuates',
    'Urinary tract infections increase confusion',
    'Pain from arthritis affects mood',
    'Delirium episodes documented'
])}

- **Psychological:** {random.choice([
    'Anxiety when separated from familiar staff',
    'Frustration due to communication difficulties',
    'Feels loss of independence and control',
    'Depression - under review by mental health team'
])}

- **Environmental:** {random.choice([
    'Overstimulation in busy communal areas',
    'Dislikes loud noises or sudden movements',
    'Prefers quieter environment',
    'Benefits from structured routine'
])}

---

## Support Strategies

### Prevention (Proactive Approaches)

1. **Environmental:**
   - {random.choice([
       'Provide quiet space for one-to-one time',
       'Reduce environmental stimulation',
       'Maintain consistent room layout',
       'Ensure good lighting to reduce confusion'
   ])}

2. **Communication:**
   - {random.choice([
       'Use calm, reassuring tone of voice',
       'Approach from the front, make eye contact',
       'Use simple, clear sentences',
       'Allow time to process information'
   ])}

3. **Routine:**
   - {random.choice([
       'Maintain consistent daily routine',
       'Same staff members where possible',
       'Personal care at preferred times',
       'Build in rest periods to prevent over-tiredness'
   ])}

4. **Activities:**
   - {random.choice([
       'Engage in meaningful activities based on life story',
       'Music therapy has proven beneficial',
       'Gentle exercise to reduce restlessness',
       'Sensory activities to promote calm'
   ])}

### Intervention (Reactive Approaches)

**If behaviour escalates:**

1. **Immediate Actions:**
   - {random.choice([
       'Give space - do not crowd or restrain',
       'Remove other residents if necessary',
       'Speak calmly and offer reassurance',
       'Redirect attention to preferred activity'
   ])}
   
2. **De-escalation Techniques:**
   - {random.choice([
       'Validate feelings: "I can see you\'re upset"',
       'Offer alternatives: "Would you like to sit in the garden?"',
       'Use distraction with familiar objects or topics',
       'Step away briefly and return with different staff member'
   ])}

3. **Post-Incident:**
   - Complete ABC chart (Antecedent, Behaviour, Consequence)
   - Debrief with staff involved
   - Review and update strategies if needed
   - Inform family if appropriate

---

## Medication

**PRN Medication Available:** {random.choice(['Yes - Lorazepam 0.5mg as prescribed', 'No', 'Under review with psychiatrist', 'Yes - to be used as last resort only'])}

**Last Review:** {random.choice(['Last month by GP', '2 weeks ago - mental health team', 'Ongoing monitoring', 'Due for review next week'])}

---

## Multi-Disciplinary Involvement

- GP: {random.choice(['Regular contact', 'Monthly review', 'As required'])}
- Mental Health Team: {random.choice(['Active involvement', 'Discharged - stable', 'Referral pending', 'Regular consultations'])}
- Family: {random.choice(['Fully informed and supportive', 'Limited contact', 'Involved in care planning', 'Weekly updates provided'])}

---

## Review and Monitoring

**Monitoring Method:** ABC charts completed for each incident

**Review Frequency:** {random.choice(['Weekly MDT discussion', 'Fortnightly review', 'Monthly assessment', 'Following each incident'])}

**Next Review Date:** {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}

---

## Staff Training Requirements

All staff supporting {name.split()[0]} should have completed:
- Dementia awareness training
- De-escalation techniques
- Understanding behaviour as communication
- Safeguarding adults

---

**Completed by:** _____________________ **Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Reviewed by Manager:** _____________________ **Date:** {datetime.now().strftime('%Y-%m-%d')}
"""
    return assessment


def generate_medication_risk_assessment(service_user_id: str, name: str) -> str:
    """Generate a medication risk assessment (optional)."""
    
    assessment = f"""# Medication Risk Assessment

**Service User:** {name}  
**Service User ID:** {service_user_id}  
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}  

---

## Medication Administration

**Level of Support Required:** {random.choice([
    'Full administration by trained staff',
    'Supervision and prompting',
    'Independent with occasional monitoring',
    'Full support - unable to self-administer'
])}

**Capacity to Consent:** {random.choice([
    'Has capacity - consents to medication',
    'Lacks capacity - best interest decision made',
    'Fluctuating capacity - assess daily',
    'Mental Capacity Assessment completed'
])}

---

## Risk Factors

| Risk Factor | Present | Notes |
|-------------|---------|-------|
| Swallowing difficulties | {random.choice(['Yes', 'No'])} | {random.choice(['SALT review completed', 'No issues identified', 'Some medications crushed', 'Liquid formulations used'])} |
| Refusal of medication | {random.choice(['Yes', 'No'])} | {random.choice(['Occasional refusal documented', 'Accepts medication well', 'Requires covert administration (authorised)', 'Persuasion sometimes needed'])} |
| Multiple medications (polypharmacy) | {random.choice(['Yes', 'No'])} | {random.choice(['10+ medications daily', '5-8 regular medications', 'Minimal medications', 'Under regular GP review'])} |
| Side effects experienced | {random.choice(['Yes', 'No'])} | {random.choice(['Drowsiness noted', 'No adverse effects', 'Dizziness after morning dose', 'Under monitoring'])} |
| Allergies | {random.choice(['Yes', 'No'])} | {random.choice(['Penicillin allergy - documented', 'No known allergies', 'Adhesive plaster sensitivity', 'NKDA'])} |

---

## Control Measures

- Medication Administration Record (MAR) chart completed accurately after each administration
- Two-person checking system for controlled drugs
- {random.choice([
    'Medication administered with food to reduce gastric irritation',
    'Specific timing requirements followed',
    'Regular monitoring for side effects',
    'Blood tests as per protocol'
])}
- {random.choice([
    'Monthly medication audit by senior staff',
    'Regular medication reviews with GP',
    'Family informed of medication changes',
    'All staff trained in medication administration'
])}

---

## PRN (As Required) Medications

**PRN protocols in place for:**
- {random.choice(['Pain relief (Paracetamol)', 'Anxiety (Lorazepam)', 'Constipation (Laxatives)', 'Indigestion (Antacids)'])}
- {random.choice(['Agitation (as per behaviour plan)', 'Nausea (Cyclizine)', 'None currently', 'Under review'])}

**Staff trained to assess need and document:** Yes

---

## Review Date

Next medication review: **{(datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')}**  
Or sooner if changes in condition.

---

**Assessor:** _____________________ **Date:** {datetime.now().strftime('%Y-%m-%d')}
"""
    return assessment


def generate_incident_description(category: str, location: str) -> tuple[str, str]:
    """Generate brief description and detailed body text for an incident."""
    
    incident_templates = {
        "Falls": [
            (
                "Service user found on floor in {location}",
                "Staff member entered {location} at {time} and found service user sitting on the floor. "
                "Service user stated they had been reaching for their walking frame and lost balance. "
                "No visible injuries noted. Vital signs checked and within normal limits. "
                "Neurological observations commenced as per falls protocol. Service user assisted to chair with hoist. "
                "Comfortable and alert. Family notified. Incident form completed. GP informed - no further action required at this time."
            ),
            (
                "Unwitnessed fall in {location}",
                "Service user discovered on floor in {location} by care staff during routine checks. "
                "Fall was unwitnessed. Service user unable to recall what happened but complained of pain to right hip. "
                "Left in position, emergency services called. Paramedics attended and conveyed to A&E for assessment. "
                "X-ray confirmed no fracture. Returned to service later same day. Post-falls protocol initiated. "
                "Family updated throughout. Falls risk assessment reviewed."
            ),
            (
                "Assisted fall during transfer",
                "During assisted transfer from wheelchair to armchair in {location}, service user's legs gave way. "
                "Staff member supported controlled descent to floor, preventing injury. Service user assessed on floor - "
                "no pain or obvious injury. Assistance requested, two staff used hoist to transfer to bed for full assessment. "
                "Appeared shaken but no injuries sustained. Observations normal. Encouraged to rest. "
                "Physiotherapy referral made for mobility review."
            ),
        ],
        "Medication": [
            (
                "Medication administration error identified",
                "During medication round in {location}, staff member realised they had administered morning medications to incorrect service user. "
                "Error identified immediately. Both service users' medications checked - no harmful medications swapped. "
                "Senior staff informed immediately, both service users monitored closely for next 4 hours. "
                "No adverse effects noted. GP contacted and advised continued monitoring. Families informed and apologised to. "
                "Staff member retrained on checking procedures. Incident reviewed at clinical governance meeting."
            ),
            (
                "Medication refused by service user",
                "Service user refused all morning medications in {location} stating 'I don't need them'. "
                "Staff attempted gentle persuasion explaining importance of medication but service user became agitated. "
                "Decision made not to force medication to maintain relationship. Senior staff informed. "
                "Further attempt made 1 hour later by different staff member - medications accepted without issue. "
                "Mental capacity regarding medication decisions to be reviewed. GP aware."
            ),
            (
                "Medication found on floor",
                "Tablet (later identified as Amlodipine 5mg) found on floor in {location} during cleaning. "
                "Unable to determine which service user this belonged to. All service users in area checked - "
                "all MAR charts showed medications signed as given. Tablet disposed of as per policy. "
                "All staff reminded to observe service users swallowing medications. "
                "Medication administration procedures reviewed with team."
            ),
        ],
        "Behaviour": [
            (
                "Verbal aggression towards staff during personal care",
                "During morning personal care in {location}, service user became verbally aggressive, shouting and swearing at care staff. "
                "Staff member stepped back, gave space, and spoke calmly. Service user continued to refuse care. "
                "Staff left room for 10 minutes then returned with different colleague. Service user had calmed and accepted care from new staff member. "
                "Possible triggers: overtired, preferred male carer not available. ABC chart completed. "
                "Behaviour support plan reviewed - no changes needed. Service user later apologised to staff."
            ),
            (
                "Physical aggression - grabbed staff member's arm",
                "While providing assistance in {location}, service user suddenly grabbed staff member's left forearm tightly. "
                "Staff member remained calm, asked service user to let go, which they did after approximately 5 seconds. "
                "Small red mark visible on staff arm but no broken skin. Cold compress applied, mark faded within 30 minutes. "
                "Service user appeared confused and did not recognise what had happened. Possible pain trigger - "
                "appeared to grimace when moved. PRN analgesia offered and accepted. Behaviour settled. "
                "No injury to staff member. Staff member completed incident form and body map."
            ),
            (
                "Exit-seeking behaviour - attempted to leave building",
                "Service user found at front entrance in {location} attempting to open the door stating they needed to 'get home to cook dinner'. "
                "Gently redirected by staff using distraction technique. Offered cup of tea and biscuit which was accepted. "
                "Walked with staff to lounge where familiar music was playing. Became settled and engaged in conversation about past. "
                "Appeared to forget about leaving. Family member telephoned to provide reassurance which helped. "
                "No distress caused. Security settings on door checked and functioning correctly."
            ),
        ],
        "Skin Integrity": [
            (
                "Skin tear to forearm identified",
                "During personal care in {location}, care staff noticed 3cm skin tear to right forearm. "
                "Service user stated they must have caught it on wheelchair but couldn't remember when. "
                "Wound cleaned with saline, sterile dressing applied as per tissue viability protocol. "
                "Wound photographed and body map completed. Not infected, edges well approximated. "
                "District nurse informed - will review at next visit. Skin tear risk assessment updated. "
                "Long sleeves recommended to protect fragile skin."
            ),
            (
                "Pressure area redness noted",
                "Redness noted to sacral area during personal care in {location}. "
                "Area measures approximately 2cm x 2cm, non-blanching. Service user denies pain or discomfort. "
                "Repositioning schedule reviewed and increased to 2-hourly. Barrier cream applied. "
                "Pressure-relieving cushion in use. Nutrition reviewed - adequate intake. "
                "District nurse to assess within 24 hours. Photography and body mapping completed. "
                "Waterlow score recalculated - remains high risk. Tissue viability nurse referral made."
            ),
        ],
        "Safeguarding": [
            (
                "Unexplained bruising identified",
                "During personal care in {location}, staff member noticed several bruises to upper arms (approximately 2-3cm each, yellow/green in colour). "
                "Service user unable to explain how bruises occurred. Body map completed and photographed. "
                "Senior staff informed immediately. Safeguarding alert raised as per policy. "
                "Recent visitors and activities reviewed. No concerns identified but monitoring continues. "
                "Family contacted - unaware of any incidents. Safeguarding team to investigate. "
                "Service user observed for any further marks or changes in behaviour."
            ),
            (
                "Allegation made by service user",
                "Service user reported to staff in {location} that another service user 'took money from their room'. "
                "Senior staff informed immediately. Both service users spoken to separately. "
                "Room checked with service user - all belongings accounted for, no money missing. "
                "Service user appeared confused about allegation and later could not recall making it. "
                "Possible confabulation due to dementia. Documented as potential safeguarding concern. "
                "Manager informed, monitoring in place. Family updated. Valuables list checked - all items present."
            ),
        ],
        "Clinical": [
            (
                "Choking incident during meal",
                "Service user began choking while eating lunch in {location}. "
                "Staff member immediately intervened, encouraged coughing. Obstruction cleared after 3-4 strong coughs. "
                "Service user recovered quickly, breathing normally. Remained seated and observed for 15 minutes. "
                "No respiratory distress noted. Meal discontinued as precaution. SALT referral made urgently. "
                "Swallowing assessment to be completed before resuming normal diet. "
                "Soft diet and supervision implemented meanwhile. GP informed. Family contacted."
            ),
            (
                "Seizure activity observed",
                "Service user experienced tonic-clonic seizure in {location} lasting approximately 2 minutes. "
                "Staff protected head with cushion, cleared area, timed seizure, placed in recovery position once jerking stopped. "
                "Post-ictal period - confused and drowsy for approximately 20 minutes. Vital signs monitored and stable. "
                "Known epilepsy, last seizure 6 months ago. No injuries sustained during seizure. "
                "Recovery uneventful. GP contacted - medication review arranged. Detailed seizure record completed. "
                "Neurological observations continued for 4 hours post-seizure."
            ),
        ],
        "Environment": [
            (
                "Water leak in ceiling",
                "Water leak discovered in ceiling of {location} during routine checks. "
                "Area immediately cordoned off, service users moved to alternative location. "
                "Maintenance contacted - attended within 30 minutes. Leak from bathroom above identified and isolated. "
                "Ceiling assessed - no immediate collapse risk but requires repair. "
                "Room out of use until repairs completed. Manager informed, contractors arranged for tomorrow. "
                "No service users or staff affected. All equipment removed from room."
            ),
            (
                "Broken window identified",
                "Broken window pane discovered in {location} during morning checks. "
                "Small crack in outer pane, no glass fragments in room. Cause unknown - possibly weather related. "
                "Area made safe, room secured and not in use pending repair. Maintenance informed. "
                "Emergency glazier contacted - repair scheduled for today. No injuries, no service users in room at time of discovery. "
                "All windows to be inspected as precaution. Manager notified."
            ),
        ],
        "Nutrition": [
            (
                "Significant weight loss identified",
                "Routine monthly weighing in {location} showed service user has lost 4kg in past month (current weight 52kg). "
                "Senior staff informed. Food charts reviewed - intake appears adequate but fluctuating. "
                "GP referral made urgently. Dietitian input requested. Possible causes being investigated - "
                "dental problems, infection, medication side effects, low mood. "
                "Daily food and fluid monitoring implemented. Fortified diet commenced. "
                "Family informed and concerned - will visit to encourage eating. MUST score calculated - medium risk."
            ),
        ],
        "Challenging Behaviour": [
            (
                "Service user resistive to care",
                "Service user became resistive during personal care in {location}, pushing staff away and shouting. "
                "Care abandoned immediately. Service user left to calm with regular checks from doorway. "
                "After 20 minutes, approached by familiar staff member with cup of tea. Service user accepted drink and appeared calmer. "
                "Personal care reattempted with different approach - service user cooperative. Trigger appeared to be rushing and feeling pressured. "
                "ABC chart completed. Reminder to all staff to allow extra time and not to rush. "
                "Service user's preferred routine discussed at handover."
            ),
        ],
        "Absconding": [
            (
                "Service user left building unsupervised",
                "Service user noted missing from {location} during routine check. Search of building commenced immediately. "
                "Not found on premises. CCTV checked - showed service user leaving via main entrance 15 minutes earlier. "
                "Police contacted immediately and description provided. Family informed. "
                "Staff member searched local area in vehicle. Police located service user 2 streets away, unharmed but confused. "
                "Returned to service safely. Full assessment completed - no injuries, appeared well. "
                "Mental capacity assessment to be completed. Door security system reviewed. "
                "Safeguarding alert raised. Best interest meeting arranged."
            ),
        ],
    }
    
    templates = incident_templates.get(category, [("Generic incident occurred", "Details of incident in {location} at {time}.")])
    brief, body = random.choice(templates)
    
    return brief.format(location=location), body.format(location=location, time="{time}")


def generate_incidents_for_service_user(service_user_id: str) -> list[dict]:
    """Generate 10-25 incidents for a service user."""
    
    num_incidents = random.randint(10, 25)
    incidents = []
    
    start_date = datetime.now() - timedelta(days=365)  # Past year
    
    for i in range(num_incidents):
        incident_date = start_date + timedelta(days=random.randint(0, 365))
        incident_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
        
        category = random.choice(INCIDENT_CATEGORIES)
        location = random.choice(LOCATIONS)
        severity = random.choice(SEVERITIES)
        
        brief, body = generate_incident_description(category, location)
        body = body.replace("{time}", incident_time)
        
        incident = {
            "incident_id": f"INC{service_user_id[2:]}{i+1:03d}",  # e.g., INC001001
            "service_user_id": service_user_id,
            "date": incident_date.strftime("%Y-%m-%d"),
            "time": incident_time,
            "location": location,
            "brief_description": brief,
            "body_text": body,
            "severity": severity,
            "category": category
        }
        
        incidents.append(incident)
    
    # Sort by date
    incidents.sort(key=lambda x: (x["date"], x["time"]))
    
    return incidents


def generate_synthetic_data():
    """Main function to generate all synthetic data."""
    
    # Setup directory structure
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    care_plans_dir = data_dir / "care_plans"
    risk_assessments_dir = data_dir / "risk_assessments"
    
    # Create directories
    care_plans_dir.mkdir(parents=True, exist_ok=True)
    risk_assessments_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating synthetic data for 100 service users...")
    print(f"Data directory: {data_dir}")
    
    all_incidents = []
    
    for i in range(1, 101):
        service_user_id = f"SU{i:03d}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        age = random.randint(65, 98)
        
        if i % 10 == 0:
            print(f"Processing service user {i}/100...")
        
        # Generate and save care plan
        care_plan = generate_care_plan(service_user_id, name, age)
        care_plan_file = care_plans_dir / f"{service_user_id}_care_plan.md"
        care_plan_file.write_text(care_plan, encoding='utf-8')
        
        # Generate and save falls risk assessment
        falls_assessment = generate_falls_risk_assessment(service_user_id, name)
        falls_file = risk_assessments_dir / f"{service_user_id}_falls_risk.md"
        falls_file.write_text(falls_assessment, encoding='utf-8')
        
        # Generate and save behaviour risk assessment
        behaviour_assessment = generate_behaviour_risk_assessment(service_user_id, name)
        behaviour_file = risk_assessments_dir / f"{service_user_id}_behaviour_risk.md"
        behaviour_file.write_text(behaviour_assessment, encoding='utf-8')
        
        # Sometimes generate medication risk assessment
        if random.random() > 0.3:  # 70% chance
            med_assessment = generate_medication_risk_assessment(service_user_id, name)
            med_file = risk_assessments_dir / f"{service_user_id}_medication_risk.md"
            med_file.write_text(med_assessment, encoding='utf-8')
        
        # Generate incidents
        incidents = generate_incidents_for_service_user(service_user_id)
        all_incidents.extend(incidents)
    
    # Write all incidents to CSV
    incidents_file = data_dir / "incidents.csv"
    
    with open(incidents_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "incident_id", "service_user_id", "date", "time", 
            "location", "brief_description", "body_text", "severity", "category"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_incidents)
    
    print(f"\n✓ Synthetic data generation complete!")
    print(f"✓ Generated 100 service users (SU001-SU100)")
    print(f"✓ Created {len(list(care_plans_dir.glob('*.md')))} care plans in {care_plans_dir}")
    print(f"✓ Created {len(list(risk_assessments_dir.glob('*.md')))} risk assessments in {risk_assessments_dir}")
    print(f"✓ Generated {len(all_incidents)} incidents in {incidents_file}")
    print(f"\nAll data uses fully anonymised, synthetic content in realistic UK social care language.")


if __name__ == "__main__":
    generate_synthetic_data()
