"""Subject-aware MCQ templates shared by scope lessons and diagnostic items."""
from __future__ import annotations

from typing import Any

from app.services.content_generation.topic_map_source_context import TopicMapSourceContext

CORRECT_OPTIONS = ("A", "B", "C", "D")

CONTENT_FAMILY_ALIASES = {
    "life_orientation": "life_skills",
    "technology": "natural_sciences",
}


def content_family(family: str) -> str:
    return CONTENT_FAMILY_ALIASES.get(family, family)


def options_for_template(template: dict[str, Any], *, correct: str) -> tuple[dict[str, str], str]:
    correct_text = template["answers"]["A"]
    distractors = [template["answers"][key] for key in ("B", "C", "D")]
    correct_index = CORRECT_OPTIONS.index(correct)
    ordered_values = distractors[:]
    ordered_values.insert(correct_index, correct_text)
    options = {label: ordered_values[idx] for idx, label in enumerate(CORRECT_OPTIONS)}
    explanation = next(
        (
            template["explanations"][key]
            for key, value in template["answers"].items()
            if value == options[correct]
        ),
        template["explanations"]["A"],
    )
    return options, explanation


def base_mcq_templates(context: TopicMapSourceContext, *, family: str, sequence: int) -> list[dict[str, Any]]:
    """Core templates (3 per family) used for lesson practice sets."""
    family = content_family(family)
    topic = context.subtopic
    if family == "mathematics":
        n1 = 36 + sequence * 4 + context.grade * 3
        n2 = 18 + sequence * 2
        return _mathematics_core_templates(context.grade, topic, n1, n2)
    if family == "languages":
        return _languages_templates(context.grade, topic, sequence)
    if family == "natural_sciences":
        return _natural_sciences_templates(topic, sequence)
    if family == "social_sciences":
        return _social_sciences_templates(topic, sequence)
    if family == "coding_and_robotics":
        return _coding_templates(topic, sequence)
    return _life_skills_templates(topic, sequence, grade=context.grade)


def extended_mcq_templates(
    context: TopicMapSourceContext,
    *,
    family: str,
    sequence: int,
    band: str,
) -> list[dict[str, Any]]:
    """Expanded template pool for diagnostic item banks (10+ per family)."""
    family = content_family(family)
    templates = list(base_mcq_templates(context, family=family, sequence=sequence))
    if family == "mathematics":
        templates.extend(_mathematics_extended_templates(context.grade, context.subtopic, sequence, band))
    elif family == "languages":
        templates.extend(_languages_extended_templates(context.grade, context.subtopic, sequence))
    elif family == "natural_sciences":
        templates.extend(_natural_sciences_extended_templates(context.subtopic, sequence))
    elif family == "social_sciences":
        templates.extend(_social_sciences_extended_templates(context.subtopic, sequence))
    elif family == "coding_and_robotics":
        templates.extend(_coding_extended_templates(context.subtopic, sequence))
    else:
        templates.extend(_life_skills_extended_templates(context.subtopic, sequence, grade=context.grade))
    return templates


def topic_phrase(topic: str) -> str:
    """Shorten long CAPS subtopic labels so stems stay readable for younger grades."""
    label = topic.strip().lower()
    if len(label) <= 28:
        return label
    head = label.split(",")[0].strip()
    words = head.split()
    return " ".join(words[:2]) if len(words) > 2 else head


def pick_template(
    context: TopicMapSourceContext,
    *,
    family: str,
    sequence: int,
    band: str,
    extended: bool = False,
    pool_offset: int = 0,
) -> dict[str, Any]:
    pool = (
        extended_mcq_templates(context, family=family, sequence=sequence, band=band)
        if extended
        else base_mcq_templates(context, family=family, sequence=sequence)
    )
    template = pool[(sequence + pool_offset) % len(pool)]
    topic = topic_phrase(context.subtopic)
    long_topic = context.subtopic.strip().lower()
    if long_topic != topic and long_topic in template["question_text"].lower():
        template = {
            **template,
            "question_text": template["question_text"].replace(long_topic, topic),
        }
    return template


def _mathematics_core_templates(grade: int, topic: str, n1: int, n2: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    total = n1 + n2
    return [
        {
            "question_text": f"What is {n1} + {n2} when solving a Grade {grade} problem about {topic_l}?",
            "skill": "addition_word_problem",
            "answers": {
                "A": str(total),
                "B": str(total + 10),
                "C": str(total - 5),
                "D": str(total + 1),
            },
            "explanations": {
                "A": f"Add {n1} and {n2} to get {total}.",
                "B": "This adds an extra ten without reason.",
                "C": "This subtracts five incorrectly.",
                "D": "This adds one too many.",
            },
        },
        {
            "question_text": f"Which representation best shows place value for {total} in {topic_l}?",
            "skill": "place_value_representation",
            "answers": {
                "A": f"A table showing thousands, hundreds, tens and ones for {total}",
                "B": "A random list of digits with no place labels",
                "C": "A drawing unrelated to the number",
                "D": "The number written backwards only",
            },
            "explanations": {
                "A": "Place-value tables show the value of each digit clearly.",
                "B": "Digits without place labels hide value.",
                "C": "An unrelated drawing does not represent the number.",
                "D": "Reversing digits changes the number.",
            },
        },
        {
            "question_text": f"Lerato checks an answer for {topic_l} by counting back. Which check is best?",
            "skill": "answer_checking",
            "answers": {
                "A": "Use the inverse operation to confirm the result",
                "B": "Change the question and keep the same answer",
                "C": "Ignore the estimate and copy a friend's answer",
                "D": "Skip checking when the answer looks large",
            },
            "explanations": {
                "A": "Inverse operations confirm whether the calculation is correct.",
                "B": "Changing the question does not verify the original answer.",
                "C": "Copying without checking can repeat an error.",
                "D": "Large answers still need checking.",
            },
        },
    ]


def _mathematics_extended_templates(grade: int, topic: str, sequence: int, band: str) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    scale = {"easy": 1, "moderate": 2, "on_level": 3, "challenging": 4}.get(band, 2)
    base = 12 + sequence * 7 + grade * 5 * scale
    partner = 6 + sequence * 3 + scale
    product = base * partner
    difference = base - partner
    return [
        {
            "question_text": (
                f"A Grade {grade} tuckshop sells {base} snacks in the morning and {partner} in the afternoon "
                f"while learners study {topic_l}. How many snacks were sold altogether?"
            ),
            "skill": "multi_step_addition",
            "answers": {
                "A": str(base + partner),
                "B": str(base + partner + 10),
                "C": str(abs(base - partner)),
                "D": str(base + partner - 1),
            },
            "explanations": {
                "A": f"Add {base} and {partner} to find the total.",
                "B": "An extra ten was added without reason.",
                "C": "This uses subtraction instead of addition.",
                "D": "One was subtracted incorrectly from the total.",
            },
        },
        {
            "question_text": (
                f"Thabo has {base + partner} stickers and gives {partner} to a friend. "
                f"How many stickers remain?"
            ),
            "skill": "subtraction_word_problem",
            "answers": {
                "A": str(base),
                "B": str(base + partner),
                "C": str(partner),
                "D": str(base + 1),
            },
            "explanations": {
                "A": f"Subtract {partner} from {base + partner} to get {base}.",
                "B": "This is the starting amount, not what remains.",
                "C": "This is the amount given away, not what is left.",
                "D": "One too many was added to the answer.",
            },
        },
        {
            "question_text": f"Which number is greater: {base} or {partner} when comparing values in {topic_l}?",
            "skill": "compare_numbers",
            "answers": {
                "A": str(max(base, partner)),
                "B": str(min(base, partner)),
                "C": "They are always equal",
                "D": "Neither can be compared",
            },
            "explanations": {
                "A": f"{max(base, partner)} is greater than {min(base, partner)}.",
                "B": "This is the smaller number.",
                "C": "The numbers are different unless they match exactly.",
                "D": "Whole numbers can be compared on a number line.",
            },
        },
        {
            "question_text": f"What is {base} × {partner} in a Grade {grade} question about {topic_l}?",
            "skill": "multiplication_facts",
            "answers": {
                "A": str(product),
                "B": str(product + base),
                "C": str(base + partner),
                "D": str(product - partner),
            },
            "explanations": {
                "A": f"{base} × {partner} = {product}.",
                "B": "This adds instead of multiplying.",
                "C": "This adds the factors instead of multiplying them.",
                "D": "This subtracts from the product without reason.",
            },
        },
        {
            "question_text": (
                f"About how much is {base} + {partner}?"
                if grade <= 6
                else f"Which estimate is reasonable before calculating {base} + {partner} for {topic_l}?"
            ),
            "skill": "estimation",
            "answers": {
                "A": f"Between {base} and {base + partner + 20}",
                "B": "Exactly zero",
                "C": "Less than {min(base, partner)}",
                "D": "More than {base + partner + 500}",
            },
            "explanations": {
                "A": "A good estimate is near the expected sum.",
                "B": "Two positive numbers cannot sum to zero.",
                "C": "The sum must be greater than each addend when both are positive.",
                "D": "The estimate is far too large for these numbers.",
            },
        },
        {
            "question_text": f"The difference between {base + partner} and {partner} is:",
            "skill": "difference",
            "answers": {
                "A": str(difference),
                "B": str(base + partner),
                "C": str(partner),
                "D": str(difference + 10),
            },
            "explanations": {
                "A": f"{base + partner} − {partner} = {difference}.",
                "B": "This is the minuend, not the difference.",
                "C": "This is the subtrahend, not the difference.",
                "D": "Ten was added without reason.",
            },
        },
        {
            "question_text": (
                f"Which statement about {topic_l} and the number {base + partner} is true?"
            ),
            "skill": "number_sense",
            "answers": {
                "A": f"{base + partner} has a ones digit of {(base + partner) % 10}",
                "B": f"{base + partner} has a ones digit of 0 always",
                "C": "The ones digit cannot be found",
                "D": f"{base + partner} is not a whole number",
            },
            "explanations": {
                "A": "The ones digit is the remainder when dividing by 10.",
                "B": "Only multiples of ten have a ones digit of zero.",
                "C": "Whole numbers always have a ones digit.",
                "D": f"{base + partner} is a whole number in this question.",
            },
        },
    ]


def _languages_templates(grade: int, topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which sentence uses a comma correctly in a Grade {grade} text about {topic_l}?",
            "skill": "punctuation",
            "answers": {
                "A": f"After reading, the learners discussed {topic_l}.",
                "B": f"After reading the learners discussed {topic_l}",
                "C": f"After, reading the learners discussed {topic_l}.",
                "D": f"After reading the, learners discussed {topic_l}.",
            },
            "explanations": {
                "A": "A comma follows the introductory phrase correctly.",
                "B": "The sentence is missing punctuation.",
                "C": "The comma breaks the phrase incorrectly.",
                "D": "The comma is placed inside the subject.",
            },
        },
        {
            "question_text": f"Which word is the strongest verb for a report on {topic_l}?",
            "skill": "vocabulary",
            "answers": {
                "A": "analysed",
                "B": "did",
                "C": "went",
                "D": "got",
            },
            "explanations": {
                "A": "Analysed is precise and academic.",
                "B": "Did is too vague.",
                "C": "Went does not describe thinking.",
                "D": "Got is informal and unclear.",
            },
        },
        {
            "question_text": f"Which option best summarises a paragraph about {topic_l}?",
            "skill": "comprehension",
            "answers": {
                "A": f"It explains how {topic_l} helps learners read and write more accurately.",
                "B": "It lists every punctuation mark in the passage.",
                "C": "It only names the author of the passage.",
                "D": "It repeats one example sentence without a main idea.",
            },
            "explanations": {
                "A": "A summary states the main idea of the whole paragraph.",
                "B": "Listing punctuation is not a summary.",
                "C": "The author is not the main idea.",
                "D": "One detail alone is not a summary.",
            },
        },
    ]


def _languages_extended_templates(grade: int, topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which prefix changes the meaning of a word about {topic_l} correctly?",
            "skill": "morphology",
            "answers": {
                "A": "re- meaning again",
                "B": "re- meaning never",
                "C": "un- meaning always",
                "D": "mis- meaning correctly",
            },
            "explanations": {
                "A": "The prefix re- often means again.",
                "B": "Re- does not mean never.",
                "C": "Un- usually means not, not always.",
                "D": "Mis- usually means wrongly.",
            },
        },
        {
            "question_text": f"Which sentence is written in the past tense for {topic_l}?",
            "skill": "grammar",
            "answers": {
                "A": f"The class discussed {topic_l} yesterday.",
                "B": f"The class will discuss {topic_l} tomorrow.",
                "C": f"The class discusses {topic_l} every day.",
                "D": f"The class is discussing {topic_l} now.",
            },
            "explanations": {
                "A": "Discussed is past tense.",
                "B": "Will discuss is future tense.",
                "C": "Discusses is present tense.",
                "D": "Is discussing is present continuous.",
            },
        },
        {
            "question_text": f"Which reference word refers back to {topic_l} in a paragraph?",
            "skill": "cohesion",
            "answers": {
                "A": "this topic",
                "B": "a random number",
                "C": "the colour blue only",
                "D": "tomorrow's weather only",
            },
            "explanations": {
                "A": "This topic links to the idea in the previous sentence.",
                "B": "A number does not refer to a topic idea.",
                "C": "Colour alone does not refer to the topic.",
                "D": "Weather is unrelated unless the passage is about weather.",
            },
        },
    ]


def _natural_sciences_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which statement about {topic_l} is supported by observation?",
            "skill": "scientific_observation",
            "answers": {
                "A": "The measurement changed when the conditions changed.",
                "B": "Results can be guessed without apparatus.",
                "C": "Evidence is optional in an investigation.",
                "D": "A hypothesis cannot be tested.",
            },
            "explanations": {
                "A": "Observations should match measured evidence.",
                "B": "Scientists use evidence, not guesses alone.",
                "C": "Investigations require evidence.",
                "D": "Hypotheses are tested in investigations.",
            },
        },
        {
            "question_text": f"Which apparatus is most appropriate for a lesson on {topic_l}?",
            "skill": "apparatus_selection",
            "answers": {
                "A": "The tool named in the lesson method for measuring the quantity",
                "B": "A ruler used to measure temperature",
                "C": "A compass used to measure mass",
                "D": "Any object chosen at random",
            },
            "explanations": {
                "A": "Each quantity needs a suitable measuring tool.",
                "B": "Rulers measure length, not temperature.",
                "C": "Compasses are not used to measure mass.",
                "D": "Random objects are not valid apparatus.",
            },
        },
        {
            "question_text": f"Why should learners record results when studying {topic_l}?",
            "skill": "data_recording",
            "answers": {
                "A": "So patterns can be compared and conclusions checked",
                "B": "So they can ignore unexpected results",
                "C": "So they can change the data to match a guess",
                "D": "So they can skip the conclusion",
            },
            "explanations": {
                "A": "Records allow evidence-based conclusions.",
                "B": "Unexpected results still matter.",
                "C": "Data should not be changed to fit guesses.",
                "D": "Conclusions depend on recorded results.",
            },
        },
    ]


def _natural_sciences_extended_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"A fair test about {topic_l} should change:",
            "skill": "fair_test",
            "answers": {
                "A": "one variable only",
                "B": "every variable at once",
                "C": "nothing at all",
                "D": "only the conclusion",
            },
            "explanations": {
                "A": "Fair tests change one variable and keep others the same.",
                "B": "Changing everything makes results hard to interpret.",
                "C": "A test must change something to observe an effect.",
                "D": "The conclusion comes after the test.",
            },
        },
        {
            "question_text": f"Which safety rule is most important during {topic_l}?",
            "skill": "laboratory_safety",
            "answers": {
                "A": "Follow teacher instructions and wear protection when needed",
                "B": "Taste chemicals to check results",
                "C": "Leave spills unattended",
                "D": "Work far from the group",
            },
            "explanations": {
                "A": "Safety rules protect learners during practical work.",
                "B": "Never taste unknown substances in class.",
                "C": "Spills must be reported and cleaned safely.",
                "D": "Supervision and teamwork support safety.",
            },
        },
    ]


def _social_sciences_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which source would best answer a question about {topic_l} in the local area?",
            "skill": "source_analysis",
            "answers": {
                "A": "A community interview or local archive record",
                "B": "A fictional story with no historical details",
                "C": "A picture with no caption or date",
                "D": "An unrelated advertisement",
            },
            "explanations": {
                "A": "Local sources provide relevant evidence.",
                "B": "Fiction is not evidence on its own.",
                "C": "Uncaptioned pictures lack context.",
                "D": "Advertisements are not historical sources for this task.",
            },
        },
        {
            "question_text": f"When comparing places linked to {topic_l}, what should learners examine first?",
            "skill": "map_skills",
            "answers": {
                "A": "Physical features and human activities shown on the map",
                "B": "Only the colours used on the map",
                "C": "The title of the textbook page",
                "D": "The number of pages in the atlas",
            },
            "explanations": {
                "A": "Maps show features and activities that explain differences.",
                "B": "Colours alone do not explain places.",
                "C": "A page title is not map evidence.",
                "D": "Page count is irrelevant.",
            },
        },
        {
            "question_text": f"Which timeline order is logical for an event about {topic_l}?",
            "skill": "chronology",
            "answers": {
                "A": "Cause, event, consequence",
                "B": "Consequence, cause, event",
                "C": "Event, event, event with no order",
                "D": "Random order with no dates",
            },
            "explanations": {
                "A": "Timelines show cause and effect over time.",
                "B": "Consequences come after causes.",
                "C": "Events need chronological order.",
                "D": "Random order hides change over time.",
            },
        },
    ]


def _social_sciences_extended_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which question is best when investigating {topic_l}?",
            "skill": "enquiry_question",
            "answers": {
                "A": "What evidence shows how people were affected?",
                "B": "What is my favourite colour?",
                "C": "How many pages are in the textbook?",
                "D": "Who is the tallest learner in the class?",
            },
            "explanations": {
                "A": "Good enquiry questions focus on evidence and impact.",
                "B": "Personal preference is not a historical enquiry question.",
                "C": "Page count is not related to the topic.",
                "D": "Class height is unrelated to the topic.",
            },
        },
        {
            "question_text": f"Why is it important to compare sources about {topic_l}?",
            "skill": "compare_sources",
            "answers": {
                "A": "To check whether accounts agree or differ",
                "B": "To avoid reading either source",
                "C": "To copy one source only",
                "D": "To ignore dates and places",
            },
            "explanations": {
                "A": "Comparing sources strengthens historical conclusions.",
                "B": "Sources must be read to be useful.",
                "C": "One source alone may be incomplete.",
                "D": "Dates and places provide important context.",
            },
        },
    ]


def _coding_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"What is the first step in an algorithm for {topic_l}?",
            "skill": "algorithm_design",
            "answers": {
                "A": "Define the input and desired output",
                "B": "Run the robot before planning",
                "C": "Delete all previous commands randomly",
                "D": "Skip testing the sequence",
            },
            "explanations": {
                "A": "Algorithms start with a clear goal and inputs.",
                "B": "Planning should come before running.",
                "C": "Random deletion is not debugging.",
                "D": "Testing is part of good programming.",
            },
        },
        {
            "question_text": f"Which command sequence repeats an action three times in {topic_l}?",
            "skill": "loops",
            "answers": {
                "A": "repeat 3: move forward 1",
                "B": "move forward 1",
                "C": "repeat 1: move forward 3",
                "D": "turn right only",
            },
            "explanations": {
                "A": "The repeat block runs the action three times.",
                "B": "A single move does not repeat.",
                "C": "This repeats once, not three times.",
                "D": "Turning alone does not repeat the move.",
            },
        },
        {
            "question_text": f"Why is debugging important when learning {topic_l}?",
            "skill": "debugging",
            "answers": {
                "A": "It helps find and fix the step that causes the wrong output",
                "B": "It removes the need for planning",
                "C": "It guarantees the robot never stops",
                "D": "It allows learners to ignore test results",
            },
            "explanations": {
                "A": "Debugging locates the faulty step.",
                "B": "Planning is still required.",
                "C": "Debugging does not guarantee uninterrupted running.",
                "D": "Test results guide debugging.",
            },
        },
    ]


def _coding_extended_templates(topic: str, sequence: int) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    return [
        {
            "question_text": f"Which input–output pair matches a simple program for {topic_l}?",
            "skill": "input_output",
            "answers": {
                "A": "Input: button press, Output: LED on",
                "B": "Input: LED on, Output: button press",
                "C": "Input: nothing, Output: nothing always",
                "D": "Input: random guess, Output: skip testing",
            },
            "explanations": {
                "A": "The input triggers the output in a simple system.",
                "B": "Outputs do not usually become inputs in this task.",
                "C": "A useful program responds to an input.",
                "D": "Testing is required in programming tasks.",
            },
        },
        {
            "question_text": f"When a program for {topic_l} fails, what should you check first?",
            "skill": "debugging_order",
            "answers": {
                "A": "Whether each step is in the correct order",
                "B": "Whether the robot colour changed",
                "C": "Whether the classroom door is open",
                "D": "Whether the date is a weekend",
            },
            "explanations": {
                "A": "Sequence errors are a common cause of wrong outputs.",
                "B": "Robot colour is unrelated to program logic.",
                "C": "The door does not change program logic.",
                "D": "The day of the week does not fix code order.",
            },
        },
    ]


def _life_skills_templates(topic: str, sequence: int, *, grade: int = 7) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    if grade <= 6:
        return [
            {
                "question_text": "Which choice is wise in class?",
                "skill": "responsible_behaviour",
                "answers": {
                    "A": "Listen, follow safety rules and ask for help when unsure",
                    "B": "Ignore instructions and work alone without checking",
                    "C": "Copy another learner without understanding",
                    "D": "Leave the activity before it is completed",
                },
                "explanations": {
                    "A": "Responsible learners follow rules and seek help.",
                    "B": "Ignoring instructions is unsafe.",
                    "C": "Copying without understanding hides misconceptions.",
                    "D": "Leaving early stops learning.",
                },
            },
            {
                "question_text": "Which question helps you think back?",
                "skill": "reflection",
                "answers": {
                    "A": "What did I learn and how can I use it at home or school?",
                    "B": "How can I avoid the task completely?",
                    "C": "Who can I blame if the task is difficult?",
                    "D": "Why should I skip checking my work?",
                },
                "explanations": {
                    "A": "Reflection links learning to real use.",
                    "B": "Avoiding the task stops progress.",
                    "C": "Blame does not improve learning.",
                    "D": "Checking work is essential.",
                },
            },
            {
                "question_text": "Which task helps you learn more?",
                "skill": "extension",
                "answers": {
                    "A": "Create a new example and teach the method to a partner",
                    "B": "Repeat the same answer without thinking",
                    "C": "Skip the vocabulary for the topic",
                    "D": "Ignore feedback from the teacher",
                },
                "explanations": {
                    "A": "Teaching a new example shows deeper understanding.",
                    "B": "Repeating without thinking is not extension.",
                    "C": "Vocabulary supports understanding.",
                    "D": "Feedback helps improvement.",
                },
            },
        ]
    return [
        {
            "question_text": f"Which choice shows a responsible action during a lesson on {topic_l}?",
            "skill": "responsible_behaviour",
            "answers": {
                "A": "Listen, follow safety rules and ask for help when unsure",
                "B": "Ignore instructions and work alone without checking",
                "C": "Copy another learner without understanding",
                "D": "Leave the activity before it is completed",
            },
            "explanations": {
                "A": "Responsible learners follow rules and seek help.",
                "B": "Ignoring instructions is unsafe.",
                "C": "Copying without understanding hides misconceptions.",
                "D": "Leaving early stops learning.",
            },
        },
        {
            "question_text": f"Which question helps a learner reflect on {topic_l}?",
            "skill": "reflection",
            "answers": {
                "A": "What did I learn and how can I use it at home or school?",
                "B": "How can I avoid the task completely?",
                "C": "Who can I blame if the task is difficult?",
                "D": "Why should I skip checking my work?",
            },
            "explanations": {
                "A": "Reflection links learning to real use.",
                "B": "Avoiding the task stops progress.",
                "C": "Blame does not improve learning.",
                "D": "Checking work is essential.",
            },
        },
        {
            "question_text": f"Which extension task best deepens understanding of {topic_l}?",
            "skill": "extension",
            "answers": {
                "A": "Create a new example and teach the method to a partner",
                "B": "Repeat the same answer without thinking",
                "C": "Skip the vocabulary for the topic",
                "D": "Ignore feedback from the teacher",
            },
            "explanations": {
                "A": "Teaching a new example shows deeper understanding.",
                "B": "Repeating without thinking is not extension.",
                "C": "Vocabulary supports understanding.",
                "D": "Feedback helps improvement.",
            },
        },
    ]


def _life_skills_extended_templates(topic: str, sequence: int, *, grade: int = 7) -> list[dict[str, Any]]:
    topic_l = topic.lower()
    if grade <= 6:
        return [
            {
                "question_text": "Which habit helps you learn well?",
                "skill": "healthy_habits",
                "answers": {
                    "A": "Rest, hydrate and ask questions when confused",
                    "B": "Skip meals to finish faster",
                    "C": "Hide mistakes from the teacher",
                    "D": "Avoid talking about the topic",
                },
                "explanations": {
                    "A": "Healthy habits help concentration and wellbeing.",
                    "B": "Skipping meals reduces energy for learning.",
                    "C": "Mistakes are part of learning.",
                    "D": "Discussion clarifies ideas.",
                },
            },
            {
                "question_text": "How can you show respect in class?",
                "skill": "respect",
                "answers": {
                    "A": "Listen to others and take turns",
                    "B": "Interrupt whenever they want",
                    "C": "Mock a partner's answer",
                    "D": "Refuse to work in a group",
                },
                "explanations": {
                    "A": "Respect includes listening and fair participation.",
                    "B": "Interrupting stops others from learning.",
                    "C": "Mocking harms the learning environment.",
                    "D": "Group work often supports understanding.",
                },
            },
        ]
    return [
        {
            "question_text": f"Which habit supports healthy learning about {topic_l}?",
            "skill": "healthy_habits",
            "answers": {
                "A": "Rest, hydrate and ask questions when confused",
                "B": "Skip meals to finish faster",
                "C": "Hide mistakes from the teacher",
                "D": "Avoid talking about the topic",
            },
            "explanations": {
                "A": "Healthy habits help concentration and wellbeing.",
                "B": "Skipping meals reduces energy for learning.",
                "C": "Mistakes are part of learning.",
                "D": "Discussion clarifies ideas.",
            },
        },
        {
            "question_text": f"How can a learner show respect during work on {topic_l}?",
            "skill": "respect",
            "answers": {
                "A": "Listen to others and take turns",
                "B": "Interrupt whenever they want",
                "C": "Mock a partner's answer",
                "D": "Refuse to work in a group",
            },
            "explanations": {
                "A": "Respect includes listening and fair participation.",
                "B": "Interrupting stops others from learning.",
                "C": "Mocking harms the learning environment.",
                "D": "Group work often supports understanding.",
            },
        },
    ]
