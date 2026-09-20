"""
Deterministic Academic & Professional Proposal Engine.
Generates comprehensive, publication-ready proposals tailored to academic levels
(Bachelor's, Master's, PhD) and niches (Education, Business, Social Media).
Runs 100% offline or as a rock-solid fallback when LLM APIs are unreachable.
"""

from typing import List, Tuple
from proposal_agent.models import (
    AcademicLevel, AcademicProposalType, AcademicProposalInput, AcademicProposalResponse
)
from proposal_agent.rules_linter import count_words

def generate_academic_offline(inp: AcademicProposalInput) -> AcademicProposalResponse:
    """Generate a structured 7-section proposal calibrated for the chosen academic level and niche."""
    level = inp.academic_level
    ptype = inp.proposal_type
    topic = inp.topic.strip()
    purpose = inp.purpose.strip()
    audience = inp.target_audience.strip() if inp.target_audience else "Evaluation Committee and Stakeholders"
    reqs = inp.specific_requirements.strip() if inp.specific_requirements else "Standard academic and institutional review guidelines."

    # 1. Section: Title
    if level == AcademicLevel.BACHELORS:
        if ptype == AcademicProposalType.EDUCATION:
            title = f"An Applied Study on {topic}: Enhancing Learning Outcomes and Student Engagement"
        elif ptype == AcademicProposalType.BUSINESS:
            title = f"Business Strategy and Feasibility Plan: {topic}"
        else:
            title = f"Strategic Social Media Campaign and Growth Plan for {topic}"
    elif level == AcademicLevel.MASTERS:
        if ptype == AcademicProposalType.EDUCATION:
            title = f"Pedagogical Innovation and Implementation Framework: An Empirical Investigation into {topic}"
        elif ptype == AcademicProposalType.BUSINESS:
            title = f"Strategic Market Optimization and Operational Framework: Driving Enterprise Value in {topic}"
        else:
            title = f"Algorithmic Distribution and Multi-Channel Engagement Dynamics: A Strategic Analysis of {topic}"
    else:  # PhD
        if ptype == AcademicProposalType.EDUCATION:
            title = f"Epistemic Paradigms and Pedagogical Transformation: A Critical Inquiry into {topic}"
        elif ptype == AcademicProposalType.BUSINESS:
            title = f"Theoretical Grounding and Econometric Modeling of {topic}: Resolving Contemporary Market Inefficiencies"
        else:
            title = f"Algorithmic Mediations and Information Diffusion: A Mixed-Methods Investigation into {topic}"

    # 2. Section: Introduction / Background
    if level == AcademicLevel.BACHELORS:
        intro = (
            f"The field of {ptype.value.lower().replace(' proposal', '')} is experiencing significant evolution, "
            f"making the study of {topic} both timely and essential. In modern environments, practitioners and learners "
            f"face emerging opportunities that require clear, structured, and practical approaches. "
            f"This proposal addresses {purpose} by establishing a foundational framework tailored for {audience}. "
            f"By synthesizing core concepts and direct observations, this project connects textbook theory with "
            f"real-world application, ensuring tangible progress and measurable classroom or organizational outcomes."
        )
    elif level == AcademicLevel.MASTERS:
        intro = (
            f"Contemporary discourse within {ptype.value.lower().replace(' proposal', '')} highlights a growing "
            f"imperative for empirical rigor and systemic integration regarding {topic}. While conventional models "
            f"offer partial explanations, rapid socio-technical shifts have created structural complexities that "
            f"existing operational paradigms fail to comprehensively address. This proposal presents an analytical framework "
            f"designed to fulfill {purpose}, targeted directly at {audience}. By bridging rigorous theoretical literature "
            f"with practical implementation protocols, this study investigates underlying causal dynamics and establishes "
            f"a repeatable, scalable benchmark for operational and academic advancement."
        )
    else:  # PhD
        intro = (
            f"Contemporary scholarship in {ptype.value.lower().replace(' proposal', '')} stands at an epistemological "
            f"crossroads concerning the theorization and systemic actualization of {topic}. Extant literature frequently "
            f"suffers from methodological fragmentation and unexamined ontological assumptions, leaving foundational "
            f"mechanisms under-theorized. This doctoral research proposal engages directly with this gap, proposing a "
            f"groundbreaking conceptual and empirical paradigm aimed at {purpose}. Formulated for evaluation by {audience}, "
            f"this inquiry problematizes prevailing orthodoxies, constructs an interdisciplinary investigative matrix, "
            f"and provides substantial theoretical and empirical contributions to the overarching discipline."
        )

    # 3. Section: Problem Statement
    if level == AcademicLevel.BACHELORS:
        prob = (
            f"A major challenge currently observed in relation to {topic} is the lack of accessible, streamlined solutions "
            f"that address day-to-day challenges. Many existing approaches are either too complex for everyday users or fail "
            f"to deliver consistent results. Specifically, stakeholders struggle with achieving {purpose} due to fragmented "
            f"tools and inadequate guidance. Without a well-organized plan, resources are wasted and key goals remain unmet."
        )
    elif level == AcademicLevel.MASTERS:
        prob = (
            f"Despite recent advancements, organizations and researchers addressing {topic} encounter critical structural "
            f"inefficiencies and strategic misalignment. Empirical evidence suggests that conventional interventions fail "
            f"to resolve {purpose} due to suboptimal integration, data silos, and insufficient analytical validation. "
            f"This gap creates measurable friction for {audience}, inhibiting performance and preventing scalable adoption."
        )
    else:  # PhD
        prob = (
            f"A critical lacuna persists within the literature regarding {topic}. Existing empirical and theoretical "
            f"models fail to account for non-linear interactions and structural mediating variables governing {purpose}. "
            f"Consequently, scholarly inquiry has reached an explanatory plateau, while institutional bodies such as "
            f"{audience} lack validated predictive models. This study directly confronts this theoretical void, establishing "
            f"the causal pathways and boundary conditions that have remained unaddressed in peer-reviewed scholarship."
        )

    # 4. Section: Objectives
    if level == AcademicLevel.BACHELORS:
        objs = [
            f"Identify and document the core requirements and foundational challenges associated with {topic}.",
            f"Design and execute a practical workflow to systematically realize {purpose}.",
            f"Evaluate performance benchmarks and gather actionable feedback from {audience}.",
            f"Produce a documented toolkit and practical recommendations adhering to: {reqs}."
        ]
    elif level == AcademicLevel.MASTERS:
        objs = [
            f"Conduct a comprehensive diagnostic and comparative analysis of existing frameworks governing {topic}.",
            f"Formulate an empirical operational model to advance {purpose} across multi-stakeholder settings.",
            f"Validate systemic efficacy through structured pilot testing, data analytics, and stakeholder feedback from {audience}.",
            f"Synthesize operational guidelines, quantitative metrics, and compliance controls aligned with: {reqs}."
        ]
    else:  # PhD
        objs = [
            f"Deconstruct extant ontological and epistemological assumptions regarding {topic} through a systematic literature meta-synthesis.",
            f"Formulate a novel theoretical construct and mathematical/conceptual taxonomy addressing {purpose}.",
            f"Deploy an empirical, triangulated multi-phase research methodology to test hypothesized causal relationships.",
            f"Synthesize doctoral findings into high-impact peer-reviewed contributions and policy rubrics conforming to: {reqs}."
        ]

    # 5. Section: Methodology or Approach
    if level == AcademicLevel.BACHELORS:
        if ptype == AcademicProposalType.EDUCATION:
            method = (
                f"This project utilizes a structured, four-phase instructional approach: "
                f"(1) Initial Needs Assessment through surveys and student interviews to establish baseline understanding of {topic}; "
                f"(2) Curriculum Material Development incorporating interactive modules and clear learning rubrics; "
                f"(3) Classroom Implementation across a targeted cohort to test feasibility; and "
                f"(4) Learning Evaluation comparing pre- and post-implementation scores to ensure {purpose} is attained."
            )
        elif ptype == AcademicProposalType.BUSINESS:
            method = (
                f"The business execution plan follows a milestone-driven strategy: "
                f"(1) Market & Competitor Discovery analyzing pricing, demand, and customer personas for {topic}; "
                f"(2) Operational Workflow Design establishing cost structures, delivery timelines, and risk controls; "
                f"(3) Pilot Launch testing minimum viable deliverables with key customer segments; and "
                f"(4) Financial and KPI Review to confirm operational profitability and deliver on {purpose}."
            )
        else:
            method = (
                f"The social media rollout follows a proven 4-stage playbook: "
                f"(1) Audience and Competitor Audit identifying top-performing content formats for {topic}; "
                f"(2) Content Creation Sprint producing educational carousels, short-form video scripts, and engagement hooks; "
                f"(3) Multi-Channel Publishing Schedule optimizing posting cadence across platforms; and "
                f"(4) Analytics Review tracking reach, click-through rates, and community growth to satisfy {purpose}."
            )
    elif level == AcademicLevel.MASTERS:
        if ptype == AcademicProposalType.EDUCATION:
            method = (
                f"This research employs a quasi-experimental, mixed-methods design. "
                f"Phase 1 conducts a systematic diagnostic audit and validated diagnostic survey instrument measuring student cognitive load and engagement in {topic}. "
                f"Phase 2 deploys an intervention protocol utilizing modern pedagogical scaffolding and digital feedback loops. "
                f"Phase 3 performs rigorous statistical analysis (including paired t-tests, ANOVA, and qualitative thematic analysis) "
                f"to measure educational yield against baseline cohorts, validating hypotheses relating to {purpose}."
            )
        elif ptype == AcademicProposalType.BUSINESS:
            method = (
                f"The strategic methodology integrates quantitative market modeling with agile execution sprints. "
                f"Phase 1 conducts unit economic sensitivity analysis, competitive benchmarking, and stakeholder elicitation on {topic}. "
                f"Phase 2 engineers an enterprise operational framework featuring automated reporting and cross-functional alignment. "
                f"Phase 3 tests the model via a controlled commercial pilot, measuring customer acquisition cost (CAC), lifetime value (LTV), "
                f"and operational efficiency to ensure empirical validation of {purpose}."
            )
        else:
            method = (
                f"This research utilizes an empirical multi-funnel growth architecture. "
                f"Phase 1 establishes algorithmic baseline tracking, audience sentiment clustering, and conversion telemetry for {topic}. "
                f"Phase 2 deploys controlled A/B split-testing across messaging variants, visual assets, and distribution algorithms. "
                f"Phase 3 applies multivariate regression and attribution modeling to isolate engagement drivers, "
                f"optimizing return on ad spend (ROAS) and organic virality to achieve {purpose}."
            )
    else:  # PhD
        if ptype == AcademicProposalType.EDUCATION:
            method = (
                f"This doctoral dissertation adopts an advanced, multi-phase convergent mixed-methods epistemological framework (Creswell & Plano Clark). "
                f"Strand A consists of a longitudinal, multi-site empirical investigation (N > 500) measuring cognitive absorption, self-efficacy, and learning outcomes in {topic} using structural equation modeling (SEM). "
                f"Strand B employs phenomenological and grounded theory qualitative protocols, gathering semi-structured in-depth interviews from educators and policy leaders. "
                f"Methodological triangulation and confirmatory factor analysis (CFA) are systematically deployed to ensure construct validity, internal consistency (Cronbach's alpha > 0.85), and generalizability for {purpose}."
            )
        elif ptype == AcademicProposalType.BUSINESS:
            method = (
                f"This study deploys an advanced econometric and dynamic capabilities methodology. "
                f"The empirical framework incorporates panel data econometrics, difference-in-differences (DiD) estimation, and machine learning predictive clustering to analyze firm-level performance in {topic}. "
                f"Robustness checks include instrumental variables (IV) estimation and Monte Carlo simulations to mitigate endogeneity concerns. "
                f"Qualitative executive cross-case synthesis provides deep contextual validation, establishing a comprehensive theoretical paradigm for {purpose}."
            )
        else:
            method = (
                f"This doctoral research employs a computational social science framework combining natural language processing (NLP), large-scale network graph theory, and longitudinal sentiment analysis. "
                f"The data corpus comprises > 1,000,000 algorithmic platform interactions and community graph nodes surrounding {topic}. "
                f"Network centrality algorithms (PageRank, Betweenness) and latent Dirichlet allocation (LDA) topic modeling delineate information cascade dynamics. "
                f"Empirical models are subjected to rigorous cross-validation and counterfactual causal inference to uncover the governing mechanisms of {purpose}."
            )

    # 6. Section: Expected Outcomes / Benefits
    if level == AcademicLevel.BACHELORS:
        outcomes = (
            f"Upon project completion, expected outcomes include: "
            f"(1) A fully tested and documented working solution for {topic}; "
            f"(2) Measurable improvement in user engagement, retention, or operational efficiency; "
            f"(3) A clear implementation guide empowering {audience} to replicate findings easily; and "
            f"(4) A robust final report satisfying all undergraduate academic and institutional requirements."
        )
    elif level == AcademicLevel.MASTERS:
        outcomes = (
            f"Anticipated contributions and deliverables encompass: "
            f"(1) An empirically validated operational model advancing current industry and academic benchmarks for {topic}; "
            f"(2) Statistically significant enhancements in performance metrics, directly demonstrating attainment of {purpose}; "
            f"(3) Comprehensive risk mitigation and scalability protocols designed for enterprise or institutional deployment; and "
            f"(4) A publishable postgraduate thesis contributing directly to the body of applied research."
        )
    else:  # PhD
        outcomes = (
            f"The transformative outcomes of this doctoral inquiry include: "
            f"(1) A seminal, peer-reviewed theoretical framework redefining the academic discourse on {topic}; "
            f"(2) Empirical resolution of long-standing causal ambiguities regarding {purpose}, supported by high-dimensional data; "
            f"(3) Novel methodological instruments and validated scales ready for cross-disciplinary adoption; and "
            f"(4) Actionable policy whitepapers and strategic doctrines providing authoritative guidance to {audience} and international bodies."
        )

    # 7. Section: Conclusion
    if level == AcademicLevel.BACHELORS:
        conclusion = (
            f"In conclusion, this proposal provides a practical, well-scoped roadmap to tackle {topic}. "
            f"By combining clear milestones with actionable steps, the project guarantees measurable progress toward {purpose}. "
            f"With the support of {audience}, this initiative will deliver practical value, high educational quality, "
            f"and a strong foundation for future study or professional implementation."
        )
    elif level == AcademicLevel.MASTERS:
        conclusion = (
            f"In summary, this proposal establishes a methodologically sound and strategically imperative approach "
            f"to addressing {topic}. By synthesizing robust analytical models with real-world execution, the initiative "
            f"resolves existing systemic inefficiencies to definitively accomplish {purpose}. "
            f"The proposed study promises substantial returns in organizational capability and applied academic scholarship."
        )
    else:  # PhD
        conclusion = (
            f"In conclusion, this doctoral dissertation proposal provides a rigorous, groundbreaking intervention into {topic}. "
            f"Through philosophical clarity, advanced methodological triangulation, and uncompromising empirical standards, "
            f"the investigation dismantles theoretical stagnation and establishes a new frontier in the discipline. "
            f"The anticipated yields will permanently advance scholarly inquiry, empower {audience} with definitive insights, "
            f"and set a new gold standard in the field."
        )

    # Level Insights description
    if level == AcademicLevel.BACHELORS:
        level_insights = (
            "Calibrated for Undergraduate / Bachelor's Level: Emphasizes conceptual clarity, foundational literature, "
            "direct practical application, and clearly bounded milestone execution."
        )
    elif level == AcademicLevel.MASTERS:
        level_insights = (
            "Calibrated for Postgraduate / Master's Level: Emphasizes theoretical frameworks, comparative synthesis, "
            "empirical justification, and rigorous methodology."
        )
    else:
        level_insights = (
            "Calibrated for Doctoral / PhD Level: Emphasizes epistemological grounding, identification of critical gaps "
            "in extant literature, rigorous mixed-methods/validation protocols, and definitive scholarly contribution."
        )

    # Assemble raw markdown
    objectives_md = "\n".join([f"- {obj}" for obj in objs])
    raw_markdown = f"""# {title}

**Academic Level:** {level.value}  
**Proposal Type:** {ptype.value}  
**Target Audience:** {audience}  
**Guidelines & Requirements:** {reqs}  

---

## 1. Title
**{title}**

## 2. Introduction / Background
{intro}

## 3. Problem Statement
{prob}

## 4. Objectives
{objectives_md}

## 5. Methodology or Approach
{method}

## 6. Expected Outcomes / Benefits
{outcomes}

## 7. Conclusion
{conclusion}

---
*Generated by Proposal Strategist Agent (Academic & Professional Division)*
"""

    word_count = count_words(raw_markdown)

    return AcademicProposalResponse(
        title=title,
        academic_level=level,
        proposal_type=ptype,
        introduction_background=intro,
        problem_statement=prob,
        objectives=objs,
        methodology_approach=method,
        expected_outcomes_benefits=outcomes,
        conclusion=conclusion,
        raw_markdown=raw_markdown,
        word_count=word_count,
        provider_used="offline (academic strategist engine)",
        level_insights=level_insights
    )
