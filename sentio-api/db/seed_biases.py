"""Seed the biases table with 30 cognitive biases.

Usage:
    python db/seed_biases.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import get_supabase

BIASES = [
    {
        "slug": "confirmation-bias",
        "name": "Confirmation Bias",
        "category": "belief",
        "description": (
            "The tendency to search for, interpret, and recall information that confirms "
            "existing beliefs while ignoring contradictory evidence. People with this bias "
            "seek out news, opinions, and data that align with what they already think, "
            "creating an echo chamber that reinforces pre-existing views."
        ),
        "example": (
            "A manager who believes a certain employee is underperforming notices every small "
            "mistake they make but ignores their successes, building a case for dismissal "
            "that feels objectively justified."
        ),
        "research_summary": (
            "Wason's (1960) card-selection experiments demonstrated that people preferentially "
            "seek confirming over disconfirming evidence, a finding replicated extensively "
            "in social and cognitive psychology."
        ),
        "detection_signals": [
            "seeks only agreeing sources",
            "dismisses contradictory data",
            "recalls supporting evidence more vividly",
        ],
        "related_bias_slugs": ["availability-heuristic", "anchoring-bias"],
        "severity_weight": 1.5,
        "prevalence_pct": 85,
    },
    {
        "slug": "availability-heuristic",
        "name": "Availability Heuristic",
        "category": "memory",
        "description": (
            "Judging the probability of events based on how easily examples come to mind "
            "rather than on actual statistical frequency. Events that are vivid, recent, "
            "or emotionally charged feel more common than they actually are."
        ),
        "example": (
            "After seeing several news reports about plane crashes, a traveller becomes "
            "convinced that flying is extremely dangerous and chooses to drive instead, "
            "despite driving being statistically far more risky."
        ),
        "research_summary": (
            "Tversky and Kahneman (1973) coined the term and showed that people estimate "
            "frequency by how easily instances are recalled, leading to systematic "
            "overestimates of dramatic but rare events."
        ),
        "detection_signals": [
            "overestimates vivid risks",
            "recent news influences probability judgements",
            "ignores base rates",
        ],
        "related_bias_slugs": ["recency-bias", "confirmation-bias"],
        "severity_weight": 1.2,
        "prevalence_pct": 72,
    },
    {
        "slug": "anchoring-bias",
        "name": "Anchoring Bias",
        "category": "decision",
        "description": (
            "Over-relying on the first piece of information encountered when making "
            "decisions, even when that anchor is arbitrary or irrelevant. Subsequent "
            "estimates and judgements adjust insufficiently away from the initial anchor."
        ),
        "example": (
            "A car salesperson shows a buyer a ₹15 lakh vehicle first; when the buyer "
            "then looks at a ₹10 lakh car, it feels like a bargain, even though the "
            "second car may be overpriced on its own merits."
        ),
        "research_summary": (
            "Tversky and Kahneman (1974) demonstrated anchoring by showing that random "
            "wheel-of-fortune spins influenced participants' subsequent numerical estimates, "
            "establishing anchoring as a robust and pervasive cognitive phenomenon."
        ),
        "detection_signals": [
            "initial number dominates negotiation",
            "insufficient adjustment from starting point",
            "irrelevant figures affect judgement",
        ],
        "related_bias_slugs": ["sunk-cost-fallacy", "status-quo-bias"],
        "severity_weight": 1.3,
        "prevalence_pct": 78,
    },
    {
        "slug": "dunning-kruger-effect",
        "name": "Dunning-Kruger Effect",
        "category": "self",
        "description": (
            "People with limited knowledge or competence in a domain overestimate their "
            "own abilities, while true experts tend to underestimate theirs. The least "
            "skilled individuals lack the metacognitive ability to recognise their own "
            "deficiencies."
        ),
        "example": (
            "A first-year medical student who has read one textbook chapter confidently "
            "disputes an experienced doctor's diagnosis, not yet knowing enough to "
            "understand what they don't know."
        ),
        "research_summary": (
            "Kruger and Dunning (1999) showed across multiple domains — logic, grammar, "
            "and humour — that bottom-quartile performers rated themselves above average, "
            "while top performers underestimated their relative standing."
        ),
        "detection_signals": [
            "overconfident in new domains",
            "dismisses expert opinion",
            "rarely expresses uncertainty",
        ],
        "related_bias_slugs": ["overconfidence-bias", "blind-spot-bias"],
        "severity_weight": 1.4,
        "prevalence_pct": 90,
    },
    {
        "slug": "sunk-cost-fallacy",
        "name": "Sunk Cost Fallacy",
        "category": "decision",
        "description": (
            "Continuing a behaviour or endeavour because of previously invested resources "
            "(time, money, or effort) rather than evaluating the future value of continuing. "
            "The emotional weight of past investments distorts rational forward-looking "
            "analysis."
        ),
        "example": (
            "A startup founder keeps pouring money into a failing product for two extra "
            "years because they have already spent ₹50 lakhs on development, even though "
            "market data clearly shows no demand."
        ),
        "research_summary": (
            "Arkes and Blumer (1985) demonstrated the sunk-cost effect experimentally and "
            "proposed that it stems from a desire to avoid appearing wasteful, making it "
            "especially potent when investments are visible to others."
        ),
        "detection_signals": [
            "justifies continuation with past investment",
            "avoids cutting losses",
            "frames quitting as failure",
        ],
        "related_bias_slugs": ["loss-aversion", "anchoring-bias"],
        "severity_weight": 1.3,
        "prevalence_pct": 68,
    },
    {
        "slug": "halo-effect",
        "name": "Halo Effect",
        "category": "social",
        "description": (
            "Letting one positive trait or first impression of a person, brand, or thing "
            "cast a positive glow over unrelated qualities. An overall favourable evaluation "
            "is extrapolated from a single admired characteristic."
        ),
        "example": (
            "An interviewer gives a candidate higher scores on technical ability and "
            "work-ethic ratings simply because the candidate is well-dressed and made "
            "strong eye contact, qualities unrelated to job performance."
        ),
        "research_summary": (
            "Thorndike (1920) first identified the halo effect in military officer ratings, "
            "and subsequent meta-analyses confirm it is one of the most widespread sources "
            "of bias in performance appraisals and consumer judgements."
        ),
        "detection_signals": [
            "one trait drives all ratings",
            "attractive people judged as more competent",
            "brand reputation overrides product evidence",
        ],
        "related_bias_slugs": ["horn-effect", "in-group-bias"],
        "severity_weight": 1.2,
        "prevalence_pct": 75,
    },
    {
        "slug": "fundamental-attribution-error",
        "name": "Fundamental Attribution Error",
        "category": "social",
        "description": (
            "The tendency to attribute other people's actions to their character or "
            "personality while attributing your own actions to circumstances and "
            "situational factors. We see others as agents acting from disposition; "
            "ourselves as responding to context."
        ),
        "example": (
            "When a colleague submits a report late, you conclude they are disorganised "
            "and lazy. When you submit a report late, you explain it as the result of an "
            "unusually heavy workload and unclear brief from management."
        ),
        "research_summary": (
            "Ross (1977) coined the term after Jones and Harris (1967) showed that people "
            "inferred attitudes consistent with essays even when told authors were assigned "
            "positions, highlighting the pervasive tendency to over-attribute behaviour to "
            "disposition."
        ),
        "detection_signals": [
            "blames others' personality for failures",
            "excuses own failures with context",
            "ignores situational constraints on others",
        ],
        "related_bias_slugs": ["self-serving-bias", "halo-effect"],
        "severity_weight": 1.3,
        "prevalence_pct": 82,
    },
    {
        "slug": "bandwagon-effect",
        "name": "Bandwagon Effect",
        "category": "social",
        "description": (
            "Adopting beliefs, opinions, or behaviours because many others do, regardless "
            "of the underlying evidence. The popularity of a view increases its perceived "
            "correctness, creating self-reinforcing social cascades."
        ),
        "example": (
            "An investor buys a cryptocurrency purely because social media is full of "
            "posts about others getting rich from it, without researching the asset's "
            "fundamentals or their own risk tolerance."
        ),
        "research_summary": (
            "Asch's (1951) conformity experiments showed that people publicly agree with "
            "obviously wrong answers when surrounded by confederates who give those answers, "
            "demonstrating how powerful social consensus is in shaping expressed beliefs."
        ),
        "detection_signals": [
            "popularity cited as evidence",
            "changes opinion when majority disagrees",
            "uncomfortable holding minority views",
        ],
        "related_bias_slugs": ["groupthink", "in-group-bias"],
        "severity_weight": 1.1,
        "prevalence_pct": 70,
    },
    {
        "slug": "optimism-bias",
        "name": "Optimism Bias",
        "category": "self",
        "description": (
            "Overestimating the likelihood of positive outcomes and underestimating "
            "the likelihood of negative ones in your own future compared with others. "
            "Most people believe they are more likely than average to succeed and less "
            "likely than average to encounter misfortune."
        ),
        "example": (
            "An entrepreneur launches a new restaurant, convinced their venture will "
            "thrive despite knowing that roughly 60% of restaurants close within the "
            "first year, believing their situation is different."
        ),
        "research_summary": (
            "Weinstein (1980) first documented unrealistic optimism about life events, "
            "and Sharot et al. (2011) identified the neural correlates in the rostral "
            "anterior cingulate cortex that drive selective updating toward positive "
            "information."
        ),
        "detection_signals": [
            "underestimates personal risks",
            "believes own projects are exception to failure rates",
            "rarely plans for negative scenarios",
        ],
        "related_bias_slugs": ["overconfidence-bias", "planning-fallacy"],
        "severity_weight": 1.1,
        "prevalence_pct": 65,
    },
    {
        "slug": "recency-bias",
        "name": "Recency Bias",
        "category": "memory",
        "description": (
            "Giving disproportionate weight to recent events, experiences, or data "
            "points when making judgements and predictions, at the expense of older "
            "but equally relevant information."
        ),
        "example": (
            "A fund manager overweights the past six months of strong market performance "
            "when projecting returns for the next year, ignoring the longer historical "
            "pattern of cyclical downturns."
        ),
        "research_summary": (
            "Murdock (1962) established the serial-position effect showing superior recall "
            "of recent list items; Benartzi and Thaler (1995) extended this to financial "
            "decision-making, linking recency bias to myopic loss aversion in investors."
        ),
        "detection_signals": [
            "over-indexes on last quarter's data",
            "forgets long-term trend when recent spike occurs",
            "changes strategy based on very recent events",
        ],
        "related_bias_slugs": ["availability-heuristic", "anchoring-bias"],
        "severity_weight": 1.2,
        "prevalence_pct": 73,
    },
    {
        "slug": "status-quo-bias",
        "name": "Status Quo Bias",
        "category": "decision",
        "description": (
            "A preference for the current state of affairs, such that any change is "
            "perceived as a loss even when switching to an alternative would yield "
            "net benefits. The default option carries disproportionate staying power."
        ),
        "example": (
            "An employee remains in a poorly-paying job for three extra years because "
            "looking for a new role feels risky, even though multiple better opportunities "
            "exist that would increase both salary and job satisfaction."
        ),
        "research_summary": (
            "Samuelson and Zeckhauser (1988) coined the term and showed experimentally "
            "that people systematically favour current arrangements, a tendency amplified "
            "by loss aversion and omission bias."
        ),
        "detection_signals": [
            "avoids changing default settings",
            "frames any change as risky",
            "inaction feels safer than action",
        ],
        "related_bias_slugs": ["loss-aversion", "sunk-cost-fallacy"],
        "severity_weight": 1.1,
        "prevalence_pct": 71,
    },
    {
        "slug": "in-group-bias",
        "name": "In-Group Bias",
        "category": "social",
        "description": (
            "Favouring people who belong to the same group as you — whether defined by "
            "nationality, religion, profession, sports team, or any shared identity — "
            "over those in out-groups, often assigning them more positive traits and "
            "more charitable interpretations."
        ),
        "example": (
            "A hiring manager unconsciously scores resumes from candidates who attended "
            "the same college as them higher on 'cultural fit', independent of actual "
            "skills or experience listed."
        ),
        "research_summary": (
            "Tajfel and Turner's (1979) Social Identity Theory demonstrated that even "
            "minimal group membership (arbitrary assignment to a 'red' or 'blue' group) "
            "is sufficient to produce in-group favouritism and out-group discrimination."
        ),
        "detection_signals": [
            "gives benefit of the doubt only to in-group",
            "attributes out-group failures to disposition",
            "overestimates in-group competence",
        ],
        "related_bias_slugs": ["bandwagon-effect", "halo-effect"],
        "severity_weight": 1.3,
        "prevalence_pct": 80,
    },
    {
        "slug": "overconfidence-bias",
        "name": "Overconfidence Bias",
        "category": "self",
        "description": (
            "Placing excessive confidence in your own answers, judgements, or abilities, "
            "leading to predictions that are more certain than the evidence warrants. "
            "Overconfidence manifests as overprecision (too narrow confidence intervals), "
            "overplacement (ranking oneself above average), and overestimation."
        ),
        "example": (
            "A trader places large, leveraged bets on a stock because they are 'certain' "
            "based on their analysis, ignoring market uncertainty and the high failure "
            "rate of similar calls by experienced analysts."
        ),
        "research_summary": (
            "Lichtenstein, Fischhoff, and Phillips (1982) documented that people's "
            "confidence in their factual answers consistently exceeds their accuracy, "
            "a finding replicated across cultures, domains, and expertise levels."
        ),
        "detection_signals": [
            "provides narrow confidence intervals",
            "rarely says 'I don't know'",
            "surprised by failure more than expected",
        ],
        "related_bias_slugs": ["dunning-kruger-effect", "planning-fallacy"],
        "severity_weight": 1.4,
        "prevalence_pct": 88,
    },
    {
        "slug": "loss-aversion",
        "name": "Loss Aversion",
        "category": "decision",
        "description": (
            "The tendency to prefer avoiding losses over acquiring equivalent gains. "
            "Psychologically, losses feel roughly twice as painful as gains of the same "
            "magnitude feel pleasurable, leading to risk-averse choices in gain domains "
            "and risk-seeking choices when facing certain losses."
        ),
        "example": (
            "An investor holds a losing stock long past any rational point because selling "
            "would make the loss 'real', while simultaneously taking profits too quickly "
            "on winning stocks to lock in gains before they disappear."
        ),
        "research_summary": (
            "Kahneman and Tversky (1979) formalised loss aversion in Prospect Theory, "
            "showing the value function is steeper in the loss domain than the gain "
            "domain, with a loss-to-gain sensitivity ratio of approximately 2:1."
        ),
        "detection_signals": [
            "holds losing investments hoping to break even",
            "refuses beneficial gambles framed as possible loss",
            "motivated more by avoiding pain than achieving gain",
        ],
        "related_bias_slugs": ["sunk-cost-fallacy", "status-quo-bias"],
        "severity_weight": 1.4,
        "prevalence_pct": 85,
    },
    {
        "slug": "planning-fallacy",
        "name": "Planning Fallacy",
        "category": "decision",
        "description": (
            "Underestimating the time, costs, and risks of future actions while "
            "overestimating the benefits and likelihood of completion on schedule. "
            "People focus on their specific plan rather than the base rate of similar "
            "projects."
        ),
        "example": (
            "A software team estimates a feature will take two weeks, ignoring that "
            "their last five similar features each took four to six weeks. The feature "
            "ends up taking five weeks, delaying a product launch."
        ),
        "research_summary": (
            "Kahneman and Tversky (1979) identified the planning fallacy and Buehler, "
            "Griffin, and Ross (1994) showed it persists even when people are explicitly "
            "reminded of their past project overruns, because inside-view thinking "
            "dominates outside-view base rates."
        ),
        "detection_signals": [
            "consistently delivers late",
            "focuses only on best-case scenario",
            "ignores base rate of similar projects",
        ],
        "related_bias_slugs": ["optimism-bias", "overconfidence-bias"],
        "severity_weight": 1.2,
        "prevalence_pct": 76,
    },
    {
        "slug": "hindsight-bias",
        "name": "Hindsight Bias",
        "category": "memory",
        "description": (
            "After learning an outcome, believing you would have predicted it beforehand. "
            "Events that were genuinely uncertain are retrospectively perceived as having "
            "been inevitable or highly predictable, distorting memory of prior beliefs."
        ),
        "example": (
            "After a company's stock price collapses, an analyst says 'I always knew "
            "their debt-to-equity ratio was unsustainable,' despite having given the "
            "stock a 'buy' rating just three months earlier."
        ),
        "research_summary": (
            "Fischhoff (1975) coined the term 'creeping determinism' and demonstrated "
            "that outcome knowledge shifts memory for prior probability estimates, a "
            "phenomenon found to be highly resistant to debiasing instructions."
        ),
        "detection_signals": [
            "claims prior knowledge of past events",
            "memory of predictions shifts toward outcome",
            "dismisses uncertainty in retrospect",
        ],
        "related_bias_slugs": ["confirmation-bias", "overconfidence-bias"],
        "severity_weight": 1.1,
        "prevalence_pct": 74,
    },
    {
        "slug": "framing-effect",
        "name": "Framing Effect",
        "category": "reasoning",
        "description": (
            "Drawing different conclusions from the same information depending on how "
            "it is presented. The way a choice or fact is worded — positively or "
            "negatively, as a gain or a loss — systematically alters preferences and "
            "decisions even when the underlying options are mathematically identical."
        ),
        "example": (
            "Patients shown a surgical procedure described as having a '90% survival "
            "rate' are far more willing to consent than those told it has a '10% "
            "mortality rate', even though both statements convey the same probability."
        ),
        "research_summary": (
            "Tversky and Kahneman's (1981) Asian Disease Problem showed that positive "
            "frames elicit risk-averse choices while negative frames elicit risk-seeking "
            "ones with identical expected outcomes, demonstrating that preference is "
            "context-dependent rather than stable."
        ),
        "detection_signals": [
            "preferences change with positive vs negative phrasing",
            "loss frame triggers avoidance regardless of expected value",
            "susceptible to marketing language",
        ],
        "related_bias_slugs": ["anchoring-bias", "loss-aversion"],
        "severity_weight": 1.2,
        "prevalence_pct": 79,
    },
    {
        "slug": "self-serving-bias",
        "name": "Self-Serving Bias",
        "category": "self",
        "description": (
            "Attributing successes to personal qualities such as skill, effort, or "
            "intelligence, while attributing failures to external factors like bad luck, "
            "unfair conditions, or other people. This protects self-esteem but distorts "
            "accurate self-assessment."
        ),
        "example": (
            "A student who passes an exam credits their intelligence and hard work, "
            "but when they fail the next exam, blames the professor's confusing questions "
            "and inadequate course materials."
        ),
        "research_summary": (
            "Miller and Ross (1975) reviewed extensive experimental literature showing "
            "the asymmetry in causal attribution for success and failure, noting it "
            "is more pronounced under ego threat and in individualistic cultures."
        ),
        "detection_signals": [
            "success attributed to ability, failure to circumstance",
            "rarely acknowledges personal contribution to failure",
            "credit-claiming in team contexts",
        ],
        "related_bias_slugs": ["fundamental-attribution-error", "overconfidence-bias"],
        "severity_weight": 1.2,
        "prevalence_pct": 77,
    },
    {
        "slug": "groupthink",
        "name": "Groupthink",
        "category": "social",
        "description": (
            "A phenomenon where the desire for harmony and conformity within a cohesive "
            "group overrides realistic appraisal of alternatives. Dissenting voices are "
            "suppressed, illusions of unanimity emerge, and the group reaches poor "
            "decisions that individuals might not make alone."
        ),
        "example": (
            "A leadership team unanimously approves a risky acquisition because the CEO "
            "seems enthusiastic and team members don't want to appear obstructionist, "
            "even though several members privately have serious reservations."
        ),
        "research_summary": (
            "Janis (1972) introduced groupthink while analysing historical foreign-policy "
            "fiascos including the Bay of Pigs invasion, identifying eight symptoms such "
            "as illusions of invulnerability, collective rationalization, and "
            "self-appointed mindguards."
        ),
        "detection_signals": [
            "dissent is suppressed or self-censored",
            "group feels invulnerable",
            "outside information not actively sought",
        ],
        "related_bias_slugs": ["bandwagon-effect", "in-group-bias"],
        "severity_weight": 1.3,
        "prevalence_pct": 66,
    },
    {
        "slug": "catastrophizing",
        "name": "Catastrophizing",
        "category": "reasoning",
        "description": (
            "Assuming the worst possible outcome from any negative event or difficulty, "
            "magnifying the significance of problems beyond what the evidence supports. "
            "Catastrophizing amplifies anxiety and interferes with proportionate "
            "problem-solving."
        ),
        "example": (
            "After making a minor error in a presentation, a person becomes convinced "
            "their entire career is ruined and their colleagues will never trust them "
            "again, spending days ruminating instead of moving on."
        ),
        "research_summary": (
            "Beck (1976) identified catastrophizing as a core cognitive distortion in "
            "depression and anxiety, and Sullivan et al. (2001) developed the Pain "
            "Catastrophizing Scale showing it predicts poorer health outcomes "
            "independently of pain intensity."
        ),
        "detection_signals": [
            "minor setbacks feel career-ending",
            "imagines extreme worst-case scenarios",
            "difficulty proportioning emotional response",
        ],
        "related_bias_slugs": ["all-or-nothing-thinking", "emotional-reasoning"],
        "severity_weight": 1.2,
        "prevalence_pct": 62,
    },
    {
        "slug": "emotional-reasoning",
        "name": "Emotional Reasoning",
        "category": "reasoning",
        "description": (
            "Believing something must be true because it feels true emotionally, treating "
            "emotional states as evidence about external reality. If you feel afraid, "
            "there must be real danger; if you feel worthless, you must be worthless."
        ),
        "example": (
            "A person feels anxious about a flight and concludes 'I feel scared, "
            "therefore this flight is genuinely dangerous,' cancelling their trip "
            "despite rationally knowing the statistical safety of air travel."
        ),
        "research_summary": (
            "Burns (1980) popularised emotional reasoning as a cognitive distortion "
            "in CBT, and subsequent experimental work by Arntz et al. (1995) confirmed "
            "that anxiety patients are more likely to treat felt threat as evidence of "
            "actual threat compared to controls."
        ),
        "detection_signals": [
            "treats feelings as facts",
            "uses 'I feel it therefore it is true' reasoning",
            "anxiety interpreted as evidence of real danger",
        ],
        "related_bias_slugs": ["catastrophizing", "confirmation-bias"],
        "severity_weight": 1.1,
        "prevalence_pct": 69,
    },
    {
        "slug": "all-or-nothing-thinking",
        "name": "All-or-Nothing Thinking",
        "category": "reasoning",
        "description": (
            "Viewing situations in absolute, black-and-white terms with no middle ground "
            "or shades of grey. Partial success is treated as total failure; any flaw "
            "renders a whole experience worthless. Also called dichotomous or polarised "
            "thinking."
        ),
        "example": (
            "A dieter who eats one biscuit concludes 'I've completely ruined my diet' "
            "and proceeds to eat an entire packet, reasoning that the day is already "
            "lost rather than returning to healthy choices at the next meal."
        ),
        "research_summary": (
            "Beck et al. (1979) identified all-or-nothing thinking as a central feature "
            "of depressive cognition, and subsequent meta-analyses confirm it correlates "
            "strongly with perfectionism, eating disorders, and borderline personality "
            "features."
        ),
        "detection_signals": [
            "uses always/never language frequently",
            "partial success labelled as failure",
            "any imperfection invalidates the whole",
        ],
        "related_bias_slugs": ["catastrophizing", "overgeneralization"],
        "severity_weight": 1.2,
        "prevalence_pct": 71,
    },
    {
        "slug": "overgeneralization",
        "name": "Overgeneralization",
        "category": "reasoning",
        "description": (
            "Drawing sweeping negative conclusions from a single event or a limited "
            "set of evidence and applying them universally. One disappointing experience "
            "becomes a permanent pattern; a single rejection means all future attempts "
            "will fail."
        ),
        "example": (
            "After one job rejection, a candidate thinks 'No company will ever hire me' "
            "and stops applying for positions, interpreting a single data point as "
            "definitive proof of a universal truth."
        ),
        "research_summary": (
            "Beck (1976) described overgeneralization as hallmark of depressive "
            "cognition; Alloy and Abramson's (1979) learned helplessness model links "
            "it to global, stable attributions for negative outcomes that predict "
            "future depressive episodes."
        ),
        "detection_signals": [
            "one event produces absolute predictions",
            "uses words like 'always' and 'never' after single incidents",
            "gives up after first failure",
        ],
        "related_bias_slugs": ["all-or-nothing-thinking", "labeling"],
        "severity_weight": 1.2,
        "prevalence_pct": 73,
    },
    {
        "slug": "labeling",
        "name": "Labeling",
        "category": "self",
        "description": (
            "Assigning a fixed, global, negative label to yourself or others based on "
            "specific behaviours or single events, rather than describing the behaviour "
            "itself. Labels compress complex, changeable people into rigid, immutable "
            "identities."
        ),
        "example": (
            "After forgetting a friend's birthday, a person thinks 'I am a terrible "
            "friend' rather than 'I forgot this time and should set a reminder', "
            "attaching a permanent identity label to a single action."
        ),
        "research_summary": (
            "Burns (1980) described labeling as an extreme form of overgeneralization "
            "in cognitive therapy; research on self-concept rigidity shows that global "
            "negative self-labels predict greater depression severity and treatment "
            "resistance."
        ),
        "detection_signals": [
            "describes self or others with fixed identity labels",
            "uses noun identities rather than verb descriptions",
            "global self-criticism after mistakes",
        ],
        "related_bias_slugs": ["overgeneralization", "self-serving-bias"],
        "severity_weight": 1.1,
        "prevalence_pct": 68,
    },
    {
        "slug": "personalization",
        "name": "Personalization",
        "category": "self",
        "description": (
            "Taking excessive personal responsibility for external events and other "
            "people's emotions, assuming you are the cause of things that are actually "
            "outside your control. Personalization creates guilt and anxiety over "
            "outcomes that have multiple or situational causes."
        ),
        "example": (
            "When a colleague seems upset after a meeting, a person immediately assumes "
            "'I must have said something to offend them,' spending the rest of the day "
            "worrying, without considering the colleague might be dealing with an "
            "unrelated personal problem."
        ),
        "research_summary": (
            "Beck (1976) identified personalization as a key distortion in depression, "
            "and research by Abramson, Seligman, and Teasdale (1978) linked internal, "
            "stable, global attributions for negative outcomes to depressive symptomology "
            "and suicide risk."
        ),
        "detection_signals": [
            "blames self for others' moods",
            "assumes causal role in unrelated events",
            "excessive guilt about outcomes beyond control",
        ],
        "related_bias_slugs": ["self-serving-bias", "fundamental-attribution-error"],
        "severity_weight": 1.1,
        "prevalence_pct": 65,
    },
    {
        "slug": "blind-spot-bias",
        "name": "Blind Spot Bias",
        "category": "self",
        "description": (
            "Recognising cognitive biases in other people's thinking and behaviour "
            "while failing to see those same biases operating in your own reasoning. "
            "Awareness of bias in general does not translate into recognition of one's "
            "own biased thinking."
        ),
        "example": (
            "A psychology professor teaches a class on confirmation bias and readily "
            "identifies it in political opponents, but does not notice how selectively "
            "they consume research that supports their preferred educational theories."
        ),
        "research_summary": (
            "Pronin, Lin, and Ross (2002) documented the bias blind spot, finding that "
            "people rate themselves as less biased than the average person on a wide "
            "range of cognitive and motivational biases, even after being educated about "
            "them."
        ),
        "detection_signals": [
            "readily identifies bias in others, rarely in self",
            "believes own reasoning is uniquely objective",
            "education about biases does not prompt self-reflection",
        ],
        "related_bias_slugs": ["dunning-kruger-effect", "overconfidence-bias"],
        "severity_weight": 1.3,
        "prevalence_pct": 84,
    },
    {
        "slug": "spotlight-effect",
        "name": "Spotlight Effect",
        "category": "social",
        "description": (
            "Overestimating how much other people notice and pay attention to your "
            "appearance, behaviour, and mistakes. People feel as though they are under "
            "a spotlight when in reality others are mostly focused on themselves."
        ),
        "example": (
            "A person spills coffee on their shirt in a meeting and spends the rest of "
            "the day convinced everyone in the office has noticed and is silently judging "
            "them, when in fact most colleagues have already forgotten the incident."
        ),
        "research_summary": (
            "Gilovich, Medvec, and Savitsky (2000) showed that people wearing embarrassing "
            "T-shirts estimated 50% of observers noticed, while actual observation rates "
            "were around 25%, demonstrating consistent overestimation of social attention."
        ),
        "detection_signals": [
            "high social anxiety about minor embarrassments",
            "assumes others notice appearance changes",
            "overestimates how long others dwell on one's mistakes",
        ],
        "related_bias_slugs": ["self-serving-bias", "personalization"],
        "severity_weight": 1.0,
        "prevalence_pct": 60,
    },
    {
        "slug": "survivorship-bias",
        "name": "Survivorship Bias",
        "category": "reasoning",
        "description": (
            "Drawing conclusions from visible successes while overlooking the failures "
            "that are not visible because they didn't survive long enough to be "
            "observed. This leads to overly optimistic beliefs about success strategies "
            "and unrealistic assessments of risk."
        ),
        "example": (
            "A business school highlights alumni who became successful entrepreneurs, "
            "leading students to believe entrepreneurship is a highly viable path, "
            "while never mentioning the 90% who tried and failed before they could "
            "be featured in alumni success stories."
        ),
        "research_summary": (
            "Wald's (1943) aircraft armour analysis is the classic example: engineers "
            "wanted to reinforce where returning planes were shot, but Wald recognised "
            "the unseen population — planes shot in other areas never returned. Brown "
            "et al. (1992) extended the concept to mutual fund performance data."
        ),
        "detection_signals": [
            "bases advice only on success cases",
            "ignores failures when evaluating strategies",
            "overestimates success rates from visible examples",
        ],
        "related_bias_slugs": ["confirmation-bias", "availability-heuristic"],
        "severity_weight": 1.2,
        "prevalence_pct": 77,
    },
    {
        "slug": "choice-supportive-bias",
        "name": "Choice-Supportive Bias",
        "category": "memory",
        "description": (
            "Retroactively attributing positive qualities to options you chose and "
            "negative qualities to options you rejected, even when your memory of the "
            "original attributes is distorted. Past choices are remembered as being "
            "better than they actually were."
        ),
        "example": (
            "A person who chose to study engineering over medicine later remembers the "
            "engineering programme as having been clearly the best option, forgetting "
            "the doubts they had at the time and misremembering the medicine programme "
            "as less appealing than it actually seemed."
        ),
        "research_summary": (
            "Mather, Shafir, and Johnson (2000) first demonstrated choice-supportive "
            "bias experimentally, showing participants' memories of chosen items' "
            "attributes shifted positively post-choice, consistent with cognitive "
            "dissonance reduction mechanisms."
        ),
        "detection_signals": [
            "past choices remembered as clearly superior",
            "negative attributes of unchosen options inflated over time",
            "difficulty acknowledging past decisions were risky or arbitrary",
        ],
        "related_bias_slugs": ["post-purchase-rationalization", "self-serving-bias"],
        "severity_weight": 1.0,
        "prevalence_pct": 70,
    },
    {
        "slug": "curse-of-knowledge",
        "name": "Curse of Knowledge",
        "category": "social",
        "description": (
            "Once you know something, it becomes very difficult to imagine not knowing "
            "it, causing you to overestimate how much others understand. Experts "
            "systematically underestimate how confusing their explanations are to "
            "novices."
        ),
        "example": (
            "A senior software engineer explains a complex system architecture to a "
            "new hire using jargon and assumed context, genuinely baffled when the "
            "newcomer is confused, because the engineer can no longer recall what it "
            "was like not to know these concepts."
        ),
        "research_summary": (
            "Camerer, Loewenstein, and Weber (1989) coined the term in an economics "
            "experiment where informed traders could not ignore their information when "
            "predicting uninformed traders' behaviour; Newton's (1990) tapping study "
            "showed listeners identified only 2.5% of tapped songs that tappers "
            "assumed were obvious."
        ),
        "detection_signals": [
            "explanations assume too much background knowledge",
            "frustrated when others don't understand 'obvious' things",
            "difficulty teaching or writing for beginners",
        ],
        "related_bias_slugs": ["fundamental-attribution-error", "overconfidence-bias"],
        "severity_weight": 1.1,
        "prevalence_pct": 72,
    },
]


def main() -> None:
    supabase = get_supabase()
    result = (
        supabase.table("biases")
        .upsert(BIASES, on_conflict="slug")
        .execute()
    )
    count = len(result.data) if result.data else 0
    print(f"Seeded {count} biases successfully.")


if __name__ == "__main__":
    main()
