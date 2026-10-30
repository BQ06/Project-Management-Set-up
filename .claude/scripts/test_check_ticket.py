import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_ticket as ct

STANDARD = """## Show a loading message while a car is looked up

**Business context**

Customers enter their registration at the start of the quote journey and currently see nothing happen while we find their car. This leaves some of them unsure the page worked. Showing progress keeps them in the journey.

**Expected behaviour**

After a customer submits their registration, the button tells them their car is being found until the result appears.

**Acceptance criteria**

- [ ] The button text changes to "Finding your car" as soon as the registration is submitted
- [ ] If the lookup takes longer than expected, the message stays until a result or an error appears
- [ ] The customer must NOT be able to submit the registration twice while it is loading

**Dependencies**

- Blocked by: N/A
- Blocks: N/A
- External: N/A

**Potential impacts**

- Who is affected: Customers starting a quote
- Related areas of the product: Registration lookup step
- Rollback / risk: Customers would see the old button text, and the change can be reverted

**Open questions**

- None
"""

CREDS = """**Credentials**

- Base URL: https://api.staging.example.com/v1
- Bearer token: Authorization: Bearer fake-token-123
- Owner: ExamplePartner, via the vault note

"""

EPIC = """## 1. Context
Customers cannot see where their claim has got to, so they phone the agents.

Agents spend much of their day answering status calls.

## 2. Goals
- Customers can see their claim status
- Agents handle fewer status calls

## 4. User Stories
### Customer
*As a customer, I want to see my claim status, so that I do not need to phone.*

## 5. Requirements & Acceptance Criteria
### Claim status
**Acceptance Criteria**
* The customer sees the current status of each claim
* A customer with no claims sees a clear message saying so
* A customer must not see another customer's claims
"""


def problems(text, kind="standard", team="DEV"):
    return ct.check(text, kind, team)


DESIGN = """## [DESIGN] - Cookie banner and chat launcher

**Business context**

The live site has a cookie banner and a chat button, and the rebuilt site has neither. The build ticket cannot start without knowing what they look like. Visitors see the banner first, so it has to work on mobile.

**What to design**

The cookie banner and the chat button on mobile and desktop, including the open and closed chat states.

**Content and behaviour**

The banner offers necessary, analytics and marketing choices, with accept and reject given equal weight. The chat button stays closed until tapped.

**Design references**

- Existing design: https://example.com/wireframes (the Shared components board)
- Brand and shared components: N/A

**Acceptance criteria**

- [ ] The banner and the chat button are designed for mobile and desktop
- [ ] Edge case: the open chat state and the manage-choices view are designed
- [ ] Must NOT: the banner must not cover the page's main buttons on mobile

**Dependencies**

- Blocked by: N/A
- Blocks: the cookie consent build ticket
- External: N/A

**Potential impacts**

- Who is affected: Website visitors
- Related areas of the product: Every page
- Rollback / risk: Dev would build the vendor default styling

**Open questions**

- None
"""


class StandardTests(unittest.TestCase):
    def test_valid_draft_passes(self):
        self.assertEqual(problems(STANDARD), [])

    def test_missing_heading_fails(self):
        bad = STANDARD.replace("**Expected behaviour**", "**Behaviour**")
        self.assertTrue(any("Expected behaviour" in p for p in problems(bad)))

    def test_wrong_order_fails(self):
        a, b = "**Dependencies**", "**Potential impacts**"
        bad = STANDARD.replace(a, "@@").replace(b, a).replace("@@", b)
        self.assertTrue(any("order" in p.lower() for p in problems(bad)))

    def test_square_brackets_fail(self):
        bad = STANDARD.replace("Customers starting a quote", "[Customers starting a quote]")
        self.assertTrue(any("bracket" in p.lower() for p in problems(bad)))

    def test_markdown_link_is_allowed(self):
        ok = STANDARD.replace("Blocked by: N/A", "Blocked by: [DEV-1](https://linear.app/x)")
        self.assertEqual(problems(ok), [])

    def test_tbc_fails(self):
        bad = STANDARD.replace("- None", "- TBC")
        self.assertTrue(any("TBC" in p for p in problems(bad)))

    def test_update_log_fails(self):
        bad = STANDARD.replace("**Business context**\n", "**Business context**\n\nUpdate 21 Oct - now in Phase 1\n")
        self.assertTrue(any("update" in p.lower() for p in problems(bad)))

    def test_credentials_are_allowed_in_a_ticket(self):
        ok = STANDARD.replace("Rollback / risk: ", "Rollback / risk: Authorization: Bearer fake-token-123 ")
        self.assertEqual(problems(ok), [])

    def test_hex_key_is_allowed_in_a_ticket(self):
        ok = STANDARD.replace("Registration lookup step", "0123456789abcdef0123456789abcdef lookup step")
        self.assertEqual(problems(ok), [])

    def test_optional_credentials_section_passes(self):
        ok = STANDARD.replace("**Potential impacts**", CREDS + "**Potential impacts**")
        self.assertEqual(problems(ok), [])

    def test_credentials_section_in_wrong_place_fails(self):
        bad = STANDARD + "\n" + CREDS
        self.assertTrue(any("order" in p.lower() for p in problems(bad)))

    def test_empty_credentials_section_fails(self):
        bad = STANDARD.replace("**Potential impacts**", "**Credentials**\n\n**Potential impacts**")
        self.assertTrue(any("Credentials" in p for p in problems(bad)))

    def test_empty_label_fails(self):
        bad = STANDARD.replace("Blocks: N/A", "Blocks:")
        self.assertTrue(any("Blocks" in p for p in problems(bad)))

    def test_missing_must_not_fails(self):
        bad = STANDARD.replace("must NOT", "should not")
        self.assertTrue(any("Must NOT" in p for p in problems(bad)))

    def test_too_few_criteria_fails(self):
        bad = STANDARD.replace("- [ ] If the lookup takes longer than expected, the message stays until a result or an error appears\n", "")
        self.assertTrue(any("criteria" in p.lower() for p in problems(bad)))

    def test_open_question_must_be_question_or_none(self):
        bad = STANDARD.replace("- None", "- Chat with dev about this")
        self.assertTrue(any("Open questions" in p for p in problems(bad)))

    def test_open_question_with_question_mark_passes(self):
        ok = STANDARD.replace("- None", "- Which wording does design want?")
        self.assertEqual(problems(ok), [])

    def test_long_title_fails(self):
        bad = STANDARD.replace("Show a loading message while a car is looked up", "Show " + "a very long title " * 6)
        self.assertTrue(any("title" in p.lower() for p in problems(bad)))

    def test_non_verb_title_fails(self):
        bad = STANDARD.replace("Show a loading message", "The loading message")
        self.assertTrue(any("verb" in p.lower() for p in problems(bad)))

    def test_context_sentence_count(self):
        bad = STANDARD.replace("Showing progress keeps them in the journey.", "Showing progress keeps them in the journey. It also cuts calls. It reassures them. It looks better. It matches the brief. It helps sales.")
        self.assertTrue(any("sentences" in p.lower() for p in problems(bad)))

    def test_slightly_longer_context_passes_for_larger_change(self):
        ok = STANDARD.replace("Showing progress keeps them in the journey.", "Showing progress keeps them in the journey. It also cuts calls. It reassures them.")
        self.assertEqual(problems(ok), [])

    def test_one_sentence_context_passes(self):
        ok = STANDARD.replace(" This leaves some of them unsure the page worked. Showing progress keeps them in the journey.", "")
        self.assertEqual(problems(ok), [])

    def test_no_testing_criterion_needed(self):
        self.assertFalse(any("checked" in p.lower() for p in problems(STANDARD)))

    def test_removed_impact_lines_are_not_required(self):
        self.assertNotIn("Compliance", STANDARD)
        self.assertNotIn("Who needs telling", STANDARD)
        self.assertEqual(problems(STANDARD), [])

    def test_dated_progress_in_context_fails(self):
        bad = STANDARD.replace("Showing progress keeps them in the journey.", "This was agreed on 21 Oct.")
        self.assertTrue(any("dated" in p.lower() for p in problems(bad)))

    def test_relative_time_in_context_fails(self):
        bad = STANDARD.replace("Showing progress keeps them in the journey.", "We agreed this yesterday.")
        self.assertTrue(any("dated" in p.lower() for p in problems(bad)))

    def test_design_links_are_allowed(self):
        ok = STANDARD.replace("until the result appears.", "until the result appears. Design reference: https://example-site.netlify.app/ and [the hero option](https://example.pages.dev/index-v3?x=1).")
        self.assertEqual(problems(ok), [])

    def test_today_describing_current_state_is_allowed(self):
        ok = STANDARD.replace("currently see nothing happen", "today see nothing happen")
        self.assertEqual(problems(ok), [])

    def test_date_outside_context_is_allowed(self):
        ok = STANDARD.replace("Blocked by: N/A", "Blocked by: a decision due 30 Oct")
        self.assertEqual(problems(ok), [])

    def test_scope_statement_as_open_question_fails(self):
        bad = STANDARD.replace("- None", "- Not in this piece of work: cancelling with the partner. Does that stay out?")
        self.assertTrue(any("scope" in p.lower() for p in problems(bad)))

    def test_wrong_team_fails(self):
        self.assertTrue(any("team" in p.lower() for p in problems(STANDARD, team="LEA")))


class EpicTests(unittest.TestCase):
    def test_valid_epic_passes(self):
        self.assertEqual(problems(EPIC, "epic"), [])

    def test_missing_section_fails(self):
        bad = EPIC.replace("## 2. Goals", "## 2. Aims")
        self.assertEqual(problems(bad, "epic"), [])  # matched by number, not title
        bad = EPIC.replace("## 2. Goals\n- Customers can see their claim status\n- Agents handle fewer status calls\n\n", "")
        self.assertTrue(any("2" in p for p in problems(bad, "epic")))

    def test_story_must_match_form(self):
        bad = EPIC.replace("*As a customer, I want to see my claim status, so that I do not need to phone.*", "Customers want to see status.")
        self.assertTrue(any("story" in p.lower() for p in problems(bad, "epic")))

    def test_epic_dated_progress_in_context_fails(self):
        bad = EPIC.replace("Customers cannot see", "As agreed on 21 Oct, customers cannot see")
        self.assertTrue(any("dated" in p.lower() for p in problems(bad, "epic")))

    def test_epic_out_of_scope_section_fails(self):
        bad = EPIC + "\n## 6. Additional\n### Out of scope\n- Payments\n"
        self.assertTrue(any("section 6" in p.lower() for p in problems(bad, "epic")))

    def test_epic_reorganisation_proposal_fails(self):
        bad = EPIC + "\n## 6. Additional\n### Proposed child and parent changes\n- Move DEV-1 under this epic\n"
        self.assertTrue(any("section 6" in p.lower() for p in problems(bad, "epic")))

    def test_epic_future_scope_is_allowed(self):
        ok = EPIC + "\n## 6. Additional\n### Future scope (nice to have)\n- Email alerts when a claim changes status\n"
        self.assertEqual(problems(ok, "epic"), [])

    def test_epic_one_paragraph_context_passes(self):
        ok = EPIC.replace("\n\nAgents spend much of their day answering status calls.", "")
        self.assertEqual(problems(ok, "epic"), [])

    def test_epic_needs_an_exclusion(self):
        bad = EPIC.replace("* A customer must not see another customer's claims\n", "")
        self.assertTrue(any("exclusion" in p.lower() for p in problems(bad, "epic")))

    def test_epic_open_questions_must_be_questions(self):
        bad = EPIC + "\n## 6. Additional\n### Open questions\n- Talk to dev\n"
        self.assertTrue(any("Open questions" in p for p in problems(bad, "epic")))

    def test_epic_open_questions_as_questions_pass(self):
        ok = EPIC + "\n## 6. Additional\n### Open questions\n- Which epic owns the content tickets?\n"
        self.assertEqual(problems(ok, "epic"), [])

    def test_optional_sections_allowed(self):
        ok = EPIC.replace("## 4. User Stories", "## 3. Roles / definitions\n| Role | Can do |\n|---|---|\n| Customer | View claims |\n\n## 4. User Stories")
        self.assertEqual(problems(ok, "epic"), [])


class DesignTests(unittest.TestCase):
    def test_valid_design_passes(self):
        self.assertEqual(problems(DESIGN, "design", "DES"), [])

    def test_design_needs_design_team(self):
        self.assertTrue(any("DES" in p for p in problems(DESIGN, "design", "DEV")))

    def test_design_title_needs_tag(self):
        bad = DESIGN.replace("## [DESIGN] - Cookie banner", "## Design the cookie banner", 1)
        self.assertTrue(any("[DESIGN]" in p for p in problems(bad, "design", "DES")))

    def test_design_missing_section_fails(self):
        bad = DESIGN.replace("**What to design**\n\nThe cookie banner and the chat button on mobile and desktop, including the open and closed chat states.\n\n", "")
        self.assertTrue(any("missing heading: What to design" in p for p in problems(bad, "design", "DES")))

    def test_design_references_need_a_value(self):
        bad = DESIGN.replace("- Brand and shared components: N/A", "- Brand and shared components:")
        self.assertTrue(any("Design references" in p for p in problems(bad, "design", "DES")))

    def test_design_needs_must_not(self):
        bad = DESIGN.replace("Must NOT: the banner must not cover", "The banner should not cover")
        self.assertTrue(any("Must NOT" in p for p in problems(bad, "design", "DES")))

    def test_design_placeholder_brackets_still_fail(self):
        bad = DESIGN.replace("The live site has", "[Add the context] The live site has", 1)
        self.assertTrue(any("square brackets" in p for p in problems(bad, "design", "DES")))

    def test_design_open_question_must_be_a_question(self):
        bad = DESIGN.replace("**Open questions**\n\n- None", "**Open questions**\n\n- Talk to dev")
        self.assertTrue(any("Open questions" in p for p in problems(bad, "design", "DES")))

    def test_standard_ticket_may_still_be_dev_or_des(self):
        self.assertEqual(problems(STANDARD, "standard", "DES"), [])


class TicketIdTests(unittest.TestCase):
    def test_lists_each_id_once_in_order(self):
        text = "Related: DEV-2257 and DES-61. See DEV-2257 again, plus LEA-4344."
        self.assertEqual(ct.ticket_ids(text), ["DEV-2257", "DES-61", "LEA-4344"])

    def test_no_ids_gives_empty_list(self):
        self.assertEqual(ct.ticket_ids(STANDARD), [])


class ConfigTests(unittest.TestCase):
    def test_defaults_are_dev_and_des(self):
        cfg = ct.load_config("/nonexistent/pm-config.json")
        self.assertEqual((cfg["build_team"], cfg["design_team"], cfg["design_tag"]), ("DEV", "DES", "[DESIGN] - "))

    def test_config_file_overrides_the_team_keys(self):
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"build_team": "ENG", "design_team": "UX", "ignored": 1}, fh)
        cfg = ct.load_config(fh.name)
        self.assertEqual((cfg["build_team"], cfg["design_team"], cfg["design_tag"]), ("ENG", "UX", "[DESIGN] - "))
        self.assertNotIn("ignored", cfg)

    def test_error_messages_use_the_configured_keys(self):
        old = ct.TEAMS
        ct.TEAMS = ("ENG", "UX")
        try:
            msgs = ct.common_checks("## Add a thing", "XYZ")
        finally:
            ct.TEAMS = old
        self.assertTrue(any("ENG" in m and "UX" in m for m in msgs))


if __name__ == "__main__":
    unittest.main()
