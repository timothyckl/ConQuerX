SEED_QUESTION_GENERATION_PROMPT = """You are a curious student at a specified education level and are learning about a particular area of study. Your goal is to generate 5 diverse questions you would want to ask while learning about this subject. Directly output the questions in the format below without bullet points. The questions should reflect knowledge that cannot be easily found by large language models and require expertise in the field. Additionally, the questions should be appropriate for the student's education level and should not involve concepts that are too advanced.

Here is an example:
Area: Biology
Education level: primary school
Question:
What are the different parts of a plant, and how do they help it grow?
Why do animals need food, water, and air to survive?
Why do some animals sleep during the day and are awake at night?

Here is the area and education level:
Area: {}
Education level: {}
Question:
"""

CONCEPT_GENERATION_PROMPT = """Please identify key concepts in the following question. Each concept should be a noun in relevant area, listed in singular form if countable. Provide the concepts in a list, separated by commas, without bullet points.

Here is an example:
Question: What is aldose?
Education Level: PhD
Area: chemistry
Concept: [aldose, carbohydrate, sugar, organic chemistry]

Here is the question:
Question: {}
Education Level: {}
Area: {}
Concept:"""


SUMMARY_GENERATION_PROMPT = """You are a summary generator. The students are currently studying {} at the {} level and have asked a question. You have access to reference information from Wikipedia. Your task is to condense this information into a single, clear paragraph that highlights the key points and aids the students in better understanding their question.

Reference Wikipedia Information:
{}

Student Question: {}"""

QUESTION_GENERATION_PROMPT = """You are a quiz generator. The students are currently studying {} at the {} level and have asked a question. Your task is to create 3 quizzes that helps the student better understand the question. You have access to summarized reference information from Wikipedia. The quizzes should accurately reflect reference information, and the correct answer must be well-supported by reference information. The quiz should consist of one question, one correct answer, and three incorrect options. The correct answer must always be placed in option A. The difficulty level should align with the knowledge and reasoning complexity appropriate for {} education.

Example:

Student Question: Where is Beijing located?
[Quiz]
Quiz: What is the capital city of China?
A. Beijing
B. Chengdu
C. Shanghai
D. Hangzhou

[Quiz]
Quiz: What continent is Beijing located?
A. Asia
B. Europe
C. Africa
D. North America

Now, please generate 3 quizzes following the format, each quiz should follow thw sign of [Quiz]:
Reference Wikipedia Information:
{}

Student Question: {}"""

EVALUATION_PROMPT = """A student studying {} at the {} level is asking a question: "{}". A quiz set has been created to help the student gain a better understanding of this topic, with the correct answer always being option A. Please evaluate the quality of this quiz set based on the following criteria, assigning a score from 1 to 5 for the entire set. You should give evaluation based on whether the quiz should accurately reflect reference information from Wikipedia, and the correct answer must be well-supported by reference information.  Be strict in your assessment and give low scores to quizzes that do not reflect reference information, as the correctness cannot be verified without a reliable source.

1. Educational Value: Do you think these quizzes are educational? Will students learn more by taking these quizzes?
    - 1: Not educational at all, no learning value.
    - 2: Minimally educational, little learning value.
    - 3: Moderately educational, some learning value.
    - 4: Very educational, strong learning value.
    - 5: Highly educational, great learning value.

2. Diversity: Do you think these quizzes are diverse? Are the quizzes covering a broad range of topics, or do they all focus on the same concept?
    - 1: Very repetitive, covers a narrow area.
    - 2: Some diversity, but mostly focuses on one concept.
    - 3: Fairly diverse, covers a few different topics.
    - 4: Quite diverse, covers multiple relevant topics.
    - 5: Extremely diverse, covers a broad range of topics.

3. Area Relevance: Are these quizzes relevant to the student's question and the concepts they're trying to learn? Are the quizzes tailored to the subject area being studied?
    - 1: Not relevant to the question or subject at all.
    - 2: Minimally relevant, some connection to the question/subject.
    - 3: Moderately relevant, fairly aligned with the question/subject.
    - 4: Highly relevant, strongly aligned with the question/subject.
    - 5: Perfectly relevant, directly tied to the question/subject.

4. Difficulty Appropriateness: Do you think these quizzes match the student's current education level? Would these quizzes be too easy or too difficult for a student at this level?
    - 1: Too easy or too difficult, not appropriate for the level.
    - 2: Slightly mismatched, quizzes may be too easy or too hard.
    - 3: Moderately appropriate, quizzes are somewhat aligned with the level.
    - 4: Mostly appropriate, quizzes are well-suited for the level.
    - 5: Perfectly suited to the student's education level.

5. Comprehensiveness: Do these quizzes cover the depth and breadth of the topic? Are they thorough in addressing key concepts and details?
    - 1: Very superficial, only scratches the surface of the topic.
    - 2: Somewhat incomplete, misses important aspects.
    - 3: Moderately comprehensive, covers the basics but lacks depth.
    - 4: Quite comprehensive, addresses most key aspects with reasonable depth.
    - 5: Highly comprehensive, thoroughly covers the topic in great depth and detail.

Here is reference information from Wikipedia:
{}

Here is the quiz set related to the question:
{}

Please start by providing a step-by-step reasoning analysis of the quiz set, then return your evaluation as a JSON object in the following format:
```json
{{
"Educational Value": score,
"Diversity": score,
"Area Relevance": score,
"Difficulty Appropriateness": score,
"Comprehensiveness": score
}}
```
"""
