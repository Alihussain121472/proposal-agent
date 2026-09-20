"""
Automated Test Suite for the Freelance Proposal Strategist Agent.
Tests red flag detection, rules linting, and strategic proposal generation across platforms.
"""

import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from proposal_agent import (
    ProposalStrategistAgent, ProposalInput, Platform, Tone,
    lint_proposal, analyze_red_flags
)
from presets import PRESETS

class TestProposalStrategist(unittest.TestCase):

    def setUp(self):
        self.agent = ProposalStrategistAgent()

    def test_red_flag_detection_spec_work(self):
        """Test detection of spec work and unpaid test requests."""
        job = "Need someone to build a scraper. Must show us what you'd do first and submit a free sample scraper."
        result = analyze_red_flags(job, "$50")
        self.assertTrue(result.has_flags)
        self.assertIsNotNone(result.alert_text)
        self.assertIn("Watch out", result.alert_text)
        # Verify 2 sentences max
        sentences = [s for s in result.alert_text.split(".") if s.strip()]
        self.assertLessEqual(len(sentences), 2)

    def test_red_flag_detection_clean_job(self):
        """Test clean job description with no red flags."""
        job = "Looking for a Next.js engineer to build an analytics dashboard with Supabase. Budget $4,000."
        result = analyze_red_flags(job, "$4000")
        self.assertFalse(result.has_flags)
        self.assertIsNone(result.alert_text)

    def test_rules_linter_forbidden_openers(self):
        """Test that linter catches 'I' or 'My name is' openers."""
        bad_proposal = "I am a senior full-stack developer with 8 years of experience. I can do this job."
        violations = lint_proposal(bad_proposal, Platform.UPWORK)
        self.assertTrue(any("opens with 'I'" in v for v in violations))

    def test_rules_linter_forbidden_buzzwords(self):
        """Test that linter catches forbidden buzzwords like 'passionate' and 'detail-oriented'."""
        bad_proposal = "Delivering this project requires great skill. I am passionate, hardworking, and detail-oriented."
        violations = lint_proposal(bad_proposal, Platform.UPWORK)
        self.assertTrue(any("passionate" in v for v in violations))
        self.assertTrue(any("detail-oriented" in v for v in violations))

    def test_upwork_proposal_generation(self):
        """Test Upwork proposal generation with offline engine."""
        preset = PRESETS["1"]["input"]
        res = self.agent.generate(preset, provider="offline")
        
        # Verify no red flags for preset 1
        self.assertIsNone(res.red_flag_alert)

        # Verify Variations exist
        self.assertTrue(len(res.variation_a.text) > 50)
        self.assertTrue(len(res.variation_b.text) > 50)

        # Verify Opener does not start with "I"
        first_word_a = res.variation_a.text.split()[0].lower()
        first_word_b = res.variation_b.text.split()[0].lower()
        self.assertNotIn(first_word_a, ["i", "my", "i'm"])
        self.assertNotIn(first_word_b, ["i", "my", "i'm"])

        # Verify different openers
        self.assertNotEqual(res.variation_a.text.splitlines()[0], res.variation_b.text.splitlines()[0])

        # Verify Coaching Note fields
        self.assertIn("Variation", res.coaching_note.stronger_variation)
        self.assertTrue(len(res.coaching_note.what_to_personalize) > 10)
        self.assertTrue(len(res.coaching_note.smart_question) > 10)
        self.assertTrue(len(res.coaching_note.win_probability_factors) > 20)

    def test_red_flag_preset_generates_alert_before_proposals(self):
        """Test that Preset 3 (with red flags) places the alert before the proposals."""
        preset = PRESETS["3"]["input"]
        res = self.agent.generate(preset, provider="offline")
        self.assertIsNotNone(res.red_flag_alert)
        self.assertIn("🚩 RED FLAG ALERT", res.raw_formatted)
        alert_idx = res.raw_formatted.find("RED FLAG ALERT")
        var_a_idx = res.raw_formatted.find("VARIATION A")
        self.assertLess(alert_idx, var_a_idx)

    def test_linkedin_length_calibration(self):
        """Test that LinkedIn proposals are calibrated for short length (100-150 words)."""
        preset = PRESETS["1"]["input"].model_copy(update={"platform": Platform.LINKEDIN})
        res = self.agent.generate(preset, provider="offline")
        # LinkedIn should be concise
        self.assertLess(res.variation_a.word_count, 175)
        self.assertLess(res.variation_b.word_count, 175)

    def test_academic_bachelors_education_generation(self):
        """Test Bachelor's level education proposal generation and verify 7 sections."""
        from presets import ACADEMIC_PRESETS
        from proposal_agent.models import AcademicLevel, AcademicProposalType
        preset = ACADEMIC_PRESETS["1"]["input"]
        res = self.agent.generate_academic(preset, provider="offline")

        self.assertEqual(res.academic_level, AcademicLevel.BACHELORS)
        self.assertEqual(res.proposal_type, AcademicProposalType.EDUCATION)
        # Verify 7 required sections
        self.assertTrue(len(res.title) > 10)
        self.assertTrue(len(res.introduction_background) > 50)
        self.assertTrue(len(res.problem_statement) > 40)
        self.assertGreaterEqual(len(res.objectives), 3)
        self.assertTrue(len(res.methodology_approach) > 50)
        self.assertTrue(len(res.expected_outcomes_benefits) > 50)
        self.assertTrue(len(res.conclusion) > 40)
        self.assertIn("Undergraduate", res.level_insights)

    def test_academic_masters_business_generation(self):
        """Test Master's level business proposal generation."""
        from presets import ACADEMIC_PRESETS
        from proposal_agent.models import AcademicLevel, AcademicProposalType
        preset = ACADEMIC_PRESETS["2"]["input"]
        res = self.agent.generate_academic(preset, provider="offline")

        self.assertEqual(res.academic_level, AcademicLevel.MASTERS)
        self.assertEqual(res.proposal_type, AcademicProposalType.BUSINESS)
        self.assertTrue(len(res.title) > 10)
        self.assertIn("Postgraduate", res.level_insights)
        self.assertGreater(res.word_count, 150)

    def test_academic_phd_social_media_generation(self):
        """Test PhD level social media proposal generation."""
        from presets import ACADEMIC_PRESETS
        from proposal_agent.models import AcademicLevel, AcademicProposalType
        preset = ACADEMIC_PRESETS["3"]["input"]
        res = self.agent.generate_academic(preset, provider="offline")

        self.assertEqual(res.academic_level, AcademicLevel.PHD)
        self.assertEqual(res.proposal_type, AcademicProposalType.SOCIAL_MEDIA)
        self.assertTrue("Epistemic" in res.title or "Algorithmic" in res.title)
        self.assertIn("Doctoral", res.level_insights)
        self.assertGreater(res.word_count, 200)

    def test_academic_depth_and_tone_calibration(self):
        """Test that Bachelor's and PhD generate distinct tones and complexity on the same topic."""
        from proposal_agent.models import AcademicLevel, AcademicProposalType, AcademicProposalInput
        topic = "Artificial Intelligence in University Student Advising"
        purpose = "Evaluate how automated AI bots impact academic advising efficiency and student retention."
        
        bachelor_inp = AcademicProposalInput(
            academic_level=AcademicLevel.BACHELORS,
            proposal_type=AcademicProposalType.EDUCATION,
            topic=topic,
            purpose=purpose
        )
        phd_inp = AcademicProposalInput(
            academic_level=AcademicLevel.PHD,
            proposal_type=AcademicProposalType.EDUCATION,
            topic=topic,
            purpose=purpose
        )

        res_bachelor = self.agent.generate_academic(bachelor_inp, provider="offline")
        res_phd = self.agent.generate_academic(phd_inp, provider="offline")

        # PhD should have scholarly/epistemological vocabulary
        self.assertIn("epistemological", res_phd.introduction_background.lower())
        # Bachelor's should have foundational/practical vocabulary
        self.assertIn("practical", res_bachelor.introduction_background.lower())
        self.assertNotEqual(res_bachelor.title, res_phd.title)

if __name__ == "__main__":
    unittest.main(verbosity=2)

