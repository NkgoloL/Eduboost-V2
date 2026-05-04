-- EduBoost SA — Phase 2 Seed Data
-- Run: docker exec -i eduboost-postgres psql -U eduboost_user -d eduboost < scripts/db_seed_phase2.sql

BEGIN;

-- ============================================================================
-- LESSONS (CAPS-Aligned for Grade R-7)
-- ============================================================================

-- Grade R-3 Lessons
INSERT INTO lessons (lesson_id, title, subject_code, grade_level, unit, topic, content, content_modality, duration_minutes, difficulty_level, learning_objectives, is_cap_aligned) VALUES
-- Mathematics Grade R
('MATH-R-001', 'Counting 1-10', 'MATH', 0, 'Numbers', 'Counting', 'Learn to count from 1 to 10 using pictures of apples, cats, and balls.', 'interactive', 15, 0.2, '["count objects to 10", "recognize numbers 1-10"]', TRUE),
('MATH-R-002', 'Shapes Around Us', 'MATH', 0, 'Space & Shape', '2D Shapes', 'Discover circles, squares, and triangles in everyday objects.', 'interactive', 15, 0.2, '["identify basic shapes", "match shapes to objects"]', TRUE),
('MATH-1-001', 'Addition Basics', 'MATH', 1, 'Numbers', 'Addition', 'Learn to add numbers up to 20 using visual aids and number lines.', 'interactive', 20, 0.4, '["add numbers within 20", "use number line for addition"]', TRUE),
('MATH-1-002', 'Subtraction Fun', 'MATH', 1, 'Numbers', 'Subtraction', 'Learn to subtract numbers within 20 using pictures.', 'interactive', 20, 0.4, '["subtract numbers within 20", "solve word problems"]', TRUE),
('MATH-2-001', 'Skip Counting', 'MATH', 2, 'Numbers', 'Patterns', 'Learn to skip count by 2s, 5s, and 10s.', 'interactive', 20, 0.5, '["skip count by 2, 5, 10", "recognize number patterns"]', TRUE),
('MATH-2-002', 'Money Matters', 'MATH', 2, 'Measurement', 'Money', 'Learn South African coin values and making change.', 'interactive', 25, 0.5, '["recognize SA coins", "count money amounts"]', TRUE),
('MATH-3-001', 'Introduction to Fractions', 'MATH', 3, 'Numbers', 'Fractions', 'Learn about halves, thirds, and quarters.', 'interactive', 25, 0.6, '["identify fractions", "split shapes into equal parts"]', TRUE),
('MATH-3-002', 'Time Telling', 'MATH', 3, 'Measurement', 'Time', 'Learn to read analog and digital clocks.', 'interactive', 25, 0.6, '["tell time to hour/half hour", "read digital clock"]', TRUE),

-- English Grade R-3
('ENG-R-001', 'My First Words', 'ENG', 0, 'Literacy', 'Vocabulary', 'Learn basic English words with pictures.', 'text', 15, 0.2, '["recognize common objects", "build vocabulary"]', TRUE),
('ENG-R-002', 'Alphabet Fun', 'ENG', 0, 'Phonics', 'Alphabet', 'Learn the letters of the alphabet with sounds.', 'interactive', 15, 0.2, '["name alphabet letters", "hear letter sounds"]', TRUE),
('ENG-1-001', 'Simple Sentences', 'ENG', 1, 'Grammar', 'Sentences', 'Learn to form simple sentences.', 'text', 20, 0.4, '["form simple sentences", "use capital letters"]', TRUE),
('ENG-1-002', 'Reading Stories', 'ENG', 1, 'Reading', 'Comprehension', 'Read short stories and answer questions.', 'text', 20, 0.4, '["read short text", "answer comprehension questions"]', TRUE),
('ENG-2-001', 'Nouns and Verbs', 'ENG', 2, 'Grammar', 'Parts of Speech', 'Learn about nouns and action words.', 'text', 20, 0.5, '["identify nouns", "identify verbs"]', TRUE),
('ENG-2-002', 'Writing Paragraphs', 'ENG', 2, 'Writing', 'Composition', 'Learn to write simple paragraphs.', 'text', 25, 0.5, '["write simple paragraph", "use proper spacing"]', TRUE),
('ENG-3-001', 'Punctuation Rules', 'ENG', 3, 'Grammar', 'Punctuation', 'Learn to use full stops, commas, and question marks.', 'text', 25, 0.6, '["use punctuation correctly", "improve writing"]', TRUE),
('ENG-3-002', 'Story Writing', 'ENG', 3, 'Writing', 'Creative Writing', 'Write your own short story.', 'text', 30, 0.6, '["write creative story", "use descriptive words"]', TRUE),

-- Life Skills Grade R-3
('LIFE-R-001', 'My Body', 'LIFE', 0, 'Health', 'Body Parts', 'Learn about different parts of the body.', 'interactive', 15, 0.2, '["name body parts", "understand basic hygiene"]', TRUE),
('LIFE-R-002', 'My Family', 'LIFE', 0, 'Social', 'Relationships', 'Learn about family members and roles.', 'text', 15, 0.2, '["identify family members", "understand family roles"]', TRUE),
('LIFE-1-001', 'Healthy Eating', 'LIFE', 1, 'Health', 'Nutrition', 'Learn about healthy food choices.', 'interactive', 20, 0.4, '["identify food groups", "make healthy choices"]', TRUE),
('LIFE-1-002', 'Safety Rules', 'LIFE', 1, 'Safety', 'Personal Safety', 'Learn important safety rules at home and school.', 'text', 20, 0.4, '["follow safety rules", "identify dangers"]', TRUE),
('LIFE-2-001', 'Emotions', 'LIFE', 2, 'Social', 'Emotional Health', 'Learn to identify and express feelings.', 'text', 20, 0.5, '["name different emotions", "express feelings appropriately"]', TRUE),
('LIFE-2-002', 'Community Helpers', 'LIFE', 2, 'Social', 'Community', 'Learn about people who help our community.', 'text', 20, 0.5, '["identify community helpers", "understand their roles"]', TRUE),
('LIFE-3-001', 'Bullying Prevention', 'LIFE', 3, 'Social', 'Wellbeing', 'Learn about bullying and how to prevent it.', 'text', 25, 0.6, '["recognize bullying", "seek help when needed"]', TRUE),
('LIFE-3-002', 'Environmental Care', 'LIFE', 3, 'Environmental', 'Sustainability', 'Learn how to care for our environment.', 'interactive', 25, 0.6, '["understand recycling", "care for environment"]', TRUE),

-- Natural Sciences Grade 4-7
('NS-4-001', 'States of Matter', 'NS', 4, 'Matter', 'Solids Liquids Gases', 'Learn about solids, liquids, and gases.', 'interactive', 30, 0.6, '["identify states of matter", "understand properties"]', TRUE),
('NS-4-002', 'The Solar System', 'NS', 4, 'Space', 'Earth and Beyond', 'Explore the planets in our solar system.', 'interactive', 30, 0.6, '["name planets", "understand solar system"]', TRUE),
('NS-5-001', 'Life Cycles', 'NS', 5, 'Life', 'Living Things', 'Learn about life cycles of plants and animals.', 'interactive', 30, 0.7, '["describe life cycles", "compare different organisms"]', TRUE),
('NS-5-002', 'Forces and Motion', 'NS', 5, 'Physics', 'Forces', 'Learn about push, pull, and friction.', 'interactive', 30, 0.7, '["identify forces", "understand motion"]', TRUE),
('NS-6-001', 'Ecosystems', 'NS', 6, 'Environment', 'Ecology', 'Learn about food chains and ecosystems.', 'interactive', 35, 0.7, '["understand food chains", "identify ecosystem components"]', TRUE),
('NS-6-002', 'Electricity', 'NS', 6, 'Physics', 'Energy', 'Learn about electric circuits and safety.', 'interactive', 35, 0.7, '["understand circuits", "apply electricity safety"]', TRUE),
('NS-7-001', 'Chemical Reactions', 'NS', 7, 'Chemistry', 'Matter', 'Learn about chemical changes and reactions.', 'interactive', 35, 0.8, '["identify chemical reactions", "understand changes"]', TRUE),
('NS-7-002', 'Evolution', 'NS', 7, 'Life', 'Change Over Time', 'Learn how living things change over time.', 'text', 35, 0.8, '["understand evolution", "explain adaptation"]', TRUE),

-- Social Sciences Grade 4-7
('SS-4-001', 'Map Skills', 'SS', 4, 'Geography', 'Maps', 'Learn to read maps and use directions.', 'interactive', 25, 0.6, '["read simple maps", "use compass directions"]', TRUE),
('SS-4-002', 'Our Community', 'SS', 4, 'Geography', 'Settlement', 'Learn about different types of communities.', 'text', 25, 0.6, '["identify community types", "understand settlement"]', TRUE),
('SS-5-001', 'Ancient Egypt', 'SS', 5, 'History', 'Ancient Civilizations', 'Learn about Ancient Egyptian civilization.', 'text', 30, 0.7, '["describe Egyptian civilization", "understand pyramids"]', TRUE),
('SS-5-002', 'South African Heritage', 'SS', 5, 'History', 'Culture', 'Learn about South African cultural heritage.', 'text', 30, 0.7, '["identify cultural groups", "understand heritage"]', TRUE),
('SS-6-001', 'Climate Zones', 'SS', 6, 'Geography', 'Climate', 'Learn about different climate zones around the world.', 'interactive', 30, 0.7, '["identify climate zones", "understand weather patterns"]', TRUE),
('SS-6-002', 'Democracy in SA', 'SS', 6, 'History', 'Government', 'Learn about South African democracy.', 'text', 30, 0.7, '["understand democracy", "know SA government"]', TRUE),
('SS-7-001', 'Industrial Revolution', 'SS', 7, 'History', 'Change', 'Learn about the Industrial Revolution.', 'text', 35, 0.8, '["describe industrialization", "understand impact"]', TRUE),
('SS-7-002', 'Global Trade', 'SS', 7, 'Geography', 'Economics', 'Learn about international trade and resources.', 'text', 35, 0.8, '["understand trade", "identify resources"]', TRUE)
ON CONFLICT (lesson_id) DO NOTHING;

-- ============================================================================
-- ASSESSMENTS
-- ============================================================================

INSERT INTO assessments (title, subject_code, grade_level, assessment_type, total_marks, time_limit_minutes, passing_score, questions, is_active) VALUES
-- Grade 1 Math Assessment
('Grade 1 Math Quiz', 'MATH', 1, 'quiz', 10, 15, 0.6, '[
  {"question_id": "q1", "type": "multiple_choice", "question": "What is 2 + 3?", "options": ["4", "5", "6", "7"], "correct_answer": "5", "marks": 1},
  {"question_id": "q2", "type": "multiple_choice", "question": "What shape is a ball?", "options": ["square", "circle", "triangle", "rectangle"], "correct_answer": "circle", "marks": 1},
  {"question_id": "q3", "type": "number_input", "question": "Count the apples: 🍎🍎🍎", "correct_answer": "3", "marks": 1},
  {"question_id": "q4", "type": "multiple_choice", "question": "What is 5 - 2?", "options": ["2", "3", "4", "5"], "correct_answer": "3", "marks": 1},
  {"question_id": "q5", "type": "multiple_choice", "question": "Which number is bigger: 7 or 4?", "options": ["7", "4", "they are equal"], "correct_answer": "7", "marks": 1},
  {"question_id": "q6", "type": "multiple_choice", "question": "What comes after 8?", "options": ["6", "7", "9", "10"], "correct_answer": "9", "marks": 1},
  {"question_id": "q7", "type": "multiple_choice", "question": "How many sides does a triangle have?", "options": ["2", "3", "4", "5"], "correct_answer": "3", "marks": 1},
  {"question_id": "q8", "type": "number_input", "question": "What is 1 + 4?", "correct_answer": "5", "marks": 1},
  {"question_id": "q9", "type": "multiple_choice", "question": "Which is a fruit?", "options": ["car", "apple", "chair", "book"], "correct_answer": "apple", "marks": 1},
  {"question_id": "q10", "type": "multiple_choice", "question": "What is 10 - 1?", "options": ["8", "9", "10", "11"], "correct_answer": "9", "marks": 1}
]'::jsonb, TRUE),

-- Grade 3 Math Assessment
('Grade 3 Math Test', 'MATH', 3, 'test', 20, 30, 0.6, '[
  {"question_id": "q1", "type": "number_input", "question": "What is 125 + 73?", "correct_answer": "198", "marks": 2},
  {"question_id": "q2", "type": "number_input", "question": "What is 200 - 87?", "correct_answer": "113", "marks": 2},
  {"question_id": "q3", "type": "multiple_choice", "question": "What is 1/2 + 1/2?", "options": ["1/4", "1", "2", "1/2"], "correct_answer": "1", "marks": 2},
  {"question_id": "q4", "type": "multiple_choice", "question": "Which fraction is bigger: 1/3 or 1/2?", "options": ["1/3", "1/2", "they are equal"], "correct_answer": "1/2", "marks": 2},
  {"question_id": "q5", "type": "number_input", "question": "What is 12 x 3?", "correct_answer": "36", "marks": 2},
  {"question_id": "q6", "type": "multiple_choice", "question": "How many minutes in 2 hours?", "options": ["60", "100", "120", "200"], "correct_answer": "120", "marks": 2},
  {"question_id": "q7", "type": "number_input", "question": "What is 45 ÷ 5?", "correct_answer": "9", "marks": 2},
  {"question_id": "q8", "type": "multiple_choice", "question": "What is the value of the 5 in 523?", "options": ["5", "50", "500", "5"], "correct_answer": "500", "marks": 2},
  {"question_id": "q9", "type": "multiple_choice", "question": "Which shape has 4 equal sides?", "options": ["rectangle", "triangle", "square", "circle"], "correct_answer": "square", "marks": 2},
  {"question_id": "q10", "type": "number_input", "question": "What is 7 x 8?", "correct_answer": "56", "marks": 2}
]'::jsonb, TRUE),

-- Grade 5 English Assessment
('Grade 5 English Test', 'ENG', 5, 'test', 20, 30, 0.6, '[
  {"question_id": "q1", "type": "multiple_choice", "question": "Which word is a noun?", "options": ["run", "happy", "school", "quickly"], "correct_answer": "school", "marks": 2},
  {"question_id": "q2", "type": "multiple_choice", "question": "Which word is a verb?", "options": ["beautiful", "jump", "blue", "tall"], "correct_answer": "jump", "marks": 2},
  {"question_id": "q3", "type": "multiple_choice", "question": "Choose the correct spelling:", "options": ["recieve", "receive", "receeve", "receve"], "correct_answer": "receive", "marks": 2},
  {"question_id": "q4", "type": "text_input", "question": "Write the past tense of: walk", "correct_answer": "walked", "marks": 2},
  {"question_id": "q5", "type": "multiple_choice", "question": "Which is a compound sentence?", "options": ["The cat slept.", "The dog barked and the cat ran.", "The happy child.", "Running fast."], "correct_answer": "The dog barked and the cat ran.", "marks": 2},
  {"question_id": "q6", "type": "multiple_choice", "question": "What type of noun is Ubuntu?", "options": ["common noun", "proper noun", "collective noun", "abstract noun"], "correct_answer": "proper noun", "marks": 2},
  {"question_id": "q7", "type": "text_input", "question": "Write the plural of: child", "correct_answer": "children", "marks": 2},
  {"question_id": "q8", "type": "multiple_choice", "question": "Which sentence uses a metaphor?", "options": ["The sun is like a ball.", "The sun is a bright star in the sky.", "The sun shines brightly.", "The sun is a fireball."], "correct_answer": "The sun is a fireball.", "marks": 2},
  {"question_id": "q9", "type": "multiple_choice", "question": "Choose the antonym of ancient:", "options": ["old", "new", "historic", "antique"], "correct_answer": "new", "marks": 2},
  {"question_id": "q10", "type": "text_input", "question": "Write the comparative form of: happy", "correct_answer": "happier", "marks": 2}
]'::jsonb, TRUE),

-- Grade 4 Natural Sciences Assessment
('Grade 4 NS Quiz', 'NS', 4, 'quiz', 10, 15, 0.6, '[
  {"question_id": "q1", "type": "multiple_choice", "question": "Which state of matter has a fixed shape?", "options": ["solid", "liquid", "gas", "plasma"], "correct_answer": "solid", "marks": 1},
  {"question_id": "q2", "type": "multiple_choice", "question": "Water freezes at what temperature?", "options": ["0°C", "100°C", "32°C", "50°C"], "correct_answer": "0°C", "marks": 1},
  {"question_id": "q3", "type": "multiple_choice", "question": "Which planet is closest to the sun?", "options": ["Venus", "Mars", "Mercury", "Jupiter"], "correct_answer": "Mercury", "marks": 1},
  {"question_id": "q4", "type": "multiple_choice", "question": "What do plants need to make food?", "options": ["sunlight", "rocks", "metal", "sand"], "correct_answer": "sunlight", "marks": 1},
  {"question_id": "q5", "type": "multiple_choice", "question": "Which is NOT a type of rock?", "options": ["igneous", "sedimentary", "metamorphic", "water"], "correct_answer": "water", "marks": 1},
  {"question_id": "q6", "type": "multiple_choice", "question": "What is the largest planet?", "options": ["Saturn", "Jupiter", "Neptune", "Uranus"], "correct_answer": "Jupiter", "marks": 1},
  {"question_id": "q7", "type": "multiple_choice", "question": "What gas do plants release?", "options": ["oxygen", "carbon dioxide", "nitrogen", "hydrogen"], "correct_answer": "oxygen", "marks": 1},
  {"question_id": "q8", "type": "multiple_choice", "question": "Which organ pumps blood?", "options": ["lungs", "heart", "brain", "stomach"], "correct_answer": "heart", "marks": 1},
  {"question_id": "q9", "type": "multiple_choice", "question": "What is the sun?", "options": ["a planet", "a star", "a moon", "an asteroid"], "correct_answer": "a star", "marks": 1},
  {"question_id": "q10", "type": "multiple_choice", "question": "Which animal is a mammal?", "options": ["fish", "snake", "dog", "chicken"], "correct_answer": "dog", "marks": 1}
]'::jsonb, TRUE);

-- ============================================================================
-- BADGES
-- ============================================================================

INSERT INTO badges (badge_key, name, description, xp_value, grade_band, badge_type, threshold, is_active) VALUES
-- Streak Badges (R-3)
('streak_3', '3-Day Streak', 'Complete activities 3 days in a row', 25, 'R-3', 'streak', 3, TRUE),
('streak_7', 'Week Warrior', 'Complete activities 7 days in a row', 50, 'R-3', 'streak', 7, TRUE),
('streak_14', 'Fortnight Fighter', 'Complete activities 14 days in a row', 100, 'R-3', 'streak', 14, TRUE),
('streak_30', 'Monthly Master', 'Complete activities 30 days in a row', 250, 'R-3', 'streak', 30, TRUE),

-- Mastery Badges (All grades)
('mastery_math', 'Math Whiz', 'Achieve 80% mastery in Mathematics', 75, 'ALL', 'mastery', 80, TRUE),
('mastery_eng', 'Word Wizard', 'Achieve 80% mastery in English', 75, 'ALL', 'mastery', 80, TRUE),
('mastery_science', 'Science Star', 'Achieve 80% mastery in Natural Sciences', 75, 'ALL', 'mastery', 80, TRUE),
('mastery_all', 'All-Round Scholar', 'Achieve 80% mastery in all subjects', 200, 'ALL', 'mastery', 80, TRUE),

-- Discovery Badges (4-7)
('discovery_math', 'Math Explorer', 'Complete 5 advanced math challenges', 50, '4-7', 'discovery', 5, TRUE),
('discovery_science', 'Science Seeker', 'Complete 5 science experiments', 50, '4-7', 'discovery', 5, TRUE),
('discovery_english', 'Language Explorer', 'Read 5 complex texts', 50, '4-7', 'discovery', 5, TRUE),

-- Milestone Badges (All grades)
('first_lesson', 'First Steps', 'Complete your first lesson', 10, 'ALL', 'milestone', 1, TRUE),
('lessons_10', 'Dedicated Learner', 'Complete 10 lessons', 50, 'ALL', 'milestone', 10, TRUE),
('lessons_50', 'Knowledge Seeker', 'Complete 50 lessons', 150, 'ALL', 'milestone', 50, TRUE),
('lessons_100', 'Century Club', 'Complete 100 lessons', 300, 'ALL', 'milestone', 100, TRUE),

-- Achievement Badges (All grades)
('perfect_score', 'Perfect Score', 'Get 100% on any assessment', 100, 'ALL', 'achievement', 100, TRUE),
('speed_demon', 'Speed Demon', 'Complete an assessment in under 5 minutes', 50, 'ALL', 'achievement', 1, TRUE),
('comeback_kid', 'Comeback Kid', 'Improve score by 20% on retry', 75, 'ALL', 'achievement', 20, TRUE),
('early_bird', 'Early Bird', 'Complete activities 5 days before deadline', 50, 'ALL', 'achievement', 5, TRUE),

-- Level Badges (All grades)
('level_5', 'Rising Star', 'Reach Level 5', 100, 'ALL', 'milestone', 5, TRUE),
('level_10', 'Super Star', 'Reach Level 10', 250, 'ALL', 'milestone', 10, TRUE),
('level_20', 'Legend', 'Reach Level 20', 500, 'ALL', 'milestone', 20, TRUE);

-- ============================================================================
-- ITEM BANK (IRT Diagnostic Items)
-- ============================================================================

INSERT INTO item_bank (item_id, subject_code, grade_level, concept_code, difficulty, discrimination, guessing, content, options, correct_answer, is_active) VALUES
-- Grade 1 Math Items
('item-m1-001', 'MATH', 1, 'GR1_ADD', 0.3, 1.2, 0.25, 'What is 2 + 3?', '["3", "4", "5", "6"]', '5', TRUE),
('item-m1-002', 'MATH', 1, 'GR1_ADD', 0.4, 1.1, 0.25, 'What is 4 + 5?', '["7", "8", "9", "10"]', '9', TRUE),
('item-m1-003', 'MATH', 1, 'GR1_SUB', 0.35, 1.2, 0.25, 'What is 5 - 2?', '["2", "3", "4", "5"]', '3', TRUE),
('item-m1-004', 'MATH', 1, 'GR1_CNT', 0.2, 1.3, 0.25, 'How many apples? 🍎🍎🍎🍎', '["3", "4", "5", "6"]', '4', TRUE),
('item-m1-005', 'MATH', 1, 'GR1_SHAPE', 0.4, 1.0, 0.25, 'Which shape is a circle?', '["square", "triangle", "circle", "rectangle"]', 'circle', TRUE),

-- Grade 3 Math Items
('item-m3-001', 'MATH', 3, 'GR3_ADD', 0.5, 1.2, 0.25, 'What is 125 + 73?', '["195", "197", "198", "199"]', '198', TRUE),
('item-m3-002', 'MATH', 3, 'GR3_SUB', 0.55, 1.1, 0.25, 'What is 200 - 87?', '["113", "123", "133", "143"]', '113', TRUE),
('item-m3-003', 'MATH', 3, 'GR3_MUL', 0.6, 1.2, 0.25, 'What is 12 x 3?', '["33", "34", "35", "36"]', '36', TRUE),
('item-m3-004', 'MATH', 3, 'GR3_FRAC', 0.5, 1.0, 0.25, 'What is 1/2 + 1/2?', '["1/4", "1", "2", "1/2"]', '1', TRUE),
('item-m3-005', 'MATH', 3, 'GR3_DIV', 0.6, 1.1, 0.25, 'What is 45 ÷ 5?', '["7", "8", "9", "10"]', '9', TRUE),

-- Grade 4 Math Items
('item-m4-001', 'MATH', 4, 'GR4_ADD', 0.6, 1.2, 0.25, 'What is 234 + 567?', '["791", "801", "811", "821"]', '801', TRUE),
('item-m4-002', 'MATH', 4, 'GR4_MUL', 0.65, 1.1, 0.25, 'What is 15 x 12?', '["165", "170", "175", "180"]', '180', TRUE),
('item-m4-003', 'MATH', 4, 'GR4_FRAC', 0.6, 1.0, 0.25, 'Which fraction is bigger: 2/3 or 3/4?', '["2/3", "3/4", "they are equal"]', '3/4', TRUE),
('item-m4-004', 'MATH', 4, 'GR4_PATT', 0.55, 1.2, 0.25, 'What comes next: 2, 4, 6, 8, ?', '["9", "10", "11", "12"]', '10', TRUE),
('item-m4-005', 'MATH', 4, 'GR4_DATA', 0.5, 1.1, 0.25, 'In a pictograph, each picture = 5 votes. 4 pictures = ?', '["9", "20", "25", "30"]', '20', TRUE),

-- Grade 5 Math Items
('item-m5-001', 'MATH', 5, 'GR5_DEC', 0.7, 1.2, 0.25, 'What is 3.5 + 2.8?', '["5.3", "6.3", "7.3", "8.3"]', '6.3', TRUE),
('item-m5-002', 'MATH', 5, 'GR5_MUL', 0.7, 1.1, 0.25, 'What is 123 x 4?', '["482", "492", "502", "512"]', '492', TRUE),
('item-m5-003', 'MATH', 5, 'GR5_DIV', 0.75, 1.0, 0.25, 'What is 156 ÷ 12?', '["11", "12", "13", "14"]', '13', TRUE),
('item-m5-004', 'MATH', 5, 'GR5_PCT', 0.7, 1.1, 0.25, 'What is 20% of 50?', '["5", "10", "15", "20"]', '10', TRUE),
('item-m5-005', 'MATH', 5, 'GR5_ANG', 0.65, 1.2, 0.25, 'How many degrees in a triangle?', '["90", "180", "270", "360"]', '180', TRUE),

-- Grade 1 English Items
('item-e1-001', 'ENG', 1, 'GR1_VOC', 0.3, 1.2, 0.25, 'Which is a fruit?', '["car", "apple", "chair", "book"]', 'apple', TRUE),
('item-e1-002', 'ENG', 1, 'GR1_CMP', 0.35, 1.1, 0.25, 'Which sentence is correct?', '["The cat run.", "The cat runs.", "The cat running.", "Cats run."]', 'The cat runs.', TRUE),
('item-e1-003', 'ENG', 1, 'GR1_SPK', 0.3, 1.3, 0.25, 'What sound does a cat make?', '["woof", "meow", "moo", "quack"]', 'meow', TRUE),

-- Grade 3 English Items
('item-e3-001', 'ENG', 3, 'GR3_NOUN', 0.5, 1.2, 0.25, 'Which word is a noun?', '["run", "happy", "school", "quickly"]', 'school', TRUE),
('item-e3-002', 'ENG', 3, 'GR3_VERB', 0.5, 1.1, 0.25, 'Which word is a verb?', '["beautiful", "jump", "blue", "tall"]', 'jump', TRUE),
('item-e3-003', 'ENG', 3, 'GR3_SPEL', 0.55, 1.0, 0.25, 'Choose the correct spelling:', '["recieve", "receive", "receeve", "receve"]', 'receive', TRUE),
('item-e3-004', 'ENG', 3, 'GR3_PUNC', 0.5, 1.2, 0.25, 'Which needs a question mark?', '["The sky is blue.", "What time is it?", "She is nice.", "I like apples."]', 'What time is it?', TRUE),

-- Grade 4 NS Items
('item-n4-001', 'NS', 4, 'GR4_MATTER', 0.5, 1.2, 0.25, 'Which state of matter has fixed shape?', '["solid", "liquid", "gas", "plasma"]', 'solid', TRUE),
('item-n4-002', 'NS', 4, 'GR4_SPACE', 0.55, 1.1, 0.25, 'Which planet is closest to the sun?', '["Venus", "Mars", "Mercury", "Jupiter"]', 'Mercury', TRUE),
('item-n4-003', 'NS', 4, 'GR4_LIVING', 0.5, 1.3, 0.25, 'What do plants need to make food?', '["sunlight", "rocks", "metal", "sand"]', 'sunlight', TRUE),
('item-n4-004', 'NS', 4, 'GR4_ROCKS', 0.5, 1.0, 0.25, 'Which is NOT a type of rock?', '["igneous", "sedimentary", "metamorphic", "water"]', 'water', TRUE),

-- Grade 5 NS Items
('item-n5-001', 'NS', 5, 'GR5_LIFECYCLE', 0.6, 1.2, 0.25, 'What is the first stage of a butterfly?', '["egg", "caterpillar", "pupa", "adult"]', 'egg', TRUE),
('item-n5-002', 'NS', 5, 'GR5_FORCE', 0.65, 1.1, 0.25, 'What force slows down a moving ball?', '["gravity", "magnetism", "friction", "electricity"]', 'friction', TRUE),
('item-n5-003', 'NS', 5, 'GR5_WATER', 0.6, 1.0, 0.25, 'What is the process of water becoming vapor?', '["evaporation", "condensation", "precipitation", "freezing"]', 'evaporation', TRUE)
ON CONFLICT (item_id) DO NOTHING;

-- ============================================================================
-- REPORTS (Sample)
-- ============================================================================

INSERT INTO reports (learner_id, report_type, title, content, summary, generated_by, is_shared) VALUES
('00000000-0000-0000-0000-000000000001', 'progress', 'Weekly Progress Report', 
 '{"week_of": "2026-04-21", "lessons_completed": 5, "time_spent_minutes": 120, "subjects_covered": ["Math", "English", "Life Skills"], "highlights": ["Improved fractions understanding", "Completed 3 English lessons"], "areas_for_improvement": ["Needs more practice with time telling"]}'::jsonb,
 'Completed 5 lessons this week. Strong progress in English.',
 'SYSTEM', FALSE),

('00000000-0000-0000-0000-000000000002', 'diagnostic', 'Mathematics Diagnostic Report',
 '{"subject": "Math", "grade_level": 5, "theta_estimate": 0.5, "standard_error": 0.12, "items_administered": 20, "mastery_score": 0.72, "knowledge_gaps": [{"concept": "GR5_DEC", "gap_grade": 4, "severity": 0.45}], "recommendations": ["Review decimal operations", "Practice percentage calculations"]}'::jsonb,
 'Math diagnostic complete. Recommended: decimal operations practice.',
 'AI', FALSE),

('00000000-0000-0000-0000-000000000001', 'parent', 'Monthly Parent Report',
 '{"month": "April 2026", "total_lessons": 18, "total_time_hours": 6, "subject_breakdown": {"Math": {"lessons": 6, "mastery": 0.45}, "English": {"lessons": 6, "mastery": 0.62}, "Life Skills": {"lessons": 6, "mastery": 0.75}}, "streak_best": 7, "badges_earned": 2, "upcoming_focus": "Fractions and time telling"}'::jsonb,
 'Great progress this month! Focus areas: fractions and time.',
 'AI', FALSE);

COMMIT;